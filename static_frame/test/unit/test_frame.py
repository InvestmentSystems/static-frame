from itertools import zip_longest
from itertools import combinations
import unittest
from collections import OrderedDict
import itertools as it
from collections import namedtuple
from io import StringIO
import string
import hashlib
import pickle
import sys

import numpy as np
import pytest
import typing as tp

import static_frame as sf

# assuming located in the same directory
from static_frame import Index
from static_frame import IndexGO
from static_frame import IndexHierarchy
from static_frame import IndexHierarchyGO
from static_frame import Series
from static_frame import Frame
from static_frame import FrameGO
from static_frame import TypeBlocks
from static_frame import Display
from static_frame import mloc
from static_frame import ILoc
from static_frame import HLoc
from static_frame import DisplayConfig

from static_frame.test.test_case import TestCase
from static_frame.test.test_case import skip_win


nan = np.nan


class TestUnit(TestCase):


    def test_frame_init_a(self):

        f = Frame.from_dict(OrderedDict([('a', (1,2)), ('b', (3,4))]), index=('x', 'y'))
        self.assertEqual(f.to_pairs(0),
                (('a', (('x', 1), ('y', 2))), ('b', (('x', 3), ('y', 4))))
                )

        f = Frame.from_dict(OrderedDict([('b', (3,4)), ('a', (1,2))]), index=('x', 'y'))
        self.assertEqual(f.to_pairs(0),
                (('b', (('x', 3), ('y', 4))), ('a', (('x', 1), ('y', 2)))))


    def test_frame_init_b(self):
        # test unusual instantiation cases

        # create a frame with a single value
        f1 = Frame(1, index=(1,2), columns=(3,4,5))
        self.assertEqual(f1.to_pairs(0),
                ((3, ((1, 1), (2, 1))), (4, ((1, 1), (2, 1))), (5, ((1, 1), (2, 1))))
                )

        # with columns not defined, we create a DF with just an index
        f2 = FrameGO(index=(1,2))
        f2['a'] = (-1, -1)
        self.assertEqual(f2.to_pairs(0),
                (('a', ((1, -1), (2, -1))),)
                )

        # with columns and index defined, we fill the value even if None
        f3 = Frame(None, index=(1,2), columns=(3,4,5))
        self.assertEqual(f3.to_pairs(0),
                ((3, ((1, None), (2, None))), (4, ((1, None), (2, None))), (5, ((1, None), (2, None)))))

        # auto populated index/columns based on shape
        f4 = Frame([[1,2], [3,4], [5,6]])
        self.assertEqual(f4.to_pairs(0),
                ((0, ((0, 1), (1, 3), (2, 5))), (1, ((0, 2), (1, 4), (2, 6))))
                )
        self.assertTrue(f4._index._loc_is_iloc)
        self.assertTrue(f4._columns._loc_is_iloc)


    def test_frame_init_c(self):
        f = sf.FrameGO.from_dict(dict(color=('black',)))
        s = f['color']
        self.assertEqual(s.to_pairs(),
                ((0, 'black'),))

    def test_frame_init_d(self):
        a1 = np.array([[1, 2, 3], [4, 5, 6]])

        f = sf.Frame(a1, own_data=True)
        self.assertEqual(mloc(a1), f.mloc[0])

    def test_frame_init_e(self):
        a1 = np.array([1, 2, 3])
        a2 = np.array([4, 5, 6])

        f = sf.Frame.from_dict(dict(a=a1, b=a2))

    def test_frame_init_f(self):
        a1 = np.array([1, 2, 3])
        a2 = np.array([4, 5, 6])

        f = sf.Frame.from_dict(dict(a=a1, b=a2))

        self.assertEqual(f.to_pairs(0),
            (('a', ((0, 1), (1, 2), (2, 3))), ('b', ((0, 4), (1, 5), (2, 6))))
            )

    def test_frame_init_g(self):

        f1 = sf.Frame(index=tuple('abc'))
        self.assertEqual(f1.shape, (3, 0))

        f2 = sf.Frame(columns=tuple('abc'))
        self.assertEqual(f2.shape, (0, 3))

        f3 = sf.Frame()
        self.assertEqual(f3.shape, (0, 0))

    def test_frame_init_h(self):

        f1 = sf.Frame(index=tuple('abc'), columns=())
        self.assertEqual(f1.shape, (3, 0))

        f2 = sf.Frame(columns=tuple('abc'), index=())
        self.assertEqual(f2.shape, (0, 3))

        f3 = sf.Frame(columns=(), index=())
        self.assertEqual(f3.shape, (0, 0))


    def test_frame_init_i(self):

        f1 = sf.FrameGO(index=tuple('abc'))
        f1['x'] = (3, 4, 5)
        f1['y'] = Series(dict(b=10, c=11, a=12))

        self.assertEqual(f1.to_pairs(0),
            (('x', (('a', 3), ('b', 4), ('c', 5))), ('y', (('a', 12), ('b', 10), ('c', 11)))))

    def test_frame_init_j(self):
        f1 = sf.Frame('q', index=tuple('ab'), columns=tuple('xy'))
        self.assertEqual(f1.to_pairs(0),
            (('x', (('a', 'q'), ('b', 'q'))), ('y', (('a', 'q'), ('b', 'q'))))
            )

    def test_frame_init_k(self):
        # check that we got autoincrement indices if no col/index provided
        f1 = Frame([[0, 1], [2, 3]])
        self.assertEqual(f1.to_pairs(0), ((0, ((0, 0), (1, 2))), (1, ((0, 1), (1, 3)))))

    def test_frame_init_m(self):
        # cannot create a single element filled Frame specifying a shape (with index and columns) but not specifying a data value
        with self.assertRaises(RuntimeError):
            f1 = Frame(index=(3,4,5), columns=list('abv'))

    def test_frame_init_n(self):
        # cannot supply a single value to unfillabe sized Frame

        with self.assertRaises(RuntimeError):
            f1 = Frame(None, index=(3,4,5), columns=())

    def test_frame_init_o(self):
        f1 = Frame()
        self.assertEqual(f1.shape, (0, 0))


    def test_frame_init_p(self):

        # raise when a data values ir provided but an axis is size zero

        with self.assertRaises(RuntimeError):
            f1 = sf.Frame('x', index=(1,2,3), columns=iter(()))

        with self.assertRaises(RuntimeError):
            f1 = sf.Frame(None, index=(1,2,3), columns=iter(()))


    def test_frame_init_q(self):

        f1 = sf.Frame(index=(1,2,3), columns=iter(()))
        self.assertEqual(f1.shape, (3, 0))
        self.assertEqual(f1.to_pairs(0), ())


    def test_frame_init_r(self):

        f1 = sf.Frame(index=(), columns=iter(range(3)))

        self.assertEqual(f1.shape, (0, 3))
        self.assertEqual(f1.to_pairs(0),
                ((0, ()), (1, ()), (2, ())))

        with self.assertRaises(RuntimeError):
            # cannot create an unfillable array with a data value
            f1 = sf.Frame('x', index=(), columns=iter(range(3)))


    def test_frame_init_iter(self):

        f1 = Frame(None, index=iter(range(3)), columns=("A",))
        self.assertEqual(
            f1.to_pairs(0),
            (('A', ((0, None), (1, None), (2, None))),)
        )

        f2 = Frame(None, index=("A",), columns=iter(range(3)))
        self.assertEqual(
            f2.to_pairs(0),
            ((0, (('A', None),)), (1, (('A', None),)), (2, (('A', None),)))
        )

    def test_frame_values_a(self):
        f = sf.Frame([[3]])
        self.assertEqual(f.values.tolist(), [[3]])


    def test_frame_values_b(self):
        f = sf.Frame(np.array([[3, 2, 1]]))
        self.assertEqual(f.values.tolist(), [[3, 2, 1]])

    def test_frame_values_c(self):
        f = sf.Frame(np.array([[3], [2], [1]]))
        self.assertEqual(f.values.tolist(), [[3], [2], [1]])


    def test_frame_from_pairs_a(self):

        frame = Frame.from_items(sorted(dict(a=[3,4,5], b=[6,3,2]).items()))
        self.assertEqual(
            list((k, list(v.items())) for k, v in frame.items()),
            [('a', [(0, 3), (1, 4), (2, 5)]), ('b', [(0, 6), (1, 3), (2, 2)])])

        frame = Frame.from_items(OrderedDict((('b', [6,3,2]), ('a', [3,4,5]))).items())
        self.assertEqual(list((k, list(v.items())) for k, v in frame.items()),
            [('b', [(0, 6), (1, 3), (2, 2)]), ('a', [(0, 3), (1, 4), (2, 5)])])


    def test_frame_from_pandas_a(self):
        import pandas as pd

        df = pd.DataFrame(dict(a=(1,2), b=(3,4)))
        df.name = 'foo'

        f = Frame.from_pandas(df)
        self.assertEqual(f.to_pairs(0),
                (('a', ((0, 1), (1, 2))), ('b', ((0, 3), (1, 4))))
                )


    def test_frame_from_pandas_b(self):
        import pandas as pd

        df = pd.DataFrame(dict(a=(1,2), b=(False, True)), index=('x', 'y'))

        f = Frame.from_pandas(df)

        self.assertEqual(f.to_pairs(0),
                (('a', (('x', 1), ('y', 2))), ('b', (('x', False), ('y', True))))
                )

        with self.assertRaises(Exception):
            f['c'] = 0


    def test_frame_from_pandas_c(self):
        import pandas as pd

        df = pd.DataFrame(dict(a=(1,2), b=(False, True)), index=('x', 'y'))

        f = FrameGO.from_pandas(df)
        f['c'] = -1

        self.assertEqual(f.to_pairs(0),
                (('a', (('x', 1), ('y', 2))), ('b', (('x', False), ('y', True))), ('c', (('x', -1), ('y', -1)))))

    def test_frame_from_pandas_a(self):
        import pandas as pd

        df = pd.DataFrame(dict(a=(1,2), b=(3,4)))
        df.name = 'foo'

        f = Frame.from_pandas(df, own_data=True)
        self.assertEqual(f.to_pairs(0),
                (('a', ((0, 1), (1, 2))), ('b', ((0, 3), (1, 4))))
                )


    def test_frame_to_pandas_a(self):
        records = (
                (1, 2, 'a', False),
                (30, 34, 'b', True),
                (54, 95, 'c', False),
                (65, 73, 'd', True),
                )
        columns = IndexHierarchy.from_product(('a', 'b'), (1, 2))
        index = IndexHierarchy.from_product((100, 200), (True, False))
        f1 = Frame.from_records(records,
                columns=columns,
                index=index)

        df = f1.to_pandas()

        self.assertEqual(df.index.values.tolist(),
            [(100, True), (100, False), (200, True), (200, False)]
            )

        self.assertEqual(df.columns.values.tolist(),
            [('a', 1), ('a', 2), ('b', 1), ('b', 2)]
            )

        self.assertEqual(df.values.tolist(),
            [[1, 2, 'a', False], [30, 34, 'b', True], [54, 95, 'c', False], [65, 73, 'd', True]])


    def test_frame_to_pandas_b(self):
        f1 = sf.Frame.from_records(
                [dict(a=1,b=1), dict(a=2,b=3), dict(a=1,b=1), dict(a=2,b=3)], index=sf.IndexHierarchy.from_labels(
                [(1,'dd',0),(1,'b',0),(2,'cc',0),(2,'ee',0)]))
        df = f1.loc[sf.HLoc[(1,'dd')]].to_pandas()

        self.assertEqual(df.index.values.tolist(),
                [(1, 'dd', 0)])
        self.assertEqual(df.values.tolist(),
                [[1, 1]]
                )

    def test_frame_getitem_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        f2 = f1['r':]
        self.assertEqual(f2.columns.values.tolist(), ['r', 's', 't'])
        self.assertTrue((f2.index == f1.index).all())
        self.assertEqual(mloc(f2.index.values), mloc(f1.index.values))

    def test_frame_getitem_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # using an Index object for selection
        self.assertEqual(
                f1[f1.columns.loc['r':]].to_pairs(0),
                (('r', (('x', 'a'), ('y', 'b'))), ('s', (('x', False), ('y', True))), ('t', (('x', True), ('y', False))))
                )


    def test_frame_length_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(len(f1), 2)



    def test_frame_iloc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual((f1.iloc[0].values == f1.loc['x'].values).all(), True)
        self.assertEqual((f1.iloc[1].values == f1.loc['y'].values).all(), True)


    def test_frame_iloc_b(self):
        # this is example dervied from this question:
        # https://stackoverflow.com/questions/22927181/selecting-specific-rows-and-columns-from-numpy-array

        a = np.arange(20).reshape((5,4))
        f1 = FrameGO(a)
        a[1,1] = 3000 # ensure we made a copy
        self.assertEqual(f1.loc[[0,1,3], [0,2]].values.tolist(),
                [[0, 2], [4, 6], [12, 14]])
        self.assertEqual(f1.iloc[[0,1,3], [0,2]].values.tolist(),
                [[0, 2], [4, 6], [12, 14]])

        self.assertTrue(f1._index._loc_is_iloc)
        self.assertTrue(f1._columns._loc_is_iloc)

        f1[4] = list(range(5))
        self.assertTrue(f1._columns._loc_is_iloc)

        f1[20] = list(range(5))
        self.assertFalse(f1._columns._loc_is_iloc)

        self.assertEqual(f1.values.tolist(),
                [[0, 1, 2, 3, 0, 0],
                [4, 5, 6, 7, 1, 1],
                [8, 9, 10, 11, 2, 2],
                [12, 13, 14, 15, 3, 3],
                [16, 17, 18, 19, 4, 4]])


    def test_frame_iter_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual((f1.keys() == f1.columns).all(), True)
        self.assertEqual([x for x in f1.columns], ['p', 'q', 'r', 's', 't'])
        self.assertEqual([x for x in f1], ['p', 'q', 'r', 's', 't'])




    def test_frame_iter_array_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(
                next(iter(f1.iter_array(axis=0))).tolist(),
                [1, 30])

        self.assertEqual(
                next(iter(f1.iter_array(axis=1))).tolist(),
                [1, 2, 'a', False, True])


    def test_frame_iter_array_b(self):

        arrays = list(np.random.rand(1000) for _ in range(100))
        f1 = Frame.from_items(
                zip(range(100), arrays)
                )

        # iter columns
        post = f1.iter_array(0).apply_pool(np.sum, max_workers=4, use_threads=True)
        self.assertEqual(post.shape, (100,))
        self.assertAlmostEqual(f1.sum().sum(), post.sum())

        post = f1.iter_array(0).apply_pool(np.sum, max_workers=4, use_threads=False)
        self.assertEqual(post.shape, (100,))
        self.assertAlmostEqual(f1.sum().sum(), post.sum())

    def test_frame_iter_array_c(self):
        arrays = []
        for _ in range(8):
            arrays.append(list(range(8)))
        f1 = Frame.from_items(
                zip(range(8), arrays)
                )

        func = {x: chr(x+65) for x in range(8)}
        # iter columns
        post = f1.iter_element().apply_pool(func, max_workers=4, use_threads=True)

        self.assertEqual(post.to_pairs(0),
                ((0, ((0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'H'))), (1, ((0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'H'))), (2, ((0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'H'))), (3, ((0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'H'))), (4, ((0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'H'))), (5, ((0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'H'))), (6, ((0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'H'))), (7, ((0, 'A'), (1, 'B'), (2, 'C'), (3, 'D'), (4, 'E'), (5, 'F'), (6, 'G'), (7, 'H'))))
                )

    def test_frame_iter_array_d(self):
        arrays = []
        for _ in range(8):
            arrays.append(list(range(8)))
        f1 = Frame.from_items(
                zip(range(8), arrays)
                )

        # when called with a pool, values are gien the func as a single argument, which for an element iteration is a tuple of coord, value
        func = lambda arg: arg[0][1]
        # iter columns
        post = f1.iter_element_items().apply_pool(func, max_workers=4, use_threads=True)

        self.assertEqual(post.to_pairs(0),
                ((0, ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0))), (1, ((0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1))), (2, ((0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2))), (3, ((0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3))), (4, ((0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4))), (5, ((0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5))), (6, ((0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6))), (7, ((0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7))))
                )



    def test_frame_setitem_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        f1['a'] = (False, True)
        self.assertEqual(f1['a'].values.tolist(), [False, True])

        # test index alginment
        f1['b'] = Series((3,2,5), index=('y', 'x', 'g'))
        self.assertEqual(f1['b'].values.tolist(), [2, 3])

        f1['c'] = Series((300,200,500), index=('y', 'j', 'k'))
        self.assertAlmostEqualItems(f1['c'].items(), [('x', nan), ('y', 300)])


    def test_frame_setitem_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        f1['u'] = 0

        self.assertEqual(f1.loc['x'].values.tolist(),
                [1, 2, 'a', False, True, 0])

        with self.assertRaises(Exception):
            f1['w'] = [[1,2], [4,5]]


    def test_frame_setitem_c(self):


        f1 = FrameGO(index=sf.Index(tuple('abcde')))
        f1['a'] = 30
        self.assertEqual(f1.to_pairs(0),
                (('a', (('a', 30), ('b', 30), ('c', 30), ('d', 30), ('e', 30))),))




    def test_frame_extend_items_a(self):
        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        columns = OrderedDict(
            (('c', np.array([0, -1])), ('d', np.array([3, 5]))))

        f1.extend_items(columns.items())

        self.assertEqual(f1.columns.values.tolist(),
                ['p', 'q', 'r', 's', 't', 'c', 'd'])

        self.assertTypeBlocksArrayEqual(f1._blocks,
                [[1, 2, 'a', False, True, 0, 3],
                [30, 50, 'b', True, False, -1, 5]],
                match_dtype=object)

    def test_frame_extend_a(self):
        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))
        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        blocks = (np.array([[50, 40], [30, 20]]),
                np.array([[50, 40], [30, 20]]))
        columns = ('a', 'b', 'c', 'd')
        f2 = Frame(TypeBlocks.from_blocks(blocks), columns=columns, index=('y', 'z'))

        f1.extend(f2)
        f3 = f1.fillna(None)

        self.assertEqual(f1.columns.values.tolist(),
                ['p', 'q', 'r', 's', 't', 'a', 'b', 'c', 'd'])

        self.assertEqual(f3.to_pairs(0),
                (('p', (('x', 1), ('y', 30))), ('q', (('x', 2), ('y', 50))), ('r', (('x', 'a'), ('y', 'b'))), ('s', (('x', False), ('y', True))), ('t', (('x', True), ('y', False))), ('a', (('x', None), ('y', 50))), ('b', (('x', None), ('y', 40))), ('c', (('x', None), ('y', 50))), ('d', (('x', None), ('y', 40))))
                )

    def test_frame_extend_b(self):
        records = (
                ('a', False, True),
                ('b', True, False))
        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r'),
                index=('x','y'))

        s1 = Series((200, -3), index=('y', 'x'))

        # this will work with a None name

        f1.extend(s1)

        self.assertEqual(f1.columns.values.tolist(), ['p', 'q', 'r', None])
        self.assertEqual(f1[None].values.tolist(), [-3, 200])


    def test_frame_extend_c(self):
        records = (
                ('a', False, True),
                ('b', True, False))
        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r'),
                index=('x','y'))

        s1 = Series((200, -3), index=('y', 'x'), name='s')

        f1.extend(s1)

        self.assertEqual(f1.columns.values.tolist(), ['p', 'q', 'r', 's'])
        self.assertEqual(f1['s'].values.tolist(), [-3, 200])

    def test_frame_extend_d(self):
        records = (
                ('a', False, True),
                ('b', True, False))
        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r'),
                index=('x','y'))

        s1 = Series((200, -3), index=('q', 'x'), name='s')

        f1.extend(s1, fill_value=0)

        self.assertEqual(f1.columns.values.tolist(), ['p', 'q', 'r', 's'])
        self.assertEqual(f1['s'].values.tolist(), [-3, 0])


    def test_frame_extend_empty_a(self):
        # full Frame, empty extensions with no index
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )
        f1 = FrameGO.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = FrameGO() # no index or columns

        f1.extend(f2)
        self.assertEqual(f1.shape, (3, 5)) # extension happens, but no change in shape



    def test_frame_extend_empty_b(self):
        # full Frame, empty extension with index
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )
        f1 = FrameGO.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = FrameGO(index=('x', 'y', 'z'))
        f1.extend(f2)
        self.assertEqual(f1.shape, (3, 5)) # extension happens, but no change in shape


    def test_frame_extend_empty_c(self):
        # empty with index, full frame extension

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )
        f1 = FrameGO.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = FrameGO(index=('x', 'y', 'z'))
        f2.extend(f1)
        self.assertEqual(f2.shape, (3, 5)) # extension happens, but no change in shape

        self.assertEqual(f2.to_pairs(0),
                (('a', (('x', 1), ('y', 30), ('z', 54))), ('b', (('x', 2), ('y', 34), ('z', 95))), ('c', (('x', 'a'), ('y', 'b'), ('z', 'c'))), ('d', (('x', False), ('y', True), ('z', False))), ('e', (('x', True), ('y', False), ('z', False))))
                )

    def test_frame_extend_empty_d(self):
        # full Frame, empty extension with different index
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )
        f1 = FrameGO.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = FrameGO(index=('w', 'x', 'y', 'z'))

        # import ipdb; ipdb.set_trace()
        f1.extend(f2)
        self.assertEqual(f1.shape, (3, 5)) # extension happens, but no change in shape



    def test_frame_extend_empty_e(self):
        # empty Frame with no index extended by full frame
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )
        f1 = FrameGO.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = FrameGO() # no index or columns

        f2.extend(f1)
        # as we align on the caller's index, if that index is empty, there is nothing to take from the passed Frame; however, since we observe columns, we add those (empty columns). this falls out of lower-level implementations: could be done differently if desirable.
        self.assertEqual(f2.shape, (0, 5))





    def test_frame_extract_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))


        f2 = f1._extract(row_key=np.array((False, True, True, False), dtype=bool))

        self.assertEqual(f2.to_pairs(0),
                (('p', (('x', 30), ('y', 2))), ('q', (('x', 34), ('y', 95))), ('r', (('x', 'b'), ('y', 'c'))), ('s', (('x', True), ('y', False))), ('t', (('x', False), ('y', False)))))


        f3 = f1._extract(row_key=np.array((True, False, False, True), dtype=bool))

        self.assertEqual(f3.to_pairs(0),
                (('p', (('w', 2), ('z', 30))), ('q', (('w', 2), ('z', 73))), ('r', (('w', 'a'), ('z', 'd'))), ('s', (('w', False), ('z', True))), ('t', (('w', False), ('z', True)))))


        # attempting to select any single row results in a problem, as the first block given to the TypeBlocks constructor is a 1d array that looks it is a (2,1) instead of a (1, 2)
        f4 = f1._extract(row_key=np.array((False, False, True, False), dtype=bool))

        self.assertEqual(
                f4.to_pairs(0),
                (('p', (('y', 2),)), ('q', (('y', 95),)), ('r', (('y', 'c'),)), ('s', (('y', False),)), ('t', (('y', False),)))
                )


    def test_frame_extract_b(self):
        # examining cases where shape goes to zero in one dimension

        f1 = Frame(None, index=tuple('ab'), columns=('c',))
        f2 = f1[[]]
        self.assertEqual(len(f2.columns), 0)
        self.assertEqual(len(f2.index), 2)
        self.assertEqual(f2.shape, (2, 0))


    def test_frame_extract_c(self):
        # examining cases where shape goes to zero in one dimension
        f1 = Frame(None, columns=tuple('ab'), index=('c',))
        f2 = f1.loc[[]]
        self.assertEqual(f2.shape, (0, 2))
        self.assertEqual(len(f2.columns), 2)
        self.assertEqual(len(f2.index), 0)


    def test_frame_loc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # cases of single series extraction
        s1 = f1.loc['x']
        self.assertEqual(list(s1.items()),
                [('p', 1), ('q', 2), ('r', 'a'), ('s', False), ('t', True)])

        s2 = f1.loc[:, 'p']
        self.assertEqual(list(s2.items()),
                [('x', 1), ('y', 30)])

        self.assertEqual(
                f1.loc[['y', 'x']].index.values.tolist(),
                ['y', 'x'])

        self.assertEqual(f1['r':].columns.values.tolist(),
                ['r', 's', 't'])


    def test_frame_loc_b(self):
        # dimensionality of returned item based on selectors
        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # return a series if one axis is multi
        post = f1.loc['x', 't':]
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.index.values.tolist(), ['t'])

        post = f1.loc['y':, 't']
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.index.values.tolist(), ['y'])

        # if both are multi than we get a Frame
        post = f1.loc['y':, 't':]
        self.assertEqual(post.__class__, Frame)
        self.assertEqual(post.index.values.tolist(), ['y'])
        self.assertEqual(post.columns.values.tolist(), ['t'])

        # return a series
        post = f1.loc['x', 's':]
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.index.values.tolist(),['s', 't'])

        post = f1.loc[:, 's']
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.index.values.tolist(), ['x', 'y'])

        self.assertEqual(f1.loc['x', 's'], False)
        self.assertEqual(f1.loc['y', 'p'], 30)


    def test_frame_loc_c(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = f1.loc['x':]
        self.assertEqual(post.index.values.tolist(),
                ['x', 'y', 'z'])


    def test_frame_loc_d(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'),
                name='foo')

        f2 = f1['r':]
        f3 = f1.loc[['y'], ['r']]
        self.assertEqual(f1.name, 'foo')
        self.assertEqual(f2.name, 'foo')
        self.assertEqual(f3.name, 'foo')

        s1 = f2.loc[:, 's']
        self.assertEqual(s1.name, 's')

        s2 = f1.loc['x', :'r']
        self.assertEqual(s2.name, 'x')



    def test_frame_items_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(
                list((k, list(v.items())) for k, v in f1.items()),
                [('p', [('x', 1), ('y', 30)]), ('q', [('x', 2), ('y', 50)]), ('r', [('x', 'a'), ('y', 'b')]), ('s', [('x', False), ('y', True)]), ('t', [('x', True), ('y', False)])]
                )




    @skip_win
    def test_frame_attrs_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(str(f1.dtypes.values.tolist()),
                "[dtype('int64'), dtype('int64'), dtype('<U1'), dtype('bool'), dtype('bool')]")

        self.assertEqual(f1.size, 10)
        self.assertEqual(f1.ndim, 2)
        self.assertEqual(f1.shape, (2, 5))



    def test_frame_assign_iloc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))


        self.assertEqual(f1.assign.iloc[1,1](3000).iloc[1,1], 3000)


    def test_frame_assign_loc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(f1.assign.loc['x', 's'](3000).values.tolist(),
                [[1, 2, 'a', 3000, True], [30, 50, 'b', True, False]])

        # can assign to a columne
        self.assertEqual(
                f1.assign['s']('x').values.tolist(),
                [[1, 2, 'a', 'x', True], [30, 50, 'b', 'x', False]])


    def test_frame_assign_loc_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # unindexed tuple/list assingment
        self.assertEqual(
                f1.assign['s']([50, 40]).values.tolist(),
                [[1, 2, 'a', 50, True], [30, 50, 'b', 40, False]]
                )

        self.assertEqual(
                f1.assign.loc['y'](list(range(5))).values.tolist(),
                [[1, 2, 'a', False, True], [0, 1, 2, 3, 4]])




    def test_frame_assign_loc_c(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # assinging a series to a part of wone row
        post = f1.assign.loc['x', 'r':](Series((-1, -2, -3), index=('t', 'r', 's')))

        self.assertEqual(post.values.tolist(),
                [[1, 2, -2, -3, -1], [30, 50, 'b', True, False]])

        post = f1.assign.loc[['x', 'y'], 'r'](Series((-1, -2), index=('y', 'x')))

        self.assertEqual(post.values.tolist(),
                [[1, 2, -2, False, True], [30, 50, -1, True, False]])

        # ordere here does not matter
        post = f1.assign.loc[['y', 'x'], 'r'](Series((-1, -2), index=('y', 'x')))

        self.assertEqual(post.values.tolist(),
                [[1, 2, -2, False, True], [30, 50, -1, True, False]])


    def test_frame_assign_loc_d(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'),
                consolidate_blocks=True)

        value1 = Frame.from_records(((20, 21, 22),(23, 24, 25)),
                index=('x', 'y'),
                columns=('s', 't', 'w'),
                consolidate_blocks=True)


        f2 = f1.assign.loc[['x', 'y'], ['s', 't']](value1)

        # In : f1.assign.loc[['x', 'y'], ['s', 't']](value1)
        # <Frame>
        # <Index> p       q       r     s        t        <<U1>
        # <Index>
        # x       1       2       a     20       21
        # y       30      50      b     23       24
        # <<U1>   <int64> <int64> <<U1> <object> <object>

        self.assertEqual(f2.to_pairs(0),
                (('p', (('x', 1), ('y', 30))), ('q', (('x', 2), ('y', 50))), ('r', (('x', 'a'), ('y', 'b'))), ('s', (('x', 20), ('y', 23))), ('t', (('x', 21), ('y', 24)))))


    def test_frame_assign_loc_e(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False),
                (30, 50, 'c', False, False),
                (3, 5, 'c', False, True),
                (30, 500, 'd', True, True),
                (30, 2, 'e', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=list('abcdef')
                )

        f3 = f1.assign.iloc[5](f1.iloc[0])
        self.assertEqual(f3.to_pairs(0),
                (('p', (('a', 1), ('b', 30), ('c', 30), ('d', 3), ('e', 30), ('f', 1))), ('q', (('a', 2), ('b', 50), ('c', 50), ('d', 5), ('e', 500), ('f', 2))), ('r', (('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'c'), ('e', 'd'), ('f', 'a'))), ('s', (('a', False), ('b', True), ('c', False), ('d', False), ('e', True), ('f', False))), ('t', (('a', True), ('b', False), ('c', False), ('d', True), ('e', True), ('f', True))))
                )

        f4 = f1.assign['q'](f1['q'] * 2)
        self.assertEqual(f4.to_pairs(0),
                (('p', (('a', 1), ('b', 30), ('c', 30), ('d', 3), ('e', 30), ('f', 30))), ('q', (('a', 4), ('b', 100), ('c', 100), ('d', 10), ('e', 1000), ('f', 4))), ('r', (('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'c'), ('e', 'd'), ('f', 'e'))), ('s', (('a', False), ('b', True), ('c', False), ('d', False), ('e', True), ('f', True))), ('t', (('a', True), ('b', False), ('c', False), ('d', True), ('e', True), ('f', True))))
                )

        f5 = f1.assign[['p', 'q']](f1[['p', 'q']] * 2)
        self.assertEqual(f5.to_pairs(0),
                (('p', (('a', 2), ('b', 60), ('c', 60), ('d', 6), ('e', 60), ('f', 60))), ('q', (('a', 4), ('b', 100), ('c', 100), ('d', 10), ('e', 1000), ('f', 4))), ('r', (('a', 'a'), ('b', 'b'), ('c', 'c'), ('d', 'c'), ('e', 'd'), ('f', 'e'))), ('s', (('a', False), ('b', True), ('c', False), ('d', False), ('e', True), ('f', True))), ('t', (('a', True), ('b', False), ('c', False), ('d', True), ('e', True), ('f', True))))
                )


    def test_frame_assign_coercion_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))
        f2 = f1.assign.loc['x', 'r'](None)
        self.assertEqual(f2.to_pairs(0),
                (('p', (('x', 1), ('y', 30))), ('q', (('x', 2), ('y', 50))), ('r', (('x', None), ('y', 'b'))), ('s', (('x', False), ('y', True))), ('t', (('x', True), ('y', False)))))


    def test_frame_mask_loc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(
                f1.mask.loc['x', 'r':].values.tolist(),
                [[False, False, True, True, True], [False, False, False, False, False]])


        self.assertEqual(f1.mask['s'].values.tolist(),
                [[False, False, False, True, False], [False, False, False, True, False]])


    def test_frame_masked_array_loc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # mask our the non-integers
        self.assertEqual(
                f1.masked_array.loc[:, 'r':].sum(), 83)


    def test_reindex_other_like_iloc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        value1 = Series((100, 200, 300), index=('s', 'u', 't'))
        iloc_key1 = (0, slice(2, None))
        v1 = f1._reindex_other_like_iloc(value1, iloc_key1)

        self.assertAlmostEqualItems(v1.items(),
                [('r', nan), ('s', 100), ('t', 300)])


        value2 = Series((100, 200), index=('y', 'x'))
        iloc_key2 = (slice(0, None), 2)
        v2 = f1._reindex_other_like_iloc(value2, iloc_key2)

        self.assertAlmostEqualItems(v2.items(),
                [('x', 200), ('y', 100)])


    def test_reindex_other_like_iloc_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        value1 = Frame.from_records(((20, 21, 22),(23, 24, 25)),
                index=('x', 'y'),
                columns=('s', 't', 'w'))

        iloc_key1 = (slice(0, None), slice(3, None))
        v1 = f1._reindex_other_like_iloc(value1, iloc_key1)

        self.assertEqual(v1.to_pairs(0),
                (('s', (('x', 20), ('y', 23))), ('t', (('x', 21), ('y', 24)))))


    def test_frame_reindex_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        # subset index reindex
        self.assertEqual(
                f1.reindex(('z', 'w')).to_pairs(axis=0),
                (('p', (('z', 65), ('w', 1))), ('q', (('z', 73), ('w', 2))), ('r', (('z', 'd'), ('w', 'a'))), ('s', (('z', True), ('w', False))), ('t', (('z', True), ('w', True)))))

        # index only with nan filling
        self.assertEqual(
                f1.reindex(('z', 'b', 'w'), fill_value=None).to_pairs(0),
                (('p', (('z', 65), ('b', None), ('w', 1))), ('q', (('z', 73), ('b', None), ('w', 2))), ('r', (('z', 'd'), ('b', None), ('w', 'a'))), ('s', (('z', True), ('b', None), ('w', False))), ('t', (('z', True), ('b', None), ('w', True)))))



    def test_frame_axis_flat_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.to_pairs(axis=1),
                (('w', (('p', 1), ('q', 2), ('r', 'a'), ('s', False), ('t', True))), ('x', (('p', 30), ('q', 34), ('r', 'b'), ('s', True), ('t', False))), ('y', (('p', 54), ('q', 95), ('r', 'c'), ('s', False), ('t', False))), ('z', (('p', 65), ('q', 73), ('r', 'd'), ('s', True), ('t', True)))))


        self.assertEqual(f1.to_pairs(axis=0),
                (('p', (('w', 1), ('x', 30), ('y', 54), ('z', 65))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('r', (('w', 'a'), ('x', 'b'), ('y', 'c'), ('z', 'd'))), ('s', (('w', False), ('x', True), ('y', False), ('z', True))), ('t', (('w', True), ('x', False), ('y', False), ('z', True)))))


    def test_frame_reindex_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(
                f1.reindex(columns=('q', 'p', 'w'), fill_value=None).to_pairs(0),
                (('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('p', (('w', 1), ('x', 30), ('y', 54), ('z', 65))), ('w', (('w', None), ('x', None), ('y', None), ('z', None)))))

        self.assertEqual(
                f1.reindex(columns=('q', 'p', 's')).to_pairs(0),
                (('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('p', (('w', 1), ('x', 30), ('y', 54), ('z', 65))), ('s', (('w', False), ('x', True), ('y', False), ('z', True)))))

        f2 = f1[['p', 'q']]

        self.assertEqual(
                f2.reindex(columns=('q', 'p')).to_pairs(0),
                (('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('p', (('w', 1), ('x', 30), ('y', 54), ('z', 65)))))

        self.assertEqual(
                f2.reindex(columns=('a', 'b'), fill_value=None).to_pairs(0),
                (('a', (('w', None), ('x', None), ('y', None), ('z', None))), ('b', (('w', None), ('x', None), ('y', None), ('z', None)))))


    def test_frame_reindex_c(self):
        # reindex both axis
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))


        self.assertEqual(
                f1.reindex(index=('y', 'x'), columns=('s', 'q')).to_pairs(0),
                (('s', (('y', False), ('x', True))), ('q', (('y', 95), ('x', 34)))))

        self.assertEqual(
                f1.reindex(index=('x', 'y'), columns=('s', 'q', 'u'),
                        fill_value=None).to_pairs(0),
                (('s', (('x', True), ('y', False))), ('q', (('x', 34), ('y', 95))), ('u', (('x', None), ('y', None)))))

        self.assertEqual(
                f1.reindex(index=('a', 'b'), columns=('c', 'd'),
                        fill_value=None).to_pairs(0),
                (('c', (('a', None), ('b', None))), ('d', (('a', None), ('b', None)))))


        f2 = f1[['p', 'q']]

        self.assertEqual(
                f2.reindex(index=('x',), columns=('q',)).to_pairs(0),
                (('q', (('x', 34),)),))

        self.assertEqual(
                f2.reindex(index=('y', 'x', 'q'), columns=('q',),
                        fill_value=None).to_pairs(0),
                (('q', (('y', 95), ('x', 34), ('q', None))),))


    def test_frame_reindex_d(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )

        columns = IndexHierarchy.from_labels((('a', 1), ('a', 2), ('b', 1), ('b', 2), ('b', 3)))
        f1 = Frame.from_records(records,
                columns=columns,
                index=('x', 'y', 'z'))

        # NOTE: must use HLoc on getting a single columns as otherwise looks like a multiple axis selection
        self.assertEqual(f1[sf.HLoc['a', 1]].to_pairs(),
                (('x', 1), ('y', 30), ('z', 54))
                )

        self.assertEqual(f1[sf.HLoc['b', 1]:].to_pairs(0),
                ((('b', 1), (('x', 'a'), ('y', 'b'), ('z', 'c'))), (('b', 2), (('x', False), ('y', True), ('z', False))), (('b', 3), (('x', True), ('y', False), ('z', False)))))

        # reindexing with no column matches results in NaN for all values
        self.assertTrue(
                f1.iloc[:, 1:].reindex(columns=IndexHierarchy.from_product(('b', 'a'), (10, 20))).isna().all().all())

        columns = IndexHierarchy.from_product(('b', 'a'), (3, 2))
        f2 = f1.reindex(columns=columns, fill_value=None)
        self.assertEqual(f2.to_pairs(0),
                ((('b', 3), (('x', True), ('y', False), ('z', False))), (('b', 2), (('x', False), ('y', True), ('z', False))), (('a', 3), (('x', None), ('y', None), ('z', None))), (('a', 2), (('x', 2), ('y', 34), ('z', 95)))))


    def test_frame_reindex_e(self):

        records = (
                (1, 2, 'a', False),
                (30, 34, 'b', True),
                (54, 95, 'c', False),
                (65, 73, 'd', True),
                )

        columns = IndexHierarchy.from_product(('a', 'b'), (1, 2))
        index = IndexHierarchy.from_product((100, 200), (True, False))

        f1 = Frame.from_records(records,
                columns=columns,
                index=index)

        self.assertEqual(f1.loc[(200, True):, ('b',1):].to_pairs(0),
                ((('b', 1), (((200, True), 'c'), ((200, False), 'd'))), (('b', 2), (((200, True), False), ((200, False), True)))))

        # reindex from IndexHierarchy to Index with tuples
        f2 = f1.reindex(
                index=IndexHierarchy.from_product((200, 300), (False, True)),
                columns=[('b',1),('a',1)],
                fill_value=None)
        self.assertEqual(f2.to_pairs(0),
                ((('b', 1), (((200, False), 'd'), ((200, True), 'c'), ((300, False), None), ((300, True), None))), (('a', 1), (((200, False), 65), ((200, True), 54), ((300, False), None), ((300, True), None)))))



    def test_frame_reindex_f(self):

        records = (
                (1, 2, 'a', False),
                (30, 34, 'b', True),
                )
        columns = IndexHierarchy.from_product(('a', 'b'), (1, 2))
        f1 = Frame.from_records(records, columns=columns, name='foo')
        f2 = f1.reindex(index=(0,1,2), fill_value=0)

        self.assertEqual(f1.name, 'foo')
        self.assertEqual(f2.name, 'foo')



    def test_frame_axis_interface_a(self):
        # reindex both axis
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.to_pairs(1),
                (('w', (('p', 1), ('q', 2), ('r', 'a'), ('s', False), ('t', True))), ('x', (('p', 30), ('q', 34), ('r', 'b'), ('s', True), ('t', False))), ('y', (('p', 54), ('q', 95), ('r', 'c'), ('s', False), ('t', False))), ('z', (('p', 65), ('q', 73), ('r', 'd'), ('s', True), ('t', True)))))

        for x in f1.iter_tuple(0):
            self.assertTrue(len(x), 4)

        for x in f1.iter_tuple(1):
            self.assertTrue(len(x), 5)


        f2 = f1[['p', 'q']]

        s1 = f2.iter_array(0).apply(np.sum)
        self.assertEqual(list(s1.items()), [('p', 150), ('q', 204)])

        s2 = f2.iter_array(1).apply(np.sum)
        self.assertEqual(list(s2.items()),
                [('w', 3), ('x', 64), ('y', 149), ('z', 138)])

        def sum_if(idx, vals):
            if idx in ('x', 'z'):
                return np.sum(vals)

        s3 = f2.iter_array_items(1).apply(sum_if)
        self.assertEqual(list(s3.items()),
                [('w', None), ('x', 64), ('y', None), ('z', 138)])



    def test_frame_group_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = tuple(f1._axis_group_iloc_items(4, axis=0)) # row iter, group by column 4

        group1, group_frame_1 = post[0]
        group2, group_frame_2 = post[1]

        self.assertEqual(group1, False)
        self.assertEqual(group2, True)

        self.assertEqual(group_frame_1.to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 2))), ('q', (('w', 2), ('x', 34), ('y', 95))), ('r', (('w', 'a'), ('x', 'b'), ('y', 'c'))), ('s', (('w', False), ('x', True), ('y', False))), ('t', (('w', False), ('x', False), ('y', False)))))

        self.assertEqual(group_frame_2.to_pairs(0),
                (('p', (('z', 30),)), ('q', (('z', 73),)), ('r', (('z', 'd'),)), ('s', (('z', True),)), ('t', (('z', True),))))


    def test_frame_group_b(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        # column iter, group by row 0
        post = list(f1._axis_group_iloc_items(0, axis=1))

        self.assertEqual(post[0][0], 2)
        self.assertEqual(post[0][1].to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 2), ('z', 30))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73)))))

        self.assertEqual(post[1][0], False)
        self.assertEqual(post[1][1].to_pairs(0),
                (('s', (('w', False), ('x', True), ('y', False), ('z', True))), ('t', (('w', False), ('x', False), ('y', False), ('z', True)))))

        self.assertEqual(post[2][0], 'a')

        self.assertEqual(post[2][1].to_pairs(0),
                (('r', (('w', 'a'), ('x', 'b'), ('y', 'c'), ('z', 'd'))),))



    def test_frame_axis_interface_b(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = list(f1.iter_group_items('s', axis=0))

        self.assertEqual(post[0][1].to_pairs(0),
                (('p', (('w', 2), ('y', 2))), ('q', (('w', 2), ('y', 95))), ('r', (('w', 'a'), ('y', 'c'))), ('s', (('w', False), ('y', False))), ('t', (('w', False), ('y', False)))))

        self.assertEqual(post[1][1].to_pairs(0),
                (('p', (('x', 30), ('z', 30))), ('q', (('x', 34), ('z', 73))), ('r', (('x', 'b'), ('z', 'd'))), ('s', (('x', True), ('z', True))), ('t', (('x', False), ('z', True)))))


        s1 = f1.iter_group('p', axis=0).apply(lambda f: f['q'].values.sum())
        self.assertEqual(list(s1.items()), [(2, 97), (30, 107)])


    def test_frame_contains_a(self):

        f1 = Frame.from_items(zip(('a', 'b'), ([20, 30, 40], [80, 10, 30])),
                index=('x', 'y', 'z'))

        self.assertTrue('a' in f1)
        self.assertTrue('b' in f1)
        self.assertFalse('x' in f1)
        self.assertFalse('y' in f1)



    def test_frame_sum_a(self):
        # reindex both axis
        records = (
                (2, 2, 3, 4.23, 50.234),
                (30, 34, 60, 80.6, 90.123),
                (2, 95, 1, 1.96, 1.54),
                (30, 73, 50, 40.23, 30.234),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = f1.sum(axis=0)
        self.assertAlmostEqualItems(list(post.items()),
                [('p', 64.0), ('q', 204.0), ('r', 114.0), ('s', 127.01999999999998), ('t', 172.131)])
        self.assertEqual(post.dtype, np.float64)

        post = f1.sum(axis=1) # sum columns, return row index
        self.assertEqual(list(f1.sum(axis=1).items()),
                [('w', 61.463999999999999), ('x', 294.72300000000001), ('y', 101.5), ('z', 223.464)])
        self.assertEqual(post.dtype, np.float64)


    def test_frame_sum_b(self):

        records = (
                (2, 2, 3),
                (30, 34, 60),
                (2, 95, 1),
                (30, 73, 50),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        post = f1.sum(axis=0)

        self.assertEqual(list(post.items()),
                [('p', 64), ('q', 204), ('r', 114)])

        self.assertEqual(list(f1.sum(axis=1).items()),
                [('w', 7), ('x', 124), ('y', 98), ('z', 153)])


    def test_frame_sum_c(self):

        index = list(''.join(x) for x in it.combinations(string.ascii_lowercase, 2))

        f1 = FrameGO(index=index)
        for col in range(100):
            s = Series(col * .1, index=index[col: col+20])
            f1[col] = s
        assert f1.sum().sum() == 9900.0


    def test_frame_prod_a(self):

        records = (
                (2, 2, 3),
                (30, 34, 60),
                (2, 95, 1),
                (30, 73, 50),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(
            f1.prod(axis=0).to_pairs(),
            (('p', 3600), ('q', 471580), ('r', 9000))
            )

        self.assertEqual(f1.prod(axis=1).to_pairs(),
            (('w', 12), ('x', 61200), ('y', 190), ('z', 109500))
            )



    def test_frame_cumsum_a(self):

        records = (
                (2, 2, 3),
                (30, 34, 60),
                (2, 95, 1),
                (30, 73, 50),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        f2 = f1.cumsum()

        self.assertEqual(
                f2.to_pairs(0),
                (('p', (('w', 2), ('x', 32), ('y', 34), ('z', 64))), ('q', (('w', 2), ('x', 36), ('y', 131), ('z', 204))), ('r', (('w', 3), ('x', 63), ('y', 64), ('z', 114))))
                )
        self.assertEqual(f1.cumsum(1).to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 2), ('z', 30))), ('q', (('w', 4), ('x', 64), ('y', 97), ('z', 103))), ('r', (('w', 7), ('x', 124), ('y', 98), ('z', 153))))
                )



    def test_frame_cumprod_a(self):

        records = (
                (2, 2, 3),
                (30, 34, 60),
                (2, 95, 1),
                (30, 73, 50),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.cumprod(0).to_pairs(0),
                (('p', (('w', 2), ('x', 60), ('y', 120), ('z', 3600))), ('q', (('w', 2), ('x', 68), ('y', 6460), ('z', 471580))), ('r', (('w', 3), ('x', 180), ('y', 180), ('z', 9000))))
                )

        self.assertEqual(f1.cumprod(1).to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 2), ('z', 30))), ('q', (('w', 4), ('x', 1020), ('y', 190), ('z', 2190))), ('r', (('w', 12), ('x', 61200), ('y', 190), ('z', 109500))))
                )

    def test_frame_min_a(self):
        # reindex both axis
        records = (
                (2, 2, 3, 4.23, 50.234),
                (30, 34, 60, 80.6, 90.123),
                (2, 95, 1, 1.96, 1.54),
                (30, 73, 50, 40.23, 30.234),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertAlmostEqualItems(tuple(f1.min().items()),
                (('p', 2.0), ('q', 2.0), ('r', 1.0), ('s', 1.96), ('t', 1.54)))

        self.assertAlmostEqualItems(tuple(f1.min(axis=1).items()),
                (('w', 2.0), ('x', 30.0), ('y', 1.0), ('z', 30.0)))

    @skip_win
    def test_frame_row_dtype_a(self):
        # reindex both axis
        records = (
                (2, 2, 3, 4.23, 50.234),
                (30, 34, 60, 80.6, 90.123),
                (2, 95, 1, 1.96, 1.54),
                (30, 73, 50, 40.23, 30.234),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1['t'].dtype, np.float64)
        self.assertEqual(f1['p'].dtype, np.int64)

        self.assertEqual(f1.loc['w'].dtype, np.float64)
        self.assertEqual(f1.loc['z'].dtype, np.float64)

        self.assertEqual(f1[['r', 's']].values.dtype, np.float64)

    def test_frame_unary_operator_a(self):

        records = (
                (2, 2, 3, False, True),
                (30, 34, 60, True, False),
                (2, 95, 1, True, True),
                (30, 73, 50, False, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        # raises exception with NP14
        # self.assertEqual((-f1).to_pairs(0),
        #         (('p', (('w', -2), ('x', -30), ('y', -2), ('z', -30))), ('q', (('w', -2), ('x', -34), ('y', -95), ('z', -73))), ('r', (('w', -3), ('x', -60), ('y', -1), ('z', -50))), ('s', (('w', True), ('x', False), ('y', False), ('z', True))), ('t', (('w', False), ('x', True), ('y', False), ('z', True)))))

        self.assertEqual((~f1).to_pairs(0),
                (('p', (('w', -3), ('x', -31), ('y', -3), ('z', -31))), ('q', (('w', -3), ('x', -35), ('y', -96), ('z', -74))), ('r', (('w', -4), ('x', -61), ('y', -2), ('z', -51))), ('s', (('w', True), ('x', False), ('y', False), ('z', True))), ('t', (('w', False), ('x', True), ('y', False), ('z', True)))))


    def test_frame_binary_operator_a(self):
        # constants

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual((f1 * 30).to_pairs(0),
                (('p', (('w', 60), ('x', 900), ('y', 60), ('z', 900))), ('q', (('w', 60), ('x', 1020), ('y', 2850), ('z', 2190))), ('r', (('w', 105.0), ('x', 1806.0), ('y', 36.0), ('z', 1506.0))))
                )



    def test_frame_binary_operator_b(self):

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        f2 = f1.loc[['y', 'z'], ['r']]
        f3 = f1 * f2

        self.assertAlmostEqualItems(list(f3['p'].items()),
                [('w', nan), ('x', nan), ('y', nan), ('z', nan)])
        self.assertAlmostEqualItems(list(f3['r'].items()),
                [('w', nan), ('x', nan), ('y', 1.4399999999999999), ('z', 2520.0400000000004)])

    def test_frame_binary_operator_c(self):

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        s1 = Series([0, 1, 2], index=('r', 'q', 'p'))

        self.assertEqual((f1 * s1).to_pairs(0),
                (('p', (('w', 4), ('x', 60), ('y', 4), ('z', 60))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('r', (('w', 0.0), ('x', 0.0), ('y', 0.0), ('z', 0.0)))))

        self.assertEqual((f1 * [0, 1, 0]).to_pairs(0),
                (('p', (('w', 0), ('x', 0), ('y', 0), ('z', 0))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('r', (('w', 0.0), ('x', 0.0), ('y', 0.0), ('z', 0.0)))))


    def test_frame_binary_operator_d(self):

        records = (
                (2, True, ''),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'))

        self.assertEqual((f1['q'] == True).to_pairs(),
                ((0, True),))

        # this handles the case where, because we are comparing to an empty string, NumPy returns a single Boolean. This is manually handled in Series._ufunc_binary_operator
        self.assertEqual((f1['r'] == True).to_pairs(),
                ((0, False),))



    def test_frame_isin_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = f1.isin({'a', 73, 30})
        self.assertEqual(post.to_pairs(0),
                (('p', (('w', False), ('x', True), ('y', False), ('z', True))), ('q', (('w', False), ('x', False), ('y', False), ('z', True))), ('r', (('w', True), ('x', False), ('y', False), ('z', False))), ('s', (('w', False), ('x', False), ('y', False), ('z', False))), ('t', (('w', False), ('x', False), ('y', False), ('z', False)))))


        post = f1.isin(['a', 73, 30])
        self.assertEqual(post.to_pairs(0),
                (('p', (('w', False), ('x', True), ('y', False), ('z', True))), ('q', (('w', False), ('x', False), ('y', False), ('z', True))), ('r', (('w', True), ('x', False), ('y', False), ('z', False))), ('s', (('w', False), ('x', False), ('y', False), ('z', False))), ('t', (('w', False), ('x', False), ('y', False), ('z', False)))))


    def test_frame_transpose_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'),
                name='foo')

        f2 = f1.transpose()

        self.assertEqual(f2.to_pairs(0),
                (('w', (('p', 2), ('q', 2), ('r', 'a'), ('s', False), ('t', False))), ('x', (('p', 30), ('q', 34), ('r', 'b'), ('s', True), ('t', False))), ('y', (('p', 2), ('q', 95), ('r', 'c'), ('s', False), ('t', False))), ('z', (('p', 30), ('q', 73), ('r', 'd'), ('s', True), ('t', True)))))

        self.assertEqual(f2.name, f1.name)


    def test_frame_from_element_iloc_items_a(self):
        items = (((0,1), 'g'), ((1,0), 'q'))

        f1 = Frame.from_element_iloc_items(items,
                index=('a', 'b'),
                columns=('x', 'y'),
                dtype=object,
                name='foo'
                )

        self.assertEqual(f1.to_pairs(0),
                (('x', (('a', None), ('b', 'q'))), ('y', (('a', 'g'), ('b', None)))))


        self.assertEqual(f1.name, 'foo')


    def test_frame_from_element_iloc_items_b(self):

        items = (((0,1), .5), ((1,0), 1.5))

        f2 = Frame.from_element_iloc_items(items,
                index=('a', 'b'),
                columns=('x', 'y'),
                dtype=float
                )

        self.assertAlmostEqualItems(tuple(f2['x'].items()),
                (('a', nan), ('b', 1.5)))

        self.assertAlmostEqualItems(tuple(f2['y'].items()),
                (('a', 0.5), ('b', nan)))


    def test_frame_from_element_loc_items_a(self):
        items = ((('b', 'x'), 'g'), (('a','y'), 'q'))

        f1 = Frame.from_element_loc_items(items,
                index=('a', 'b'),
                columns=('x', 'y'),
                dtype=object,
                name='foo'
                )

        self.assertEqual(f1.to_pairs(0),
                (('x', (('a', None), ('b', 'g'))), ('y', (('a', 'q'), ('b', None)))))
        self.assertEqual(f1.name, 'foo')

    def test_frame_from_items_a(self):

        f1 = Frame.from_items(
                zip(range(10), (np.random.rand(1000) for _ in range(10))),
                name='foo'
                )
        self.assertEqual(f1.name, 'foo')

    def test_frame_from_items_b(self):

        s1 = Series((1, 2, 3), index=('a', 'b', 'c'))
        s2 = Series((4, 5, 6), index=('a', 'b', 'c'))

        with self.assertRaises(RuntimeError):
            # must have an index to consume Series
            Frame.from_items(zip(list('xy'), (s1, s2)))

    def test_frame_from_items_c(self):

        s1 = Series((1, 2, 3), index=('a', 'b', 'c'))
        s2 = Series((4, 5, 6), index=('a', 'b', 'c'))

        f1 = Frame.from_items(zip(list('xy'), (s1, s2)), index=s1.index)

        self.assertEqual(f1.to_pairs(0),
                (('x', (('a', 1), ('b', 2), ('c', 3))), ('y', (('a', 4), ('b', 5), ('c', 6)))))

    def test_frame_from_items_d(self):

        s1 = Series((1, 2, 3), index=('a', 'b', 'c'))
        s2 = Series((4, 5, 6), index=('a', 'b', 'c'))

        f1 = Frame.from_items(zip(list('xy'), (s1, s2)), index=('c', 'a'))

        self.assertEqual(f1.to_pairs(0),
            (('x', (('c', 3), ('a', 1))), ('y', (('c', 6), ('a', 4)))))


    def test_frame_from_items_e(self):

        s1 = Series((1, 2, 3), index=('a', 'b', 'c'))
        s2 = Series((4, 5, 6), index=('a', 'b', 'c'))
        s3 = Series((7, 8, 9), index=('a', 'b', 'c'))

        f1 = Frame.from_items(zip(list('xy'), (s1, s2, s3)), index=('c', 'a'),
                consolidate_blocks=True)

        self.assertEqual(len(f1._blocks._blocks), 1)



    def test_frame_from_structured_array_a(self):
        a = np.array([('Venus', 4.87, 464), ('Neptune', 102, -200)],
                dtype=[('name', object), ('mass', 'f4'), ('temperature', 'i4')])

        f = sf.Frame.from_structured_array(a, index_column='name', name='foo')

        self.assertEqual(f.shape, (2, 2))
        self.assertEqual(f.name, 'foo')
        self.assertEqual(f['temperature'].sum(), 264)


    def test_frame_from_structured_array_b(self):
        a = np.array([('Venus', 4.87, 464), ('Neptune', 102, -200)],
                dtype=[('name', object), ('mass', 'f4'), ('temperature', 'i4')])

        f = sf.Frame.from_structured_array(a, index_column=2, name='foo')
        self.assertEqual(f['name'].to_pairs(),
                ((464, 'Venus'), (-200, 'Neptune')))



    def test_frame_iter_element_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(
                [x for x in f1.iter_element()],
                [2, 2, 'a', False, False, 30, 34, 'b', True, False, 2, 95, 'c', False, False, 30, 73, 'd', True, True])

        self.assertEqual([x for x in f1.iter_element_items()],
                [(('w', 'p'), 2), (('w', 'q'), 2), (('w', 'r'), 'a'), (('w', 's'), False), (('w', 't'), False), (('x', 'p'), 30), (('x', 'q'), 34), (('x', 'r'), 'b'), (('x', 's'), True), (('x', 't'), False), (('y', 'p'), 2), (('y', 'q'), 95), (('y', 'r'), 'c'), (('y', 's'), False), (('y', 't'), False), (('z', 'p'), 30), (('z', 'q'), 73), (('z', 'r'), 'd'), (('z', 's'), True), (('z', 't'), True)])


        post = f1.iter_element().apply(lambda x: '_' + str(x) + '_')

        self.assertEqual(post.to_pairs(0),
                (('p', (('w', '_2_'), ('x', '_30_'), ('y', '_2_'), ('z', '_30_'))), ('q', (('w', '_2_'), ('x', '_34_'), ('y', '_95_'), ('z', '_73_'))), ('r', (('w', '_a_'), ('x', '_b_'), ('y', '_c_'), ('z', '_d_'))), ('s', (('w', '_False_'), ('x', '_True_'), ('y', '_False_'), ('z', '_True_'))), ('t', (('w', '_False_'), ('x', '_False_'), ('y', '_False_'), ('z', '_True_')))))




    def test_frame_iter_element_b(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        # support working with mappings
        post = f1.iter_element().apply({2: 200, False: 200})

        self.assertEqual(post.to_pairs(0),
                (('p', (('w', 200), ('x', 30), ('y', 200), ('z', 30))), ('q', (('w', 200), ('x', 34), ('y', 95), ('z', 73))), ('r', (('w', 'a'), ('x', 'b'), ('y', 'c'), ('z', 'd'))), ('s', (('w', 200), ('x', True), ('y', 200), ('z', True))), ('t', (('w', 200), ('x', 200), ('y', 200), ('z', True))))
                )

    # @unittest.skip('in development')
    def test_frame_iter_element_c(self):

        a2 = np.array([
                [None, None],
                [None, 1],
                [None, 5]
                ], dtype=object)
        a1 = np.array([True, False, True])
        a3 = np.array([['a'], ['b'], ['c']])

        tb1 = TypeBlocks.from_blocks((a3, a1, a2))

        f1 = Frame(tb1,
                index=self.get_letters(None, tb1.shape[0]),
                columns=IndexHierarchy.from_product(('i', 'ii'), ('a', 'b'))
                )
        values = list(f1.iter_element())
        self.assertEqual(values,
                ['a', True, None, None, 'b', False, None, 1, 'c', True, None, 5]
                )

        f2 = f1.iter_element().apply(lambda x: str(x).lower().replace('e', ''))

        self.assertEqual(f2.to_pairs(0),
                ((('i', 'a'), (('a', 'a'), ('b', 'b'), ('c', 'c'))), (('i', 'b'), (('a', 'tru'), ('b', 'fals'), ('c', 'tru'))), (('ii', 'a'), (('a', 'non'), ('b', 'non'), ('c', 'non'))), (('ii', 'b'), (('a', 'non'), ('b', '1'), ('c', '5'))))
                )

    def test_frame_reversed(self):
        columns = tuple('pqrst')
        index = tuple('zxwy')
        records = ((2, 2, 'a', False, False),
                   (30, 34, 'b', True, False),
                   (2, 95, 'c', False, False),
                   (30, 73, 'd', True, True))

        f = Frame.from_records(
                records, columns=columns, index=index,name='foo')

        self.assertTrue(tuple(reversed(f)) == tuple(reversed(columns)))


    def test_frame_sort_index_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('z', 'x', 'w', 'y'),
                name='foo')

        f2 = f1.sort_index()
        self.assertEqual(f2.to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 30), ('z', 2))), ('q', (('w', 95), ('x', 34), ('y', 73), ('z', 2))), ('r', (('w', 'c'), ('x', 'b'), ('y', 'd'), ('z', 'a'))), ('s', (('w', False), ('x', True), ('y', True), ('z', False))), ('t', (('w', False), ('x', False), ('y', True), ('z', False)))))
        self.assertEqual(f1.name, f2.name)

        self.assertEqual(f1.sort_index(ascending=False).to_pairs(0),
                (('p', (('z', 2), ('y', 30), ('x', 30), ('w', 2))), ('q', (('z', 2), ('y', 73), ('x', 34), ('w', 95))), ('r', (('z', 'a'), ('y', 'd'), ('x', 'b'), ('w', 'c'))), ('s', (('z', False), ('y', True), ('x', True), ('w', False))), ('t', (('z', False), ('y', True), ('x', False), ('w', False)))))


    def test_frame_sort_columns_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('t', 's', 'r', 'q', 'p'),
                index=('z', 'x', 'w', 'y'),
                name='foo')

        f2 = f1.sort_columns()
        self.assertEqual(
                f2.to_pairs(0),
                (('p', (('z', False), ('x', False), ('w', False), ('y', True))), ('q', (('z', False), ('x', True), ('w', False), ('y', True))), ('r', (('z', 'a'), ('x', 'b'), ('w', 'c'), ('y', 'd'))), ('s', (('z', 2), ('x', 34), ('w', 95), ('y', 73))), ('t', (('z', 2), ('x', 30), ('w', 2), ('y', 30)))))

        self.assertEqual(f2.name, f1.name)

    def test_frame_sort_values_a(self):
        # reindex both axis
        records = (
                (2, 2, 'c', False, False),
                (30, 34, 'd', True, False),
                (2, 95, 'a', False, False),
                (30, 73, 'b', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'r', 'q', 't', 's'),
                index=('z', 'x', 'w', 'y'),
                name='foo')

        post = f1.sort_values('q')
        self.assertEqual(post.name, f1.name)

        self.assertEqual(post.to_pairs(0),
                (('p', (('w', 2), ('y', 30), ('z', 2), ('x', 30))), ('r', (('w', 95), ('y', 73), ('z', 2), ('x', 34))), ('q', (('w', 'a'), ('y', 'b'), ('z', 'c'), ('x', 'd'))), ('t', (('w', False), ('y', True), ('z', False), ('x', True))), ('s', (('w', False), ('y', True), ('z', False), ('x', False)))))


        self.assertEqual(f1.sort_values('p').to_pairs(0),
                (('p', (('z', 2), ('w', 2), ('x', 30), ('y', 30))), ('r', (('z', 2), ('w', 95), ('x', 34), ('y', 73))), ('q', (('z', 'c'), ('w', 'a'), ('x', 'd'), ('y', 'b'))), ('t', (('z', False), ('w', False), ('x', True), ('y', True))), ('s', (('z', False), ('w', False), ('x', False), ('y', True))))
                )


    def test_frame_sort_values_b(self):
        # reindex both axis
        records = (
                (2, 2, 'c', False, False),
                (30, 34, 'd', True, False),
                (2, 95, 'a', True, False),
                (30, 73, 'b', False, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'r', 'q', 't', 's'),
                index=('z', 'x', 'w', 'y'))

        post = f1.sort_values(('p', 't'))

        self.assertEqual(post.to_pairs(0),
                (('p', (('z', 2), ('w', 2), ('y', 30), ('x', 30))), ('r', (('z', 2), ('w', 95), ('y', 73), ('x', 34))), ('q', (('z', 'c'), ('w', 'a'), ('y', 'b'), ('x', 'd'))), ('t', (('z', False), ('w', True), ('y', False), ('x', True))), ('s', (('z', False), ('w', False), ('y', True), ('x', False)))))



    def test_frame_sort_values_c(self):

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'),
                name='foo')

        f2 = f1.sort_values('y', axis=0)
        self.assertEqual(f2.to_pairs(0),
                (('r', (('w', 3.5), ('x', 60.2), ('y', 1.2), ('z', 50.2))), ('p', (('w', 2), ('x', 30), ('y', 2), ('z', 30))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73)))))

        self.assertEqual(f2.name, 'foo')


    def test_frame_relabel_a(self):
        # reindex both axis
        records = (
                (2, 2, 'c', False, False),
                (30, 34, 'd', True, False),
                (2, 95, 'a', False, False),
                (30, 73, 'b', True, True),
                )

        f1 = FrameGO.from_records(records,
                columns=('p', 'r', 'q', 't', 's'),
                index=('z', 'x', 'w', 'y'))

        f2 = f1.relabel(columns={'q': 'QQQ'})

        self.assertEqual(f2.to_pairs(0),
                (('p', (('z', 2), ('x', 30), ('w', 2), ('y', 30))), ('r', (('z', 2), ('x', 34), ('w', 95), ('y', 73))), ('QQQ', (('z', 'c'), ('x', 'd'), ('w', 'a'), ('y', 'b'))), ('t', (('z', False), ('x', True), ('w', False), ('y', True))), ('s', (('z', False), ('x', False), ('w', False), ('y', True))))
                )

        f3 = f1.relabel(index={'y': 'YYY'})

        self.assertEqual(f3.to_pairs(0),
                (('p', (('z', 2), ('x', 30), ('w', 2), ('YYY', 30))), ('r', (('z', 2), ('x', 34), ('w', 95), ('YYY', 73))), ('q', (('z', 'c'), ('x', 'd'), ('w', 'a'), ('YYY', 'b'))), ('t', (('z', False), ('x', True), ('w', False), ('YYY', True))), ('s', (('z', False), ('x', False), ('w', False), ('YYY', True)))))

        self.assertTrue((f1.mloc == f2.mloc).all())
        self.assertTrue((f2.mloc == f3.mloc).all())


    def test_frame_get_a(self):
        # reindex both axis
        records = (
                (2, 2, 'c', False, False),
                (30, 34, 'd', True, False),
                (2, 95, 'a', False, False),
                (30, 73, 'b', True, True),
                )

        f1 = FrameGO.from_records(records,
                columns=('p', 'r', 'q', 't', 's'),
                index=('z', 'x', 'w', 'y'))

        self.assertEqual(f1.get('r').values.tolist(),
                [2, 34, 95, 73])

        self.assertEqual(f1.get('a'), None)
        self.assertEqual(f1.get('w'), None)
        self.assertEqual(f1.get('a', -1), -1)

    def test_frame_isna_a(self):
        f1 = FrameGO([
                [np.nan, 2, np.nan, 0],
                [3, 4, np.nan, 1],
                [np.nan, np.nan, np.nan, 5]],
                columns=list('ABCD'))

        self.assertEqual(f1.isna().to_pairs(0),
                (('A', ((0, True), (1, False), (2, True))), ('B', ((0, False), (1, False), (2, True))), ('C', ((0, True), (1, True), (2, True))), ('D', ((0, False), (1, False), (2, False)))))

        self.assertEqual(f1.notna().to_pairs(0),
                (('A', ((0, False), (1, True), (2, False))), ('B', ((0, True), (1, True), (2, False))), ('C', ((0, False), (1, False), (2, False))), ('D', ((0, True), (1, True), (2, True)))))

    def test_frame_dropna_a(self):
        f1 = FrameGO([
                [np.nan, 2, np.nan, 0],
                [3, 4, np.nan, 1],
                [np.nan, np.nan, np.nan, np.nan]],
                columns=list('ABCD'))

        self.assertAlmostEqualFramePairs(
                f1.dropna(axis=0, condition=np.all).to_pairs(0),
                (('A', ((0, nan), (1, 3.0))), ('B', ((0, 2.0), (1, 4.0))), ('C', ((0, nan), (1, nan))), ('D', ((0, 0.0), (1, 1.0)))))

        self.assertAlmostEqualFramePairs(
                f1.dropna(axis=1, condition=np.all).to_pairs(0),
                (('A', ((0, nan), (1, 3.0), (2, nan))), ('B', ((0, 2.0), (1, 4.0), (2, nan))), ('D', ((0, 0.0), (1, 1.0), (2, nan)))))


        f2 = f1.dropna(axis=0, condition=np.any)
        # dropping to zero results in an empty DF in the same manner as Pandas; not sure if this is correct or ideal
        self.assertEqual(f2.shape, (0, 4))

        f3 = f1.dropna(axis=1, condition=np.any)
        self.assertEqual(f3.shape, (3, 0))

    def test_frame_dropna_b(self):
        f1 = FrameGO([
                [np.nan, 2, 3, 0],
                [3, 4, np.nan, 1],
                [0, 1, 2, 3]],
                columns=list('ABCD'))

        self.assertEqual(f1.dropna(axis=0, condition=np.any).to_pairs(0),
                (('A', ((2, 0.0),)), ('B', ((2, 1.0),)), ('C', ((2, 2.0),)), ('D', ((2, 3.0),))))
        self.assertEqual(f1.dropna(axis=1, condition=np.any).to_pairs(0),
                (('B', ((0, 2.0), (1, 4.0), (2, 1.0))), ('D', ((0, 0.0), (1, 1.0), (2, 3.0)))))

    def test_frame_dropna_c(self):
        f1 = Frame([
                [np.nan, np.nan],
                [np.nan, np.nan],],
                columns=list('AB'))
        f2 = f1.dropna()
        self.assertEqual(f2.shape, (0, 2))



    def test_frame_fillna_a(self):
        dtype = np.dtype

        f1 = FrameGO([
                [np.nan, 2, 3, 0],
                [3, 4, np.nan, 1],
                [0, 1, 2, 3]],
                columns=list('ABCD'))

        f2 = f1.fillna(0)
        self.assertEqual(f2.to_pairs(0),
                (('A', ((0, 0.0), (1, 3.0), (2, 0.0))), ('B', ((0, 2.0), (1, 4.0), (2, 1.0))), ('C', ((0, 3.0), (1, 0.0), (2, 2.0))), ('D', ((0, 0.0), (1, 1.0), (2, 3.0)))))

        post = f2.dtypes
        self.assertEqual(post.to_pairs(),
                (('A', dtype('float64')), ('B', dtype('float64')), ('C', dtype('float64')), ('D', dtype('float64'))))

        f3 = f1.fillna(None)
        self.assertEqual(f3.to_pairs(0),
                (('A', ((0, None), (1, 3.0), (2, 0.0))), ('B', ((0, 2.0), (1, 4.0), (2, 1.0))), ('C', ((0, 3.0), (1, None), (2, 2.0))), ('D', ((0, 0.0), (1, 1.0), (2, 3.0)))))

        post = f3.dtypes
        self.assertEqual(post.to_pairs(),
                (('A', dtype('O')), ('B', dtype('O')), ('C', dtype('O')), ('D', dtype('O'))))



    def test_frame_fillna_leading_a(self):
        a2 = np.array([
                [None, None, None, None],
                [None, 1, None, 6],
                [None, 5, None, None]
                ], dtype=object)
        a1 = np.array([None, None, None], dtype=object)
        a3 = np.array([
                [None, 4],
                [None, 1],
                [None, 5]
                ], dtype=object)
        tb1 = TypeBlocks.from_blocks((a1, a2, a3))

        f1 = Frame(tb1,
                index=self.get_letters(None, tb1.shape[0]),
                columns=self.get_letters(-tb1.shape[1], None)
                )

        self.assertEqual(f1.fillna_leading(0, axis=0).to_pairs(0),
                (('t', (('a', 0), ('b', 0), ('c', 0))), ('u', (('a', 0), ('b', 0), ('c', 0))), ('v', (('a', 0), ('b', 1), ('c', 5))), ('w', (('a', 0), ('b', 0), ('c', 0))), ('x', (('a', 0), ('b', 6), ('c', None))), ('y', (('a', 0), ('b', 0), ('c', 0))), ('z', (('a', 4), ('b', 1), ('c', 5)))))

        self.assertEqual(f1.fillna_leading(0, axis=1).to_pairs(0),
                (('t', (('a', 0), ('b', 0), ('c', 0))), ('u', (('a', 0), ('b', 0), ('c', 0))), ('v', (('a', 0), ('b', 1), ('c', 5))), ('w', (('a', 0), ('b', None), ('c', None))), ('x', (('a', 0), ('b', 6), ('c', None))), ('y', (('a', 0), ('b', None), ('c', None))), ('z', (('a', 4), ('b', 1), ('c', 5)))))


    def test_frame_empty_a(self):

        f1 = FrameGO(index=('a', 'b', 'c'))
        f1['w'] = Series.from_items(zip('cebga', (10, 20, 30, 40, 50)))
        f1['x'] = Series.from_items(zip('abc', range(3, 6)))
        f1['y'] = Series.from_items(zip('abcd', range(2, 6)))
        f1['z'] = Series.from_items(zip('qabc', range(7, 11)))

        self.assertEqual(f1.to_pairs(0),
                (('w', (('a', 50), ('b', 30), ('c', 10))), ('x', (('a', 3), ('b', 4), ('c', 5))), ('y', (('a', 2), ('b', 3), ('c', 4))), ('z', (('a', 8), ('b', 9), ('c', 10)))))


    @skip_win
    def test_frame_from_csv_a(self):
        # header, mixed types, no index

        s1 = StringIO('count,score,color\n1,1.3,red\n3,5.2,green\n100,3.4,blue\n4,9.0,black')

        f1 = Frame.from_csv(s1)
        post = f1.iloc[:, :2].sum(axis=0)
        self.assertEqual(post.to_pairs(),
                (('count', 108.0), ('score', 18.9)))
        self.assertEqual(f1.shape, (4, 3))

        self.assertEqual(f1.dtypes.iter_element().apply(str).to_pairs(),
                (('count', 'int64'), ('score', 'float64'), ('color', '<U5')))


        s2 = StringIO('color,count,score\nred,1,1.3\ngreen,3,5.2\nblue,100,3.4\nblack,4,9.0')

        f2 = Frame.from_csv(s2)
        self.assertEqual(f2['count':].sum().to_pairs(),
                (('count', 108.0), ('score', 18.9)))
        self.assertEqual(f2.shape, (4, 3))
        self.assertEqual(f2.dtypes.iter_element().apply(str).to_pairs(),
                (('color', '<U5'), ('count', 'int64'), ('score', 'float64')))


        # add junk at beginning and end
        s3 = StringIO('junk\ncolor,count,score\nred,1,1.3\ngreen,3,5.2\nblue,100,3.4\nblack,4,9.0\njunk')

        f3 = Frame.from_csv(s3, skip_header=1, skip_footer=1)
        self.assertEqual(f3.shape, (4, 3))
        self.assertEqual(f3.dtypes.iter_element().apply(str).to_pairs(),
                (('color', '<U5'), ('count', 'int64'), ('score', 'float64')))



    def test_frame_from_csv_b(self):
        filelike = StringIO('''count,number,weight,scalar,color,active
0,4,234.5,5.3,'red',False
30,50,9.234,5.434,'blue',True''')
        f1 = Frame.from_csv(filelike)

        self.assertEqual(f1.columns.values.tolist(),
                ['count', 'number', 'weight', 'scalar', 'color', 'active'])


    def test_frame_from_csv_c(self):

        s1 = StringIO('color,count,score\nred,1,1.3\ngreen,3,5.2\nblue,100,3.4\nblack,4,9.0')
        f1 = Frame.from_csv(s1, index_column='color')
        self.assertEqual(f1.to_pairs(0),
                (('count', (('red', 1), ('green', 3), ('blue', 100), ('black', 4))), ('score', (('red', 1.3), ('green', 5.2), ('blue', 3.4), ('black', 9.0)))))


    def test_frame_to_csv_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        file = StringIO()
        f1.to_csv(file)
        file.seek(0)
        self.assertEqual(file.read(),
'index,p,q,r,s,t\nw,2,2,a,False,False\nx,30,34,b,True,False\ny,2,95,c,False,False\nz,30,73,d,True,True')

        file = StringIO()
        f1.to_csv(file, include_index=False)
        file.seek(0)
        self.assertEqual(file.read(),
'p,q,r,s,t\n2,2,a,False,False\n30,34,b,True,False\n2,95,c,False,False\n30,73,d,True,True')

        file = StringIO()
        f1.to_csv(file, include_index=False, include_columns=False)
        file.seek(0)
        self.assertEqual(file.read(),
'2,2,a,False,False\n30,34,b,True,False\n2,95,c,False,False\n30,73,d,True,True')


    def test_frame_to_csv_b(self):

        f = sf.Frame([1, 2, 3],
                columns=['a'],
                index=sf.Index(range(3), name='Important Name'))
        file = StringIO()
        f.to_csv(file)
        file.seek(0)
        self.assertEqual(file.read(), 'Important Name,a\n0,1\n1,2\n2,3')

    def test_frame_to_tsv_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        file = StringIO()
        f1.to_tsv(file)
        file.seek(0)
        self.assertEqual(file.read(),
'index\tp\tq\tr\ts\tt\nw\t2\t2\ta\tFalse\tFalse\nx\t30\t34\tb\tTrue\tFalse\ny\t2\t95\tc\tFalse\tFalse\nz\t30\t73\td\tTrue\tTrue')


    def test_frame_to_html_a(self):
        records = (
                (2, 'a', False),
                (3, 'b', False),
                )
        f1 = Frame.from_records(records,
                columns=('r', 's', 't'),
                index=('w', 'x'))
        post = f1.to_html()
        self.assertEqual(post, '<table border="1"><thead><tr><th><span style="color: #777777">&lt;Frame&gt;</span></th><th></th><th></th><th></th></tr><tr><th><span style="color: #777777">&lt;Index&gt;</span></th><th>r</th><th>s</th><th>t</th></tr><tr><th><span style="color: #777777">&lt;Index&gt;</span></th><th></th><th></th><th></th></tr></thead><tbody><tr><th>w</th><td>2</td><td>a</td><td>False</td></tr><tr><th>x</th><td>3</td><td>b</td><td>False</td></tr></tbody></table>'
        )


    def test_frame_to_html_datatables_a(self):
        records = (
                (2, 'a', False),
                (3, 'b', False),
                )
        f1 = Frame.from_records(records,
                columns=('r', 's', 't'),
                index=('w', 'x'))

        sio = StringIO()

        post = f1.to_html_datatables(sio, show=False)

        self.assertEqual(post, None)

        self.assertTrue(len(sio.read()) > 1600)



    def test_frame_and_a(self):

        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))
        f2 = FrameGO([
                [np.nan, 2, 3, 0],
                [3, 4, np.nan, 1],
                [0, 1, 2, 3]],
                columns=list('ABCD'))

        self.assertEqual(f1.all(axis=0).to_pairs(),
                (('p', True), ('q', True), ('r', True), ('s', False), ('t', False)))

        self.assertEqual(f1.any(axis=0).to_pairs(),
                (('p', True), ('q', True), ('r', True), ('s', True), ('t', True)))

        self.assertEqual(f1.all(axis=1).to_pairs(),
                (('w', False), ('x', False), ('y', False), ('z', True)))

        self.assertEqual(f1.any(axis=1).to_pairs(),
                (('w', True), ('x', True), ('y', True), ('z', True)))



    def test_frame_unique_a(self):

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.unique().tolist(),
                [1.2, 2.0, 3.5, 30.0, 34.0, 50.2, 60.2, 73.0, 95.0])

        records = (
                (2, 2, 2),
                (30, 34, 34),
                (2, 2, 2),
                (30, 73, 73),
                )
        f2 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f2.unique().tolist(), [2, 30, 34, 73])

        self.assertEqual(f2.unique(axis=0).tolist(),
                [[2, 2, 2], [30, 34, 34], [30, 73, 73]])
        self.assertEqual(f2.unique(axis=1).tolist(),
                [[2, 2], [30, 34], [2, 2], [30, 73]])

    def test_frame_unique_b(self):

        records = (
                (None, 2, None),
                ('30', 34, '30'),
                (None, 2, None),
                ('30', 34, '30'),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(len(f1.unique()), 4)

        self.assertEqual(len(f1.unique(axis=0)), 2)

        self.assertEqual(len(f1.unique(axis=1)), 2)


    def test_frame_duplicated_a(self):

        a1 = np.array([[50, 50, 32, 17, 17], [2,2,1,3,3]])
        f1 = Frame(a1, index=('a', 'b'), columns=('p', 'q', 'r', 's','t'))

        self.assertEqual(f1.duplicated(axis=1).to_pairs(),
                (('p', True), ('q', True), ('r', False), ('s', True), ('t', True)))

        self.assertEqual(f1.duplicated(axis=0).to_pairs(),
                (('a', False), ('b', False)))


    def test_frame_duplicated_b(self):

        a1 = np.array([[50, 50, 32, 17, 17], [2,2,1,3,3]])
        f1 = Frame(a1, index=('a', 'b'), columns=('p', 'q', 'r', 's','t'))

        self.assertEqual(f1.drop_duplicated(axis=1, exclude_first=True).to_pairs(1),
                (('a', (('p', 50), ('r', 32), ('s', 17))), ('b', (('p', 2), ('r', 1), ('s', 3)))))

    def test_frame_from_concat_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'a'))

        records = (
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f2 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'a'))

        records = (
                (2, 2, 'a', False, False),
                (30, 73, 'd', True, True),
                )

        f3 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'a'))

        f = Frame.from_concat((f1, f2, f3), axis=1, columns=range(15))

        # no blocks are copied or reallcoated
        self.assertEqual(f.mloc.tolist(),
                f1.mloc.tolist() + f2.mloc.tolist() + f3.mloc.tolist()
                )
        # order of index is retained
        self.assertEqual(f.to_pairs(1),
                (('x', ((0, 2), (1, 2), (2, 'a'), (3, False), (4, False), (5, 2), (6, 95), (7, 'c'), (8, False), (9, False), (10, 2), (11, 2), (12, 'a'), (13, False), (14, False))), ('a', ((0, 30), (1, 34), (2, 'b'), (3, True), (4, False), (5, 30), (6, 73), (7, 'd'), (8, True), (9, True), (10, 30), (11, 73), (12, 'd'), (13, True), (14, True)))))


    def test_frame_from_concat_b(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'a'))

        records = (
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f2 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'b'))

        records = (
                (2, 2, 'a', False, False),
                (30, 73, 'd', True, True),
                )

        f3 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'c'))

        f = Frame.from_concat((f1, f2, f3), axis=1, columns=range(15))

        self.assertEqual(f.index.values.tolist(),
                ['a', 'b', 'c', 'x'])

        self.assertAlmostEqualFramePairs(f.to_pairs(1),
                (('a', ((0, 30), (1, 34), (2, 'b'), (3, True), (4, False), (5, nan), (6, nan), (7, nan), (8, nan), (9, nan), (10, nan), (11, nan), (12, nan), (13, nan), (14, nan))), ('b', ((0, nan), (1, nan), (2, nan), (3, nan), (4, nan), (5, 30), (6, 73), (7, 'd'), (8, True), (9, True), (10, nan), (11, nan), (12, nan), (13, nan), (14, nan))), ('c', ((0, nan), (1, nan), (2, nan), (3, nan), (4, nan), (5, nan), (6, nan), (7, nan), (8, nan), (9, nan), (10, 30), (11, 73), (12, 'd'), (13, True), (14, True))), ('x', ((0, 2), (1, 2), (2, 'a'), (3, False), (4, False), (5, 2), (6, 95), (7, 'c'), (8, False), (9, False), (10, 2), (11, 2), (12, 'a'), (13, False), (14, False))))
                )


        f = Frame.from_concat((f1, f2, f3), union=False, axis=1, columns=range(15))

        self.assertEqual(f.index.values.tolist(),
                ['x'])
        self.assertEqual(f.to_pairs(0),
                ((0, (('x', 2),)), (1, (('x', 2),)), (2, (('x', 'a'),)), (3, (('x', False),)), (4, (('x', False),)), (5, (('x', 2),)), (6, (('x', 95),)), (7, (('x', 'c'),)), (8, (('x', False),)), (9, (('x', False),)), (10, (('x', 2),)), (11, (('x', 2),)), (12, (('x', 'a'),)), (13, (('x', False),)), (14, (('x', False),))))


    def test_frame_from_concat_c(self):
        records = (
                (2, 2, False),
                (30, 34, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 't'),
                index=('x', 'a'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=('r', 's',),
                index=('x', 'a'))

        # get combined columns as they are unique
        f = Frame.from_concat((f1, f2), axis=1)
        self.assertEqual(f.to_pairs(0),
                (('p', (('x', 2), ('a', 30))), ('q', (('x', 2), ('a', 34))), ('t', (('x', False), ('a', False))), ('r', (('x', 'c'), ('a', 'd'))), ('s', (('x', False), ('a', True))))
                )


    @skip_win
    def test_frame_from_concat_d(self):
        records = (
                (2, 2, False),
                (30, 34, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('a', 'b'))

        records = (
                (2, 2, False),
                (30, 34, False),
                )

        f2 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('c', 'd'))

        f = Frame.from_concat((f1, f2), axis=0)

        # block copmatible will result in attempt to keep vertical types
        self.assertEqual(
                [str(x) for x in f.dtypes.values.tolist()],
                ['int64', 'int64', 'bool'])

        self.assertEqual(f.to_pairs(0),
                (('p', (('a', 2), ('b', 30), ('c', 2), ('d', 30))), ('q', (('a', 2), ('b', 34), ('c', 2), ('d', 34))), ('r', (('a', False), ('b', False), ('c', False), ('d', False)))))


    @skip_win
    def test_frame_from_concat_e(self):

        f1 = Frame.from_items(zip(
                ('a', 'b', 'c'),
                ((1, 2), (1, 2), (False, True))
                ))

        f = Frame.from_concat((f1, f1, f1), index=range(6))
        self.assertEqual(
                f.to_pairs(0),
                (('a', ((0, 1), (1, 2), (2, 1), (3, 2), (4, 1), (5, 2))), ('b', ((0, 1), (1, 2), (2, 1), (3, 2), (4, 1), (5, 2))), ('c', ((0, False), (1, True), (2, False), (3, True), (4, False), (5, True)))))
        self.assertEqual(
                [str(x) for x in f.dtypes.values.tolist()],
                ['int64', 'int64', 'bool'])

        f = Frame.from_concat((f1, f1, f1), axis=1, columns=range(9))

        self.assertEqual(f.to_pairs(0),
                ((0, ((0, 1), (1, 2))), (1, ((0, 1), (1, 2))), (2, ((0, False), (1, True))), (3, ((0, 1), (1, 2))), (4, ((0, 1), (1, 2))), (5, ((0, False), (1, True))), (6, ((0, 1), (1, 2))), (7, ((0, 1), (1, 2))), (8, ((0, False), (1, True)))))

        self.assertEqual([str(x) for x in f.dtypes.values.tolist()],
                ['int64', 'int64', 'bool', 'int64', 'int64', 'bool', 'int64', 'int64', 'bool'])

    def test_frame_from_concat_f(self):
        # force a reblock before concatenating

        a1 = np.array([1, 2, 3], dtype=np.int64)
        a2 = np.array([10,50,30], dtype=np.int64)
        a3 = np.array([1345,2234,3345], dtype=np.int64)
        a4 = np.array([False, True, False])
        a5 = np.array([False, False, False])
        a6 = np.array(['g', 'd', 'e'])
        tb1 = TypeBlocks.from_blocks((a1, a2, a3, a4, a5, a6))

        f1 = Frame(TypeBlocks.from_blocks((a1, a2, a3, a4, a5, a6)),
                columns = ('a', 'b', 'c', 'd', 'e', 'f'),
                own_data=True)
        self.assertEqual(len(f1._blocks._blocks), 6)

        f2 = Frame(f1.iloc[1:]._blocks.consolidate(),
                columns = ('a', 'b', 'c', 'd', 'e', 'f'),
                own_data=True)
        self.assertEqual(len(f2._blocks._blocks), 3)

        f = Frame.from_concat((f1 ,f2), index=range(5))

        self.assertEqual(
                [str(x) for x in f.dtypes.values.tolist()],
                ['int64', 'int64', 'int64', 'bool', 'bool', '<U1'])

        self.assertEqual(
                [str(x.dtype) for x in f._blocks._blocks],
                ['int64', 'bool', '<U1'])


    def test_frame_from_concat_g(self):
        records = (
                (2, 2, False),
                (30, 34, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 't'),
                index=('x', 'a'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=('r', 's',),
                index=('x', 'a'))

        # get combined columns as they are unique
        f = Frame.from_concat((f1, f2), axis=1)
        self.assertEqual(f.to_pairs(0),
                (('p', (('x', 2), ('a', 30))), ('q', (('x', 2), ('a', 34))), ('t', (('x', False), ('a', False))), ('r', (('x', 'c'), ('a', 'd'))), ('s', (('x', False), ('a', True))))
                )


    def test_frame_from_concat_h(self):

        index = list(''.join(x) for x in it.combinations(string.ascii_lowercase, 3))
        columns = list(''.join(x) for x in it.combinations(string.ascii_uppercase, 2))
        data = np.random.rand(len(index), len(columns))
        f1 = Frame(data, index=index, columns=columns)

        f2 = f1[[c for c in f1.columns if c.startswith('D')]]
        f3 = f1[[c for c in f1.columns if c.startswith('G')]]
        post = sf.Frame.from_concat((f2, f3), axis=1)

        # this form of concatenation has no copy
        assert post.mloc.tolist() == [f2.mloc[0], f3.mloc[0]]
        self.assertEqual(post.shape, (2600, 41))


    def test_frame_from_concat_i(self):

        sf1 = sf.Frame.from_dict(dict(a=[1,2,3],b=[1,2,3]),index=[100,200,300]).reindex_add_level(columns='A')
        sf2 = sf.Frame.from_dict(dict(a=[1,2,3],b=[1,2,3]),index=[100,200,300]).reindex_add_level(columns='B')

        f = sf.Frame.from_concat((sf1, sf2), axis=1)
        self.assertEqual(f.to_pairs(0),
                ((('A', 'a'), ((100, 1), (200, 2), (300, 3))), (('A', 'b'), ((100, 1), (200, 2), (300, 3))), (('B', 'a'), ((100, 1), (200, 2), (300, 3))), (('B', 'b'), ((100, 1), (200, 2), (300, 3)))))


    def test_frame_from_concat_j(self):

        sf1 = sf.Frame.from_dict(dict(a=[1,2,3],b=[1,2,3]),index=[100,200,300]).reindex_add_level(index='A')
        sf2 = sf.Frame.from_dict(dict(a=[1,2,3],b=[1,2,3]),index=[100,200,300]).reindex_add_level(index='B')

        f = sf.Frame.from_concat((sf1, sf2), axis=0)

        self.assertEqual(f.to_pairs(0),
                (('a', ((('A', 100), 1), (('A', 200), 2), (('A', 300), 3), (('B', 100), 1), (('B', 200), 2), (('B', 300), 3))), ('b', ((('A', 100), 1), (('A', 200), 2), (('A', 300), 3), (('B', 100), 1), (('B', 200), 2), (('B', 300), 3))))
                )


    def test_frame_from_concat_k(self):
        records = (
                (2, 2, False),
                (30, 34, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 't'),
                index=('x', 'a'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=('r', 's',),
                index=('x', 'a'))

        # get combined columns as they are unique
        f = Frame.from_concat((f1, f2), axis=1, name='foo')
        self.assertEqual(f.name, 'foo')


    def test_frame_from_concat_m(self):
        records = (
                (2, 2, False),
                (30, 34, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 't'),
                index=('x', 'a'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=(3, 4,),
                index=('x', 'a'))

        f = Frame.from_concat((f1, f2), axis=1, name='foo')

        self.assertEqual(f.columns.values.tolist(),
                ['p', 'q', 't', 3, 4])
        self.assertEqual(f.to_pairs(0),
                (('p', (('x', 2), ('a', 30))), ('q', (('x', 2), ('a', 34))), ('t', (('x', False), ('a', False))), (3, (('x', 'c'), ('a', 'd'))), (4, (('x', False), ('a', True))))
                )

    def test_frame_from_concat_n(self):
        records = (
                (2, False),
                (30, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q'),
                index=('x', 'a'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=('p', 'q'),
                index=(3, 10))

        f = Frame.from_concat((f1, f2), axis=0, name='foo')

        self.assertEqual(f.index.values.tolist(),
                ['x', 'a', 3, 10])
        self.assertEqual(f.to_pairs(0),
                (('p', (('x', 2), ('a', 30), (3, 'c'), (10, 'd'))), ('q', (('x', False), ('a', False), (3, False), (10, True))))
                )


    def test_frame_from_concat_o(self):
        records = (
                (2, False),
                (34, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q',),
                index=('x', 'z'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=('r', 's',),
                index=('x', 'z'))


        s1 = Series((0, 100), index=('x', 'z'), name='t')

        f = Frame.from_concat((f1, f2, s1), axis=1)

        self.assertEqual(f.to_pairs(0),
                (('p', (('x', 2), ('z', 34))), ('q', (('x', False), ('z', False))), ('r', (('x', 'c'), ('z', 'd'))), ('s', (('x', False), ('z', True))), ('t', (('x', 0), ('z', 100))))
                )



    def test_frame_from_concat_p(self):
        records = (
                (2, False),
                (34, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q',),
                index=('a', 'b'))

        s1 = Series((0, True), index=('p', 'q'), name='c', dtype=object)
        s2 = Series((-2, False), index=('p', 'q'), name='d', dtype=object)

        f = Frame.from_concat((s2, f1, s1), axis=0)

        self.assertEqual(f.to_pairs(0),
                (('p', (('d', -2), ('a', 2), ('b', 34), ('c', 0))), ('q', (('d', False), ('a', False), ('b', False), ('c', True)))))



    def test_frame_from_concat_q(self):
        s1 = Series((2, 3, 0,), index=list('abc'), name='x').reindex_add_level('i')
        s2 = Series(('10', '20', '100'), index=list('abc'), name='y').reindex_add_level('i')

        # stack horizontally
        f = Frame.from_concat((s1, s2), axis=1)

        self.assertEqual(f.to_pairs(0),
                (('x', ((('i', 'a'), 2), (('i', 'b'), 3), (('i', 'c'), 0))), ('y', ((('i', 'a'), '10'), (('i', 'b'), '20'), (('i', 'c'), '100'))))
            )

        # stack vertically
        f = Frame.from_concat((s1, s2), axis=0)
        self.assertEqual(f.to_pairs(0),
                ((('i', 'a'), (('x', 2), ('y', '10'))), (('i', 'b'), (('x', 3), ('y', '20'))), (('i', 'c'), (('x', 0), ('y', '100'))))
            )


    def test_frame_from_concat_r(self):
        f1 = sf.Frame.from_records(
                [dict(a=1,b=1),dict(a=2,b=3),dict(a=1,b=1),dict(a=2,b=3)],
                index=sf.IndexHierarchy.from_labels([(1,'dd'),(1,'bb'),(2,'cc'),(2,'dd')]))

        f2 = sf.Frame.from_records(
                [dict(a=1,b=1),dict(a=2,b=3),dict(a=1,b=1),dict(a=2,b=3)],
                index=sf.IndexHierarchy.from_labels([(3,'ddd'),(3,'bbb'),(4,'ccc'),(4,'ddd')])) * 100

        self.assertEqual(Frame.from_concat((f1, f2), axis=0).to_pairs(0),
                (('a', (((1, 'dd'), 1), ((1, 'bb'), 2), ((2, 'cc'), 1), ((2, 'dd'), 2), ((3, 'ddd'), 100), ((3, 'bbb'), 200), ((4, 'ccc'), 100), ((4, 'ddd'), 200))), ('b', (((1, 'dd'), 1), ((1, 'bb'), 3), ((2, 'cc'), 1), ((2, 'dd'), 3), ((3, 'ddd'), 100), ((3, 'bbb'), 300), ((4, 'ccc'), 100), ((4, 'ddd'), 300))))
                )

    def test_frame_from_concat_s(self):
        records = (
                (2, False),
                (34, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q',),
                index=('x', 'z'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=('r', 's',),
                index=('x', 'z'))

        with self.assertRaises(NotImplementedError):
            f = Frame.from_concat((f1, f2), axis=None)


    def test_frame_from_concat_t(self):
        frame1 = sf.Frame.from_records(
                [dict(a=1,b=1), dict(a=2,b=3), dict(a=1,b=1), dict(a=2,b=3)], index=sf.IndexHierarchy.from_labels([(1,'dd',0), (1,'bb',0), (2,'cc',0), (2,'ee',0)]))
        frame2 = sf.Frame.from_records(
                [dict(a=100,b=200), dict(a=20,b=30), dict(a=101,b=101), dict(a=201,b=301)], index=sf.IndexHierarchy.from_labels([(1,'ddd',0), (1,'bbb',0), (2,'ccc',0), (2,'eee',0)]))

        # produce invalid index labels into an IndexHierarchy constructor
        with self.assertRaises(RuntimeError):
            sf.Frame.from_concat((frame1, frame2))


    def test_frame_from_concat_u(self):
        # this fails; figure out why
        a = sf.Series(('a', 'b', 'c'), index=range(3, 6))
        f = sf.Frame.from_concat((
                a,
                sf.Series(a.index.values, index=a.index)),
                axis=0,
                columns=(3, 4, 5), index=(1,2))

        self.assertEqual(f.to_pairs(0),
                ((3, ((1, 'a'), (2, 3))), (4, ((1, 'b'), (2, 4))), (5, ((1, 'c'), (2, 5))))
                )

    def test_frame_set_index_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'y'),
                consolidate_blocks=True)

        self.assertEqual(f1.set_index('r').to_pairs(0),
                (('p', (('a', 2), ('b', 30))), ('q', (('a', 2), ('b', 34))), ('r', (('a', 'a'), ('b', 'b'))), ('s', (('a', False), ('b', True))), ('t', (('a', False), ('b', False)))))

        self.assertEqual(f1.set_index('r', drop=True).to_pairs(0),
                (('p', (('a', 2), ('b', 30))), ('q', (('a', 2), ('b', 34))), ('s', (('a', False), ('b', True))), ('t', (('a', False), ('b', False)
                ))))

        f2 = f1.set_index('r', drop=True)

        self.assertEqual(f2.to_pairs(0),
                (('p', (('a', 2), ('b', 30))), ('q', (('a', 2), ('b', 34))), ('s', (('a', False), ('b', True))), ('t', (('a', False), ('b', False))))
                )

        self.assertTrue(f1.mloc[[0, 2]].tolist() == f2.mloc.tolist())


    def test_frame_set_index_b(self):
        records = (
                (2, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'y'),
                consolidate_blocks=True)

        for col in f1.columns:
            f2 = f1.set_index(col)
            self.assertEqual(f2.index.name, col)


    def test_frame_set_index_c(self):
        records = (
                (2, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                )

    def test_frame_set_index_d(self):

        for arrays in self.get_arrays_a():
            tb1 = TypeBlocks.from_blocks(arrays)

            f1 = FrameGO(tb1)
            f1[tb1.shape[1]] = range(tb1.shape[0])

            for i in range(f1.shape[1]):
                f2 = f1.set_index(i, drop=True)
                self.assertTrue(f2.shape == (3, f1.shape[1] - 1))


    def test_frame_head_tail_a(self):

        # thest of multi threaded apply

        f1 = Frame.from_items(
                zip(range(10), (np.random.rand(1000) for _ in range(10)))
                )
        self.assertEqual(f1.head(3).index.values.tolist(),
                [0, 1, 2])
        self.assertEqual(f1.tail(3).index.values.tolist(),
                [997, 998, 999])


    def test_frame_from_records_date_a(self):

        d = np.datetime64

        records = (
                (d('2018-01-02'), d('2018-01-02'), 'a', False, False),
                (d('2017-01-02'), d('2017-01-02'), 'b', True, False),
                (d('2016-01-02'), d('2016-01-02'), 'c', False, False),
                (d('2015-01-02'), d('2015-01-02'), 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=None)

        dtype = np.dtype

        self.assertEqual(list(f1._blocks._reblock_signature()),
                [(dtype('<M8[D]'), 2), (dtype('<U1'), 1), (dtype('bool'), 2)])


    def test_frame_from_records_a(self):

        NT = namedtuple('Sample', ('a', 'b', 'c'))
        records = [NT(x, x, x) for x in range(4)]
        f1 = Frame.from_records(records)
        self.assertEqual(f1.columns.values.tolist(), ['a', 'b', 'c'])
        self.assertEqual(f1.sum().to_pairs(),
                (('a', 6), ('b', 6), ('c', 6)))

    def test_frame_from_records_b(self):

        records = [{'a':x, 'b':x, 'c':x} for x in range(4)]
        f1 = Frame.from_records(records)
        self.assertEqual(f1.columns.values.tolist(), ['a', 'b', 'c'])
        self.assertEqual(f1.sum().to_pairs(),
                (('a', 6), ('b', 6), ('c', 6)))


    def test_frame_from_records_c(self):

        f1 = sf.Frame.from_records([[1, 2], [2, 3]], columns=['a', 'b'])
        self.assertEqual(f1.to_pairs(0),
                (('a', ((0, 1), (1, 2))), ('b', ((0, 2), (1, 3)))))

        with self.assertRaises(Exception):
            f2 = sf.Frame.from_records([[1, 2], [2, 3]], columns=['a'])


    def test_frame_from_records_d(self):

        s1 = Series([3, 4, 5], index=('x', 'y', 'z'))
        s2 = Series(list('xyz'), index=('x', 'y', 'z'))

        with self.assertRaises(Exception):
            # cannot use Series in from_records
            f1 = sf.Frame.from_records([s1, s2], columns=['a', 'b', 'c'])


    def test_frame_from_records_e(self):

        a1 = np.array([[1,2,3], [4,5,6]])

        f1 = sf.Frame.from_records(a1, index=('x', 'y'), columns=['a', 'b', 'c'])

        self.assertEqual(f1.to_pairs(0),
                (('a', (('x', 1), ('y', 4))), ('b', (('x', 2), ('y', 5))), ('c', (('x', 3), ('y', 6)))))


    def test_frame_from_records_f(self):

        records = [[1,'2',3], [4,'5',6]]
        dtypes = (np.int64, str, str)
        f1 = sf.Frame.from_records(records,
                index=('x', 'y'),
                columns=['a', 'b', 'c'],
                dtypes=dtypes)
        self.assertEqual(f1.dtypes.iter_element().apply(str).to_pairs(),
                (('a', 'int64'), ('b', '<U1'), ('c', '<U1'))
                )

    def test_frame_from_records_g(self):

        records = [[1,'2',3], [4,'5',6]]
        dtypes = {'b': np.int64}
        f1 = sf.Frame.from_records(records,
                index=('x', 'y'),
                columns=['a', 'b', 'c'],
                dtypes=dtypes)

        self.assertEqual(str(f1.dtypes['b']), 'int64')


    def test_frame_from_records_h(self):

        NT = namedtuple('NT', ('a', 'b', 'c'))

        records = [NT(1,'2',3), NT(4,'5',6)]
        dtypes = {'b': np.int64}
        f1 = sf.Frame.from_records(records, dtypes=dtypes)

        self.assertEqual(str(f1.dtypes['b']), 'int64')


    def test_frame_from_records_i(self):


        records = [dict(a=1, b='2', c=3), dict(a=4, b='5', c=6)]
        dtypes = {'b': np.int64}
        f1 = sf.Frame.from_records(records, dtypes=dtypes)

        self.assertEqual(str(f1.dtypes['b']), 'int64')


    def test_frame_from_json_a(self):

        msg = """[
        {
        "userId": 1,
        "id": 1,
        "title": "delectus aut autem",
        "completed": false
        },
        {
        "userId": 1,
        "id": 2,
        "title": "quis ut nam facilis et officia qui",
        "completed": false
        },
        {
        "userId": 1,
        "id": 3,
        "title": "fugiat veniam minus",
        "completed": false
        },
        {
        "userId": 1,
        "id": 4,
        "title": "et porro tempora",
        "completed": true
        }]"""

        f1 = Frame.from_json(msg, name=msg)
        self.assertEqual(sorted(f1.columns.values.tolist()),
                sorted(['completed', 'id', 'title', 'userId']))
        self.assertEqual(f1['id'].sum(), 10)

        self.assertEqual(f1.name, msg)

    @unittest.skip('requires network')
    def test_frame_from_json_b(self):
        url = 'https://jsonplaceholder.typicode.com/todos'
        f1 = Frame.from_json_url(url)
        self.assertEqual(f1.columns.values.tolist(),
                ['completed', 'id', 'title', 'userId'])



    def test_frame_reindex_flat_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )

        columns = IndexHierarchy.from_labels(
                (('a', 1), ('a', 2), ('b', 1), ('b', 2), ('b', 3)))
        f1 = Frame.from_records(records,
                columns=columns,
                index=('x', 'y', 'z'))

        f2 = f1.reindex_flat(columns=True)

        self.assertEqual(f2.to_pairs(0),
                ((('a', 1), (('x', 1), ('y', 30), ('z', 54))), (('a', 2), (('x', 2), ('y', 34), ('z', 95))), (('b', 1), (('x', 'a'), ('y', 'b'), ('z', 'c'))), (('b', 2), (('x', False), ('y', True), ('z', False))), (('b', 3), (('x', True), ('y', False), ('z', False)))))


    def test_frame_add_level_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )
        f1 = Frame.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = f1.reindex_add_level(index='I', columns='II')

        self.assertEqual(f2.to_pairs(0),
                ((('II', 'a'), ((('I', 'x'), 1), (('I', 'y'), 30), (('I', 'z'), 54))), (('II', 'b'), ((('I', 'x'), 2), (('I', 'y'), 34), (('I', 'z'), 95))), (('II', 'c'), ((('I', 'x'), 'a'), (('I', 'y'), 'b'), (('I', 'z'), 'c'))), (('II', 'd'), ((('I', 'x'), False), (('I', 'y'), True), (('I', 'z'), False))), (('II', 'e'), ((('I', 'x'), True), (('I', 'y'), False), (('I', 'z'), False))))
                )


    @unittest.skip('non required dependency')
    def test_frame_from_from_pandas_a(self):
        import pandas as pd

        pdf = pd.DataFrame(
                dict(a=(False, True, False),
                b=(False, False,False),
                c=(1,2,3),
                d=(4,5,6),
                e=(None, None, None)))

        sff = Frame.from_pandas(pdf)
        self.assertTrue((pdf.dtypes.values == sff.dtypes.values).all())


    def test_frame_to_frame_go_a(self):
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )
        f1 = Frame.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = f1.to_frame_go()
        f2['f'] = None
        self.assertEqual(f1.columns.values.tolist(),
                ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual(f2.columns.values.tolist(),
                ['a', 'b', 'c', 'd', 'e', 'f'])



    def test_frame_to_frame_go_b(self):
        records = (
                (1, 2, 'a', False, True),
                (54, 95, 'c', False, False),
                )
        f1 = Frame.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y'),
                name='foo')

        f2 = f1.to_frame_go()
        f3 = f2.to_frame()

        self.assertTrue(f1.name, 'foo')
        self.assertTrue(f2.name, 'foo')
        self.assertTrue(f3.name, 'foo')


    def test_frame_astype_a(self):
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )
        f1 = Frame.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = f1.astype['d':](int)
        self.assertEqual(f2.to_pairs(0),
                (('a', (('x', 1), ('y', 30), ('z', 54))), ('b', (('x', 2), ('y', 34), ('z', 95))), ('c', (('x', 'a'), ('y', 'b'), ('z', 'c'))), ('d', (('x', 0), ('y', 1), ('z', 0))), ('e', (('x', 1), ('y', 0), ('z', 0))))
                )

        f3 = f1.astype[['a', 'b']](bool)
        self.assertEqual(f3.to_pairs(0),
                (('a', (('x', True), ('y', True), ('z', True))), ('b', (('x', True), ('y', True), ('z', True))), ('c', (('x', 'a'), ('y', 'b'), ('z', 'c'))), ('d', (('x', False), ('y', True), ('z', False))), ('e', (('x', True), ('y', False), ('z', False))))
                )


    def test_frame_pickle_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        pbytes = pickle.dumps(f1)
        f2 = pickle.loads(pbytes)

        self.assertEqual([b.flags.writeable for b in f2._blocks._blocks],
                [False, False, False, False, False])

    def test_frame_set_index_hierarchy_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 2, 'b', True, False),
                (30, 50, 'a', True, False),
                (30, 50, 'b', True, False),
                )

        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        f2 = f1.set_index_hierarchy(['q', 'r'])
        self.assertEqual(f2.index.name, ('q', 'r'))

        self.assertEqual(f2.to_pairs(0),
                (('p', (((2, 'a'), 1), ((2, 'b'), 30), ((50, 'a'), 30), ((50, 'b'), 30))), ('q', (((2, 'a'), 2), ((2, 'b'), 2), ((50, 'a'), 50), ((50, 'b'), 50))), ('r', (((2, 'a'), 'a'), ((2, 'b'), 'b'), ((50, 'a'), 'a'), ((50, 'b'), 'b'))), ('s', (((2, 'a'), False), ((2, 'b'), True), ((50, 'a'), True), ((50, 'b'), True))), ('t', (((2, 'a'), True), ((2, 'b'), False), ((50, 'a'), False), ((50, 'b'), False)))))

        f3 = f1.set_index_hierarchy(['q', 'r'], drop=True)
        self.assertEqual(f3.index.name, ('q', 'r'))

        self.assertEqual(f3.to_pairs(0),
                (('p', (((2, 'a'), 1), ((2, 'b'), 30), ((50, 'a'), 30), ((50, 'b'), 30))), ('s', (((2, 'a'), False), ((2, 'b'), True), ((50, 'a'), True), ((50, 'b'), True))), ('t', (((2, 'a'), True), ((2, 'b'), False), ((50, 'a'), False), ((50, 'b'), False))))
                )

        f4 = f1.set_index_hierarchy(slice('q', 'r'), drop=True)
        self.assertEqual(f4.index.name, ('q', 'r'))

        self.assertEqual(f4.to_pairs(0),
                (('p', (((2, 'a'), 1), ((2, 'b'), 30), ((50, 'a'), 30), ((50, 'b'), 30))), ('s', (((2, 'a'), False), ((2, 'b'), True), ((50, 'a'), True), ((50, 'b'), True))), ('t', (((2, 'a'), True), ((2, 'b'), False), ((50, 'a'), False), ((50, 'b'), False))))
                )


    def test_frame_set_index_hierarchy_b(self):

        labels = (
                (1, 1, 'a'),
                (1, 2, 'b'),
                (1, 3, 'c'),
                (2, 1, 'd'),
                (2, 2, 'e'),
                (2, 3, 'f'),
                (3, 1, 'g'),
                (3, 2, 'h'),
                (3, 3, 'i'),
                )

        f = Frame(labels)
        # import ipdb; ipdb.set_trace()
        f = f.astype[[0, 1]](int)

        # TODO: this fails
        # fh = f.set_index_hierarchy([0, 1], drop=True)

        fh = f.set_index_hierarchy([0, 1], drop=False)
        self.assertEqual(
                fh.loc[HLoc[:, 3]].to_pairs(0),
                ((0, (((1, 3), 1), ((2, 3), 2), ((3, 3), 3))), (1, (((1, 3), 3), ((2, 3), 3), ((3, 3), 3))), (2, (((1, 3), 'c'), ((2, 3), 'f'), ((3, 3), 'i'))))
                )


    @unittest.skip('requires network')
    def test_frame_set_index_hierarchy_c(self):

        f = sf.FrameGO.from_json_url('https://jsonplaceholder.typicode.com/photos')
        tracks = f.iter_group('albumId', axis=0).apply(lambda g: len(g))
        # f['tracks'] = f['albumId'].iter_element().apply(tracks)

        from itertools import chain

        items = chain.from_iterable(zip(g.index, range(len(g))) for g in f.iter_group('albumId'))

        f['track'] = Series.from_items(items)


        fh = f.set_index_hierarchy(['albumId', 'track'], drop=True)

        fh.loc[HLoc[:, [2, 5]], ['title', 'url']]

        # import ipdb; ipdb.set_trace()
        # this gives the wrong result:
        fh.loc[HLoc[:, [2, 5]], 'title']

        fh.loc[sf.ILoc[-1], ['id', 'title', 'url']]

    def test_frame_set_index_hierarchy_d(self):
        f1 = sf.Frame.from_records([('one', 1, 'hello')],
                columns=['name', 'val', 'msg'])

        f2 = f1.set_index_hierarchy(['name', 'val'], drop=True)

        self.assertEqual(f2.to_pairs(0),
                (('msg', ((('one', 1), 'hello'),)),))

    def test_frame_iloc_in_loc_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.loc[ILoc[-2:], ['q', 't']].to_pairs(0),
                (('q', (('y', 95), ('z', 73))), ('t', (('y', False), ('z', True)))))

        self.assertEqual(f1.loc[ILoc[[0, -1]], 's':].to_pairs(0),
                (('s', (('w', False), ('z', True))), ('t', (('w', False), ('z', True)))))

        self.assertEqual(f1.loc[['w', 'x'], ILoc[[0, -1]]].to_pairs(0),
                (('p', (('w', 2), ('x', 30))), ('t', (('w', False), ('x', False))))
                )



    def test_frame_iter_group_items_a(self):

        # testing a hierarchical index and columns, selecting column with a tuple

        records = (
                ('a', 999999, 0.1),
                ('a', 201810, 0.1),
                ('b', 999999, 0.4),
                ('b', 201810, 0.4))
        f1 = Frame.from_records(records, columns=list('abc'))

        f1 = f1.set_index_hierarchy(['a', 'b'], drop=False)
        f1 = f1.reindex_add_level(columns='i')

        groups = list(f1.iter_group_items(('i', 'a'), axis=0))
        self.assertEqual(groups[0][0], 'a')
        self.assertEqual(groups[0][1].to_pairs(0),
                ((('i', 'a'), ((('a', 999999), 'a'), (('a', 201810), 'a'))), (('i', 'b'), ((('a', 999999), 999999), (('a', 201810), 201810))), (('i', 'c'), ((('a', 999999), 0.1), (('a', 201810), 0.1)))))

        self.assertEqual(groups[1][0], 'b')
        self.assertEqual(groups[1][1].to_pairs(0),
                ((('i', 'a'), ((('b', 999999), 'b'), (('b', 201810), 'b'))), (('i', 'b'), ((('b', 999999), 999999), (('b', 201810), 201810))), (('i', 'c'), ((('b', 999999), 0.4), (('b', 201810), 0.4)))))


    def test_frame_drop_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.drop['r':].to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 2), ('z', 30))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73)))))

        self.assertEqual(f1.drop.loc[['x', 'z'], 's':].to_pairs(0),
                (('p', (('w', 2), ('y', 2))), ('q', (('w', 2), ('y', 95))), ('r', (('w', 'a'), ('y', 'c')))))

        self.assertEqual(f1.drop.loc['x':, 'q':].to_pairs(0),
                (('p', (('w', 2),)),))


    def test_frame_roll_a(self):

        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.roll(1).to_pairs(0),
                (('p', (('w', 30), ('x', 2), ('y', 30), ('z', 2))), ('q', (('w', 73), ('x', 2), ('y', 34), ('z', 95))), ('r', (('w', 'd'), ('x', 'a'), ('y', 'b'), ('z', 'c'))), ('s', (('w', True), ('x', False), ('y', True), ('z', False))), ('t', (('w', True), ('x', False), ('y', False), ('z', False))))
                )

        self.assertEqual(f1.roll(-2, include_index=True).to_pairs(0),
                (('p', (('y', 2), ('z', 30), ('w', 2), ('x', 30))), ('q', (('y', 95), ('z', 73), ('w', 2), ('x', 34))), ('r', (('y', 'c'), ('z', 'd'), ('w', 'a'), ('x', 'b'))), ('s', (('y', False), ('z', True), ('w', False), ('x', True))), ('t', (('y', False), ('z', True), ('w', False), ('x', False))))
                )

        self.assertEqual(f1.roll(-3, 3).to_pairs(0),
                (('p', (('w', 'd'), ('x', 'a'), ('y', 'b'), ('z', 'c'))), ('q', (('w', True), ('x', False), ('y', True), ('z', False))), ('r', (('w', True), ('x', False), ('y', False), ('z', False))), ('s', (('w', 30), ('x', 2), ('y', 30), ('z', 2))), ('t', (('w', 73), ('x', 2), ('y', 34), ('z', 95))))
                )

        self.assertEqual(
                f1.roll(-3, 3, include_index=True, include_columns=True).to_pairs(0),
                (('r', (('z', 'd'), ('w', 'a'), ('x', 'b'), ('y', 'c'))), ('s', (('z', True), ('w', False), ('x', True), ('y', False))), ('t', (('z', True), ('w', False), ('x', False), ('y', False))), ('p', (('z', 30), ('w', 2), ('x', 30), ('y', 2))), ('q', (('z', 73), ('w', 2), ('x', 34), ('y', 95)))))


    def test_frame_shift_a(self):


        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        dtype = np.dtype

        # nan as default forces floats and objects
        self.assertEqual(f1.shift(2).dtypes.values.tolist(),
                [dtype('float64'), dtype('float64'), dtype('O'), dtype('O'), dtype('O')])

        self.assertEqual(f1.shift(1, fill_value=-1).to_pairs(0),
                (('p', (('w', -1), ('x', 2), ('y', 30), ('z', 2))), ('q', (('w', -1), ('x', 2), ('y', 34), ('z', 95))), ('r', (('w', -1), ('x', 'a'), ('y', 'b'), ('z', 'c'))), ('s', (('w', -1), ('x', False), ('y', True), ('z', False))), ('t', (('w', -1), ('x', False), ('y', False), ('z', False))))
                )

        self.assertEqual(f1.shift(1, 1, fill_value=-1).to_pairs(0),
                (('p', (('w', -1), ('x', -1), ('y', -1), ('z', -1))), ('q', (('w', -1), ('x', 2), ('y', 30), ('z', 2))), ('r', (('w', -1), ('x', 2), ('y', 34), ('z', 95))), ('s', (('w', -1), ('x', 'a'), ('y', 'b'), ('z', 'c'))), ('t', (('w', -1), ('x', False), ('y', True), ('z', False))))
                )

        self.assertEqual(f1.shift(0, 5, fill_value=-1).to_pairs(0),
                (('p', (('w', -1), ('x', -1), ('y', -1), ('z', -1))), ('q', (('w', -1), ('x', -1), ('y', -1), ('z', -1))), ('r', (('w', -1), ('x', -1), ('y', -1), ('z', -1))), ('s', (('w', -1), ('x', -1), ('y', -1), ('z', -1))), ('t', (('w', -1), ('x', -1), ('y', -1), ('z', -1))))
                )


    def test_frame_name_a(self):

        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'y', 'z'),
                name='test')

        self.assertEqual(f1.name, 'test')

        f2 = f1.rename('alt')

        self.assertEqual(f1.name, 'test')
        self.assertEqual(f2.name, 'alt')



    def test_frame_name_b(self):

        with self.assertRaises(TypeError):
            f = Frame.from_dict(dict(a=(1,2), b=(3,4)), name=['test'])

        with self.assertRaises(TypeError):
            f = Frame.from_dict(dict(a=(1,2), b=(3,4)), name={'a': 30})

        with self.assertRaises(TypeError):
            f = Frame.from_dict(dict(a=(1,2), b=(3,4)), name=('a', [1, 2]))



    def test_frame_name_b(self):

        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                )
        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'y', 'z'),
                name='test')

        self.assertEqual(f1.name, 'test')

        f2 = f1.rename('alt')

        self.assertEqual(f1.name, 'test')
        self.assertEqual(f2.name, 'alt')

        f2['u'] = -1

        self.assertEqual(f1.columns.values.tolist(), ['p', 'q', 'r', 's', 't'])
        self.assertEqual(f2.columns.values.tolist(), ['p', 'q', 'r', 's', 't', 'u'])



    @skip_win
    def test_frame_display_a(self):

        f1 = Frame(((1,2),(True,False)), name='foo',
                index=Index(('x', 'y'), name='bar'),
                columns=Index(('a', 'b'), name='rig')
                )

        match = tuple(f1.display(DisplayConfig(type_color=False)))

        self.assertEqual(
            match,
            (['<Frame: foo>'], ['<Index: rig>', 'a', 'b', '<<U1>'], ['<Index: bar>', '', ''], ['x', '1', '2'], ['y', '1', '0'], ['<<U1>', '<int64>', '<int64>'])
            )



    def test_frame_reindex_drop_level_a(self):

        f1 = Frame.from_records(
                (dict(a=x, b=x) for x in range(4)),
                index=sf.IndexHierarchy.from_labels([(1,1),(1,2),(2,3),(2,4)]))

        with self.assertRaises(Exception):
            # this results in an index of size 2 being created, as we dro the leves with a postive depth; next support negative depth?
            f2 = f1.reindex_drop_level(index=-1)



    def test_frame_iter_group_index_a(self):

        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'y', 'z'))

        post = tuple(f1.iter_group_index(0, axis=0))

        self.assertEqual(len(post), 3)
        self.assertEqual(
                f1.iter_group_index(0, axis=0).apply(lambda x: x[['p', 'q']].values.sum()).to_pairs(),
                (('x', 4), ('y', 64), ('z', 97))
                )


    def test_frame_iter_group_index_b(self):

        records = (
                (2, 2, 'a', 'q', False, False),
                (30, 34, 'b', 'c', True, False),
                (2, 95, 'c', 'd', False, False),
                )
        f1 = Frame.from_records(records,
                columns=IndexHierarchy.from_product((1, 2, 3), ('a', 'b')),
                index=('x', 'y', 'z'))

        # with axis 1, we are grouping based on columns while maintain the index
        post = tuple(f1.iter_group_index(1, axis=1))

        self.assertEqual(len(post), 2)

        post = f1[HLoc[f1.columns[0]]]
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.to_pairs(),
            (('x', 2), ('y', 30), ('z', 2))
            )

        post = f1.loc[:, HLoc[f1.columns[0]]]
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.to_pairs(),
            (('x', 2), ('y', 30), ('z', 2))
            )

        self.assertEqual(
                f1.iter_group_index(1, axis=1).apply(lambda x: x.iloc[:, 0].sum()).to_pairs(),
                (('a', 34), ('b', 131))
                )

    def test_frame_clip_a(self):

        records = (
                (2, 2),
                (30, 34),
                (2, 95),
                )
        f1 = Frame.from_records(records,
                columns=('a', 'b'),
                index=('x', 'y', 'z')
                )

        self.assertEqual(f1.clip(upper=0).to_pairs(0),
                (('a', (('x', 0), ('y', 0), ('z', 0))), ('b', (('x', 0), ('y', 0), ('z', 0)))))

        self.assertEqual(f1.clip(lower=90).to_pairs(0),
                (('a', (('x', 90), ('y', 90), ('z', 90))), ('b', (('x', 90), ('y', 90), ('z', 95)))))


    def test_frame_clip_b(self):

        records = (
                (2, 2),
                (30, 34),
                (2, 95),
                )
        f1 = Frame.from_records(records,
                columns=('a', 'b'),
                index=('x', 'y', 'z')
                )

        s1 = Series((1, 20), index=('a', 'b'))

        self.assertEqual(f1.clip(upper=s1, axis=1).to_pairs(0),
            (('a', (('x', 1), ('y', 1), ('z', 1))), ('b', (('x', 2), ('y', 20), ('z', 20)))))

        s2 = Series((3, 33, 80), index=('x', 'y', 'z'))

        self.assertEqual(f1.clip(s2, axis=0).to_pairs(0),
            (('a', (('x', 3), ('y', 33), ('z', 80))), ('b', (('x', 3), ('y', 34), ('z', 95)))))


    def test_frame_clip_c(self):

        records = (
                (2, 2),
                (30, 34),
                (2, 95),
                )
        f1 = Frame.from_records(records,
                columns=('a', 'b'),
                index=('x', 'y', 'z')
                )

        f2 = sf.Frame([[5, 4], [0, 10]], index=list('yz'), columns=list('ab'))

        self.assertEqual(f1.clip(upper=f2).to_pairs(0),
                (('a', (('x', 2.0), ('y', 5.0), ('z', 0.0))), ('b', (('x', 2.0), ('y', 4.0), ('z', 10.0)))))

        self.assertEqual(f1.clip(lower=3, upper=f2).to_pairs(0),
            (('a', (('x', 3.0), ('y', 5.0), ('z', 3.0))), ('b', (('x', 3.0), ('y', 4.0), ('z', 10.0))))
            )

    def test_frame_loc_e(self):
        fp = self.get_test_input('jph_photos.txt')
        # using a raw string to avoid unicode decoding issues on windows
        f = sf.Frame.from_tsv(fp, dtypes=dict(albumId=np.int64, id=np.int64), encoding='utf-8')
        post = f.loc[f['albumId'] >= 98]
        self.assertEqual(post.shape, (150, 5))


    def test_frame_from_dict_a(self):

        with self.assertRaises(RuntimeError):
            # mismatched length
            sf.Frame.from_dict(dict(a=(1,2,3,4,5), b=tuple('abcdef')))





if __name__ == '__main__':
    unittest.main()
