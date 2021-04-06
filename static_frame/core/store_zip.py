import typing as tp
import zipfile
import pickle
from io import StringIO
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor

from static_frame.core.frame import Frame
from static_frame.core.store import Store
from static_frame.core.store import store_coherent_non_write
from static_frame.core.store import store_coherent_write
from static_frame.core.store import StoreConfigMap
from static_frame.core.store import StoreConfig
from static_frame.core.store import StoreConfigHE
from static_frame.core.store import StoreConfigMapInitializer
from static_frame.core.util import AnyCallable
from static_frame.core.container_util import container_to_exporter_attr


# class FrameExporter(tp.Protocol):
#     def __call__(self, frame: Frame, *args: tp.Any, **kwargs: tp.Any) -> tp.Any:
#         raise NotImplementedError

FrameExporter = AnyCallable # Protocol not supported yet...

FrameConstructor = tp.Callable[[tp.Any], Frame]


class DeferredFrameInitPayload(tp.NamedTuple):
    '''
    Defines the necessary objects to construct a frame. Used for multiprocessing.
    '''
    src: bytes
    name: tp.Hashable
    config: StoreConfigHE
    constructor: FrameConstructor


class BytesConstructionPayload(tp.NamedTuple):
    '''
    Defines the necessary objects to construct writeable frame bytes. Used for multiprocessing.
    '''
    name: tp.Hashable
    config: StoreConfigHE
    frame: Frame
    exporter: FrameExporter


LabelAndBytesT = tp.Tuple[tp.Hashable, tp.Union[str, bytes]]

class _StoreZip(Store):

    _EXT: tp.FrozenSet[str] = frozenset(('.zip',))
    _EXT_CONTAINED: str = ''
    _EXPORTER: AnyCallable

    @classmethod
    def _container_type_to_constructor(cls, container_type: tp.Type[Frame]) -> FrameConstructor:
        raise NotImplementedError

    @classmethod
    def _build_frame(cls,
            src: bytes,
            name: tp.Hashable,
            config: tp.Union[StoreConfigHE, StoreConfig],
            constructor: FrameConstructor,
            ) -> Frame:
        raise NotImplementedError

    @classmethod
    def _build_frame_from_payload(cls, payload: DeferredFrameInitPayload) -> Frame:
        return cls._build_frame(
                src=payload.src,
                name=payload.name,
                config=payload.config,
                constructor=payload.constructor,
        )

    @store_coherent_non_write
    def labels(self, *,
            config: StoreConfigMapInitializer = None,
            strip_ext: bool = True,
            ) -> tp.Iterator[tp.Hashable]:

        config_map = StoreConfigMap.from_initializer(config)

        with zipfile.ZipFile(self._fp) as zf:
            for name in zf.namelist():
                if strip_ext:
                    name = name.replace(self._EXT_CONTAINED, '')
                # always use default decoder
                yield config_map.default.label_decode(name)

    @store_coherent_non_write
    def read_many(self,
            labels: tp.Iterable[tp.Hashable],
            *,
            config: StoreConfigMapInitializer = None,
            container_type: tp.Type[Frame] = Frame,
        ) -> tp.Iterator[Frame]:

        config_map = StoreConfigMap.from_initializer(config)
        multiprocess: bool = config_map.default.read_max_workers is not None
        constructor: FrameConstructor = self._container_type_to_constructor(container_type)

        def gen() -> tp.Iterable[tp.Union[DeferredFrameInitPayload, Frame]]:
            with zipfile.ZipFile(self._fp) as zf:
                for label in labels:
                    c: StoreConfig = config_map[label]

                    label_encoded: str = config_map.default.label_encode(label)
                    src: bytes = zf.read(label_encoded + self._EXT_CONTAINED)

                    if multiprocess:
                        yield DeferredFrameInitPayload( # pylint: disable=no-value-for-parameter
                                src=src,
                                name=label,
                                config=c.to_store_config_he(),
                                constructor=constructor,
                        )
                    else:
                        yield self._build_frame(
                                src=src,
                                name=label,
                                config=c,
                                constructor=constructor,
                        )

        if multiprocess:
            chunksize = config_map.default.read_chunksize

            with ProcessPoolExecutor(max_workers=config_map.default.read_max_workers) as executor:
                yield from executor.map(self._build_frame_from_payload, gen(), chunksize=chunksize)
        else:
            yield from gen() # type: ignore

    # --------------------------------------------------------------------------

    @staticmethod
    def _payload_to_bytes(payload: BytesConstructionPayload) -> LabelAndBytesT:
        raise NotImplementedError

    @classmethod
    def _serialize_multiprocess_write(cls,
            items: tp.Iterable[BytesConstructionPayload],
            chunksize: int,
            max_workers:int,
        ) -> tp.Iterable[LabelAndBytesT]:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            yield from executor.map(cls._payload_to_bytes, items, chunksize=chunksize)

    @store_coherent_write
    def write(self,
            items: tp.Iterable[tp.Tuple[tp.Hashable, Frame]],
            *,
            config: StoreConfigMapInitializer = None
        ) -> None:
        config_map = StoreConfigMap.from_initializer(config)
        multiprocess = (config_map.default.write_max_workers is not None and
                        config_map.default.write_max_workers > 1)

        def gen() -> tp.Iterable[BytesConstructionPayload]:
            for label, frame in items:
                yield BytesConstructionPayload( # pylint: disable=no-value-for-parameter
                        name=label,
                        config=config_map[label].to_store_config_he(),
                        frame=frame,
                        exporter=self.__class__._EXPORTER,
                )

        if multiprocess:
            label_and_bytes: tp.Iterable[LabelAndBytesT] = self._serialize_multiprocess_write(
                    gen(),
                    chunksize=config_map.default.write_chunksize,
                    max_workers=tp.cast(int, config_map.default.write_max_workers),
            )
        else:
            label_and_bytes = (self._payload_to_bytes(x) for x in gen())

        with zipfile.ZipFile(self._fp, 'w', zipfile.ZIP_DEFLATED) as zf:
            for label, frame_bytes in label_and_bytes:
                label_encoded = config_map.default.label_encode(label)

                # this will write it without a container
                zf.writestr(label_encoded + self._EXT_CONTAINED, frame_bytes)


class _StoreZipDelimited(_StoreZip):
    # store attribute of passed-in container_type to use for construction
    _EXPORTER_ATTR: str
    _CONSTRUCTOR_ATTR: str

    @classmethod
    def _container_type_to_constructor(cls, container_type: tp.Type[Frame]) -> FrameConstructor:
        return getattr(container_type, cls._CONSTRUCTOR_ATTR) # type: ignore

    @classmethod
    def _build_frame(cls,
            src: bytes,
            name: tp.Hashable,
            config: tp.Union[StoreConfigHE, StoreConfig],
            constructor: FrameConstructor,
        ) -> Frame:
        return constructor( # type: ignore
            StringIO(src.decode()),
            index_depth=config.index_depth,
            columns_depth=config.columns_depth,
            dtypes=config.dtypes,
            name=name,
            consolidate_blocks=config.consolidate_blocks,
        )

    @staticmethod
    def _payload_to_bytes(payload: BytesConstructionPayload) -> LabelAndBytesT:
        c = payload.config

        dst = StringIO()
        # call from class to explicitly pass self as frame
        payload.exporter(payload.frame,
                dst,
                include_index=c.include_index,
                include_index_name=c.include_index_name,
                include_columns=c.include_columns,
                include_columns_name=c.include_columns_name
        )
        return payload.name, dst.getvalue()


class StoreZipTSV(_StoreZipDelimited):
    '''
    Store of TSV files contained within a ZIP file.
    '''
    _EXT_CONTAINED = '.txt'
    _EXPORTER = Frame.to_tsv
    _CONSTRUCTOR_ATTR = Frame.from_tsv.__name__


class StoreZipCSV(_StoreZipDelimited):
    '''
    Store of CSV files contained within a ZIP file.
    '''
    _EXT_CONTAINED = '.csv'
    _EXPORTER = Frame.to_csv
    _CONSTRUCTOR_ATTR = Frame.from_csv.__name__


#-------------------------------------------------------------------------------

class StoreZipPickle(_StoreZip):
    '''A zip of pickles, permitting incremental loading of Frames.
    '''
    _EXT_CONTAINED = '.pickle'
    _EXPORTER = pickle.dumps

    @classmethod
    def _container_type_to_constructor(cls, container_type: tp.Type[Frame]) -> FrameConstructor:
        return pickle.loads

    @classmethod
    def _build_frame(cls,
            src: bytes,
            name: tp.Hashable,
            config: tp.Union[StoreConfigHE, StoreConfig],
            constructor: FrameConstructor,
        ) -> Frame:
        return constructor(src)

    @store_coherent_non_write
    def read_many(self,
            labels: tp.Iterable[tp.Hashable],
            *,
            config: StoreConfigMapInitializer = None,
            container_type: tp.Type[Frame] = Frame,
            ) -> tp.Iterator[Frame]:

        exporter = container_to_exporter_attr(container_type)

        for frame in _StoreZip.read_many(self,
                labels,
                config=config,
                container_type=container_type,
                ):
            if frame.__class__ is container_type:
                yield frame
            else:
                yield getattr(frame, exporter)()

    @staticmethod
    def _payload_to_bytes(payload: BytesConstructionPayload) -> LabelAndBytesT:
        return payload.name, payload.exporter(payload.frame)


#-------------------------------------------------------------------------------

class StoreZipParquet(_StoreZip):
    '''A zip of parquet files, permitting incremental loading of Frames.
    '''
    _EXT_CONTAINED = '.parquet'
    _EXPORTER = Frame.to_parquet

    @classmethod
    def _container_type_to_constructor(cls, container_type: tp.Type[Frame]) -> FrameConstructor:
        return container_type.from_parquet

    @classmethod
    def _build_frame(cls,
            src: bytes,
            name: tp.Hashable,
            config: tp.Union[StoreConfigHE, StoreConfig],
            constructor: FrameConstructor,
        ) -> Frame:
        return constructor( # type: ignore
            BytesIO(src),
            index_depth=config.index_depth,
            index_name_depth_level=config.index_name_depth_level,
            columns_depth=config.columns_depth,
            columns_name_depth_level=config.columns_name_depth_level,
            columns_select=config.columns_select,
            dtypes=config.dtypes,
            name=name,
            consolidate_blocks=config.consolidate_blocks,
        )

    @staticmethod
    def _payload_to_bytes(payload: BytesConstructionPayload) -> LabelAndBytesT:
        c = payload.config

        dst = BytesIO()
        payload.exporter(payload.frame,
                dst,
                include_index=c.include_index,
                include_index_name=c.include_index_name,
                include_columns=c.include_columns,
                include_columns_name=c.include_columns_name,
                )
        return payload.name, dst.getvalue()
