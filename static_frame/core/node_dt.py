
import typing as tp
import numpy as np

from static_frame.core.util import DT64_YEAR
from static_frame.core.util import DT64_MONTH
from static_frame.core.util import DT64_DAY
from static_frame.core.util import DTYPE_INT_DEFAULT
from static_frame.core.util import DTYPE_OBJECT
from static_frame.core.util import DTYPE_DATETIME_KIND
from static_frame.core.util import EMPTY_TUPLE

from static_frame.core.util import array_from_element_attr
from static_frame.core.util import array_from_element_method


if tp.TYPE_CHECKING:

    from static_frame.core.frame import Frame  #pylint: disable = W0611 #pragma: no cover
    from static_frame.core.index import Index  #pylint: disable = W0611 #pragma: no cover
    from static_frame.core.index_hierarchy import IndexHierarchy  #pylint: disable = W0611 #pragma: no cover
    from static_frame.core.series import Series  #pylint: disable = W0611 #pragma: no cover
    from static_frame.core.type_blocks import TypeBlocks  #pylint: disable = W0611 #pragma: no cover

# only ContainerOperand subclasses
TContainer = tp.TypeVar('TContainer', 'Index', 'IndexHierarchy', 'Series', 'Frame', 'TypeBlocks')

BlocksType = tp.Iterable[np.ndarray]
ToContainerType = tp.Callable[[tp.Iterator[np.ndarray]], TContainer]

#https://docs.python.org/3/library/datetime.html

class InterfaceDatetime(tp.Generic[TContainer]):

    __slots__ = (
        '_blocks', # function that returns iterable of arrays
        '_blocks_to_container', # partialed function that will return a new container
        )

    DT64_EXCLUDE_YEAR = (DT64_YEAR,)
    DT64_EXCLUDE_YEAR_MONTH = (DT64_YEAR, DT64_MONTH)

    def __init__(self,
            blocks: BlocksType,
            blocks_to_container: ToContainerType[TContainer]
            ) -> None:
        self._blocks: BlocksType = blocks
        self._blocks_to_container: ToContainerType[TContainer] = blocks_to_container

    @staticmethod
    def _validate_dtype(
            dtype: np.dtype,
            exclude: tp.Iterable[np.dtype] = EMPTY_TUPLE,
            ) -> None:
        if ((dtype.kind == DTYPE_DATETIME_KIND
                or dtype == DTYPE_OBJECT)
                and dtype not in exclude
                ):
            return
        raise RuntimeError(f'invalid dtype ({dtype}) for date operation')

    #---------------------------------------------------------------------------

    @property
    def year(self) -> TContainer:
        'Return the year of each element.'

        def blocks() -> tp.Iterator[np.ndarray]:
            for block in self._blocks:
                self._validate_dtype(block.dtype)

                if block.dtype.kind == DTYPE_DATETIME_KIND:
                    array = block.astype(DT64_YEAR).astype(int) + 1970
                    array.flags.writeable = False
                else: # must be object type
                    array = array_from_element_attr(
                            array=block,
                            attr_name='year',
                            dtype=DTYPE_INT_DEFAULT)
                yield array

        return self._blocks_to_container(blocks())

    @property
    def month(self) -> TContainer:
        '''
        Return the month of each element, between 1 and 12 inclusive.
        '''

        def blocks() -> tp.Iterator[np.ndarray]:
            for block in self._blocks:
                self._validate_dtype(block.dtype, exclude=self.DT64_EXCLUDE_YEAR)

                if block.dtype.kind == DTYPE_DATETIME_KIND:
                    array = block.astype(DT64_MONTH).astype(int) % 12 + 1
                    array.flags.writeable = False
                else: # must be object type
                    array = array_from_element_attr(
                            array=block,
                            attr_name='month',
                            dtype=DTYPE_INT_DEFAULT)
                yield array

        return self._blocks_to_container(blocks())

    @property
    def day(self) -> TContainer:
        '''
        Return the day of each element, between 1 and the number of days in the given month of the given year.
        '''

        def blocks() -> tp.Iterator[np.ndarray]:
            for block in self._blocks:
                self._validate_dtype(block.dtype, exclude=self.DT64_EXCLUDE_YEAR_MONTH)

                if block.dtype.kind == DTYPE_DATETIME_KIND:
                    if block.dtype != DT64_DAY:
                        block = block.astype(DT64_DAY)
                    array = block - block.astype(DT64_MONTH) + 1
                    array.flags.writeable = False
                else: # must be object type
                    array = array_from_element_attr(
                            array=block,
                            attr_name='day',
                            dtype=DTYPE_INT_DEFAULT)

                yield array

        return self._blocks_to_container(blocks())


    #---------------------------------------------------------------------------

    def weekday(self) -> TContainer:

        def blocks() -> tp.Iterator[np.ndarray]:
            for block in self._blocks:
                self._validate_dtype(block.dtype, exclude=self.DT64_EXCLUDE_YEAR_MONTH)

                if block.dtype.kind == DTYPE_DATETIME_KIND:
                    if block.dtype != DT64_DAY: # go to day first, then object
                        block = block.astype(DT64_DAY)
                    block = block.astype(DTYPE_OBJECT)
                # all object arrays by this point

                # returns an immutable array
                array = array_from_element_method(
                        array=block,
                        method_name='weekday',
                        args=EMPTY_TUPLE,
                        dtype=DTYPE_INT_DEFAULT
                        )
                yield array

        return self._blocks_to_container(blocks())