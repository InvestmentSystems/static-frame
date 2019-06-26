
import unittest
import numpy as np

from collections import OrderedDict

from static_frame import Index
from static_frame import IndexGO
from static_frame import IndexDate
from static_frame import Series
from static_frame import Frame
from static_frame import FrameGO
from static_frame import IndexYearMonth
from static_frame import IndexYear
from static_frame import DisplayConfig

from static_frame import IndexHierarchy
from static_frame import IndexHierarchyGO
from static_frame import IndexLevel
from static_frame import IndexLevelGO
from static_frame import HLoc
from static_frame.core.array_go import ArrayGO

from static_frame.test.test_case import TestCase

class TestUnit(TestCase):


    def test_hierarhcy_init_a(self):

        labels = (('I', 'A'),
                ('I', 'B'),
                )

        ih1 = IndexHierarchy.from_labels(labels, name='foo')
        ih2 = IndexHierarchy(ih1)
        self.assertEqual(ih1.name, 'foo')
        self.assertEqual(ih2.name, 'foo')


    def test_hierarhcy_init_b(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'B'),
                ('I', 'C')
                )

        with self.assertRaises(RuntimeError):
            ih1 = IndexHierarchy.from_labels(labels)

    def test_hierarhcy_init_c(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'B'),
                ('III', 'B'),
                ('III', 'A')
                )

        ih1 = IndexHierarchy.from_labels(labels)
        self.assertEqual(ih1.values.tolist(),
            [['I', 'A'], ['I', 'B'], ['II', 'B'], ['III', 'B'], ['III', 'A']])


    def test_hierarhcy_init_d(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'B'),
                ('III', 'B'),
                ('III', 'B')
                )
        with self.assertRaises(KeyError):
            ih1 = IndexHierarchy.from_labels(labels)

    def test_hierarhcy_init_e(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'B'),
                ('III', 'B'),
                ('I', 'B'),
                )

        with self.assertRaises(RuntimeError):
            ih1 = IndexHierarchy.from_labels(labels)



    def test_hierarhcy_init_f(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'B'),
                ('III', 'B'),
                ('I', 'B'),
                )

        with self.assertRaises(RuntimeError):
            ih1 = IndexHierarchy.from_labels(labels)

    def test_hierarhcy_init_g(self):

        labels = (
                ('I', 'A', 1),
                ('I', 'B', 1),
                ('II', 'A', 1),
                ('II', 'A', 2),
                ('II', 'A', 1),
                )
        with self.assertRaises(KeyError):
            ih1 = IndexHierarchy.from_labels(labels)

    def test_hierarhcy_init_h(self):

        labels = (
                ('I', 'A', 1),
                ('I', 'B', 1),
                ('II', 'A', 1),
                ('II', 'A', 2),
                ('II', 'B', 1),
                ('II', 'A', 3),
                )
        with self.assertRaises(RuntimeError):
            ih1 = IndexHierarchy.from_labels(labels)


    def test_hierarchy_loc_to_iloc_a(self):


        groups = Index(('A', 'B', 'C'))
        dates = IndexDate.from_date_range('2018-01-01', '2018-01-04')
        observations = Index(('x', 'y'))


        lvl2a = IndexLevel(index=observations)
        lvl2b = IndexLevel(index=observations, offset=2)
        lvl2c = IndexLevel(index=observations, offset=4)
        lvl2d = IndexLevel(index=observations, offset=6)
        lvl2_targets = ArrayGO((lvl2a, lvl2b, lvl2c, lvl2d))


        lvl1a = IndexLevel(index=dates,
                targets=lvl2_targets, offset=0)
        lvl1b = IndexLevel(index=dates,
                targets=lvl2_targets, offset=len(lvl1a))
        lvl1c = IndexLevel(index=dates,
                targets=lvl2_targets, offset=len(lvl1a) * 2)

        # we need as many targets as len(index)
        lvl0 = IndexLevel(index=groups,
                targets=ArrayGO((lvl1a, lvl1b, lvl1c)))


        self.assertEqual(len(lvl2a), 2)
        self.assertEqual(len(lvl1a), 8)
        self.assertEqual(len(lvl0), 24)

        self.assertEqual(list(lvl2a.depths()),
                [1])
        self.assertEqual(list(lvl1a.depths()),
                [2, 2, 2, 2])
        self.assertEqual(list(lvl0.depths()),
                [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3])

        ih = IndexHierarchy(lvl0)

        self.assertEqual(len(ih), 24)

        post = ih.loc_to_iloc(HLoc[
                ['A', 'B', 'C'],
                slice('2018-01-01', '2018-01-04'),
                ['x', 'y']])
        # this will break if we recognize this can be a slice
        self.assertEqual(post, list(range(len(ih))))

        post = ih.loc_to_iloc(HLoc[
                ['A', 'B', 'C'],
                slice('2018-01-01', '2018-01-04'),
                'x'])

        self.assertEqual(post, list(range(0, len(ih), 2)))

        post = ih.loc_to_iloc(HLoc[
                'C',
                '2018-01-03',
                'y'])

        self.assertEqual(post, 21)

        post = ih.loc_to_iloc(HLoc['B', '2018-01-03':, 'y'])
        self.assertEqual(post, [13, 15])


        post = ih.loc_to_iloc(HLoc[['B', 'C'], '2018-01-03'])
        self.assertEqual(post, [12, 13, 20, 21])

        post = ih.loc_to_iloc(HLoc[['A', 'C'], :, 'y'])
        self.assertEqual(post, [1, 3, 5, 7, 17, 19, 21, 23])

        post = ih.loc_to_iloc(HLoc[['A', 'C'], :, 'x'])
        self.assertEqual(post, [0, 2, 4, 6, 16, 18, 20, 22])



    def test_hierarchy_from_product_a(self):

        groups = Index(('A', 'B', 'C'))
        dates = IndexDate.from_date_range('2018-01-01', '2018-01-04')
        observations = Index(('x', 'y'))

        ih = IndexHierarchy.from_product(groups, dates, observations)


    def test_hierarchy_from_tree_a(self):

        OD = OrderedDict

        tree = OD([('A', (1, 2, 3, 4)), ('B', (1, 2))])

        ih = IndexHierarchy.from_tree(tree)

        self.assertEqual(ih.to_frame().to_pairs(0),
                ((0, ((0, 'A'), (1, 'A'), (2, 'A'), (3, 'A'), (4, 'B'), (5, 'B'))), (1, ((0, 1), (1, 2), (2, 3), (3, 4), (4, 1), (5, 2))))
                )


    def test_hierarchy_from_tree_b(self):

        OD = OrderedDict

        tree = OD([
                ('I', OD([
                        ('A', (1, 2)), ('B', (1, 2, 3)), ('C', (2, 3))
                        ])
                ),
                ('II', OD([
                        ('A', (1, 2, 3)), ('B', (1,))
                        ])
                ),
                ])

        ih = IndexHierarchy.from_tree(tree)
        self.assertEqual(ih.to_frame().to_pairs(0),
                ((0, ((0, 'I'), (1, 'I'), (2, 'I'), (3, 'I'), (4, 'I'), (5, 'I'), (6, 'I'), (7, 'II'), (8, 'II'), (9, 'II'), (10, 'II'))), (1, ((0, 'A'), (1, 'A'), (2, 'B'), (3, 'B'), (4, 'B'), (5, 'C'), (6, 'C'), (7, 'A'), (8, 'A'), (9, 'A'), (10, 'B'))), (2, ((0, 1), (1, 2), (2, 1), (3, 2), (4, 3), (5, 2), (6, 3), (7, 1), (8, 2), (9, 3), (10, 1))))
                )


    def test_hierarchy_from_labels_a(self):

        labels = (('I', 'A', 1),
                ('I', 'A', 2),
                ('I', 'B', 1),
                ('I', 'B', 2),
                ('II', 'A', 1),
                ('II', 'A', 2),
                ('II', 'B', 1),
                ('II', 'B', 2),
                )

        ih = IndexHierarchy.from_labels(labels)
        self.assertEqual(len(ih), 8)
        self.assertEqual(ih.depth, 3)

        self.assertEqual([ih.loc_to_iloc(x) for x in labels],
                [0, 1, 2, 3, 4, 5, 6, 7])


        labels = (('I', 'A', 1),
                ('I', 'A', 2),
                ('I', 'B', 1),
                ('II', 'B', 2),
                )

        ih = IndexHierarchy.from_labels(labels)
        self.assertEqual(len(ih), 4)
        self.assertEqual(ih.depth, 3)

        self.assertEqual([ih.loc_to_iloc(x) for x in labels], [0, 1, 2, 3])


    def test_hierarchy_from_labels_b(self):

        labels = (('I', 'A'),
                ('I', 'B'),
                )

        ih = IndexHierarchy.from_labels(labels)

        self.assertEqual(ih.to_frame().to_pairs(0),
                ((0, ((0, 'I'), (1, 'I'))), (1, ((0, 'A'), (1, 'B')))))

    def test_hierarchy_loc_to_iloc_b(self):
        OD = OrderedDict
        tree = OD([
                ('I', OD([
                        ('A', (1, 2)), ('B', (1, 2, 3)), ('C', (2, 3))
                        ])
                ),
                ('II', OD([
                        ('A', (1, 2, 3)), ('B', (1,))
                        ])
                ),
                ])

        ih = IndexHierarchy.from_tree(tree)

        post = ih.loc_to_iloc(HLoc['I', 'B', 1])
        self.assertEqual(post, 2)

        post = ih.loc_to_iloc(HLoc['I', 'B', 3])
        self.assertEqual(post, 4)

        post = ih.loc_to_iloc(HLoc['II', 'A', 3])
        self.assertEqual(post, 9)

        post = ih.loc_to_iloc(HLoc['II', 'A'])
        self.assertEqual(post, slice(7, 10))

        post = ih.loc_to_iloc(HLoc['I', 'C'])
        self.assertEqual(post, slice(5, 7))


        post = ih.loc_to_iloc(HLoc['I', ['A', 'C']])
        self.assertEqual(post, [0, 1, 5, 6])


        post = ih.loc_to_iloc(HLoc[:, 'A', :])
        self.assertEqual(post, [0, 1, 7, 8, 9])


        post = ih.loc_to_iloc(HLoc[:, 'C', 3])
        self.assertEqual(post, [6])

        post = ih.loc_to_iloc(HLoc[:, :, 3])
        self.assertEqual(post, [4, 6, 9])

        post = ih.loc_to_iloc(HLoc[:, :, 1])
        self.assertEqual(post, [0, 2, 7, 10])

        # TODO: not sure what to do when a multiple selection, [1, 2], is a superset of the leaf index; we do not match with a normal loc
        # ih.loc_to_iloc((slice(None), slice(None), [1,2]))


    def test_hierarchy_loc_to_iloc_c(self):
        OD = OrderedDict
        tree = OD([
                ('I', OD([
                        ('A', (1, 2)), ('B', (1, 2, 3)), ('C', (2, 3))
                        ])
                ),
                ('II', OD([
                        ('A', (1, 2, 3)), ('B', (1,))
                        ])
                ),
                ])

        ih = IndexHierarchy.from_tree(tree)

        # TODO: add additional validaton
        post = ih.loc[('I', 'B', 2): ('II', 'A', 2)]
        self.assertTrue(len(post), 6)

        post = ih.loc[[('I', 'B', 2), ('II', 'A', 2)]]
        self.assertTrue(len(post), 2)


    def test_hierarchy_contains_a(self):
        labels = (('I', 'A'),
                ('I', 'B'),
                )
        ih = IndexHierarchy.from_labels(labels)

        self.assertTrue(('I', 'A') in ih)


    def test_hierarchy_extract_a(self):
        idx = IndexHierarchy.from_product(['A', 'B'], [1, 2])

        self.assertEqual(idx.iloc[1], ('A', 2))
        self.assertEqual(idx.loc[('B', 1)], ('B', 1))
        self.assertEqual(idx[2], ('B', 1))
        self.assertEqual(idx.loc[HLoc['B', 1]], ('B', 1))



    def test_hierarchy_iter_a(self):
        OD = OrderedDict
        tree = OD([
                ('I', OD([
                        ('A', (1, 2)), ('B', (1, 2))
                        ])
                ),
                ('II', OD([
                        ('A', (1, 2)), ('B', (1, 2))
                        ])
                ),
                ])

        ih = IndexHierarchy.from_tree(tree)

        # this iterates over numpy arrays, which can be used with contains
        self.assertEqual([k in ih for k in ih],
                [True, True, True, True, True, True, True, True]
                )


    def test_hierarchy_reversed(self):
        labels = (('a', 1), ('a', 2), ('b', 1), ('b', 2))
        hier_idx = IndexHierarchy.from_labels(labels)
        self.assertTrue(
            all(tuple(hidx_1) == hidx_2
                for hidx_1, hidx_2 in zip(reversed(hier_idx), reversed(labels)))
        )


    def test_hierarchy_keys_a(self):
        OD = OrderedDict
        tree = OD([
                ('I', OD([
                        ('A', (1, 2)), ('B', (1, 2))
                        ])
                ),
                ('II', OD([
                        ('A', (1, 2)), ('B', (1, 2))
                        ])
                ),
                ])

        ih = IndexHierarchy.from_tree(tree)

        # NOTE: for now, __iter__ return arrays, so we have convert to a tuple
        self.assertEqual([tuple(k) in ih.keys() for k in ih],
                [True, True, True, True, True, True, True, True]
                )


    def test_hierarchy_display_a(self):
        OD = OrderedDict
        tree = OD([
                ('I', OD([
                        ('A', (1, 2)), ('B', (1, 2))
                        ])
                ),
                ('II', OD([
                        ('A', (1, 2)), ('B', (1, 2))
                        ])
                ),
                ])

        ih = IndexHierarchy.from_tree(tree)

        post = ih.display()
        self.assertEqual(len(post), 10)

        s = Series(range(8), index=ih)
        post = s.display()
        self.assertEqual(len(post), 11)

    def test_hierarchy_loc_a(self):
        OD = OrderedDict
        tree = OD([
                ('I', OD([
                        ('A', (1, 2)), ('B', (1, 2))
                        ])
                ),
                ('II', OD([
                        ('A', (1, 2)), ('B', (1, 2))
                        ])
                ),
                ])

        ih = IndexHierarchy.from_tree(tree)

        s = Series(range(8), index=ih)

        self.assertEqual(
                s.loc[HLoc['I']].values.tolist(),
                [0, 1, 2, 3])

        self.assertEqual(
                s.loc[HLoc[:, 'A']].values.tolist(),
                [0, 1, 4, 5])

    def test_hierarchy_series_a(self):
        f = IndexHierarchy.from_tree
        s1 = Series(23, index=f(dict(a=(1,2,3))))
        self.assertEqual(s1.values.tolist(), [23, 23, 23])

        f = IndexHierarchy.from_product
        s2 = Series(3, index=f(Index(('a', 'b')), Index((1,2))))
        self.assertEqual(s2.to_pairs(),
                ((('a', 1), 3), (('a', 2), 3), (('b', 1), 3), (('b', 2), 3)))


    def test_hierarchy_frame_a(self):
        OD = OrderedDict
        tree = OD([
                ('I', OD([
                        ('A', (1,)), ('B', (1, 2))
                        ])
                ),
                ('II', OD([
                        ('A', (1,)), ('B', (1, 2))
                        ])
                ),
                ])

        ih = IndexHierarchy.from_tree(tree)

        data = np.arange(6*6).reshape(6, 6)
        f1 = Frame(data, index=ih, columns=ih)
        # self.assertEqual(len(f.to_pairs(0)), 8)


        f2 = f1.assign.loc[('I', 'B', 2), ('II', 'A', 1)](200)

        post = f2.to_pairs(0)
        self.assertEqual(post,
                ((('I', 'A', 1), ((('I', 'A', 1), 0), (('I', 'B', 1), 6), (('I', 'B', 2), 12), (('II', 'A', 1), 18), (('II', 'B', 1), 24), (('II', 'B', 2), 30))), (('I', 'B', 1), ((('I', 'A', 1), 1), (('I', 'B', 1), 7), (('I', 'B', 2), 13), (('II', 'A', 1), 19), (('II', 'B', 1), 25), (('II', 'B', 2), 31))), (('I', 'B', 2), ((('I', 'A', 1), 2), (('I', 'B', 1), 8), (('I', 'B', 2), 14), (('II', 'A', 1), 20), (('II', 'B', 1), 26), (('II', 'B', 2), 32))), (('II', 'A', 1), ((('I', 'A', 1), 3), (('I', 'B', 1), 9), (('I', 'B', 2), 200), (('II', 'A', 1), 21), (('II', 'B', 1), 27), (('II', 'B', 2), 33))), (('II', 'B', 1), ((('I', 'A', 1), 4), (('I', 'B', 1), 10), (('I', 'B', 2), 16), (('II', 'A', 1), 22), (('II', 'B', 1), 28), (('II', 'B', 2), 34))), (('II', 'B', 2), ((('I', 'A', 1), 5), (('I', 'B', 1), 11), (('I', 'B', 2), 17), (('II', 'A', 1), 23), (('II', 'B', 1), 29), (('II', 'B', 2), 35))))
        )


        f3 = f1.assign.loc[('I', 'B', 2):, HLoc[:, :, 2]](200)

        self.assertEqual(f3.to_pairs(0),
                ((('I', 'A', 1), ((('I', 'A', 1), 0), (('I', 'B', 1), 6), (('I', 'B', 2), 12), (('II', 'A', 1), 18), (('II', 'B', 1), 24), (('II', 'B', 2), 30))), (('I', 'B', 1), ((('I', 'A', 1), 1), (('I', 'B', 1), 7), (('I', 'B', 2), 13), (('II', 'A', 1), 19), (('II', 'B', 1), 25), (('II', 'B', 2), 31))), (('I', 'B', 2), ((('I', 'A', 1), 2), (('I', 'B', 1), 8), (('I', 'B', 2), 200), (('II', 'A', 1), 200), (('II', 'B', 1), 200), (('II', 'B', 2), 200))), (('II', 'A', 1), ((('I', 'A', 1), 3), (('I', 'B', 1), 9), (('I', 'B', 2), 15), (('II', 'A', 1), 21), (('II', 'B', 1), 27), (('II', 'B', 2), 33))), (('II', 'B', 1), ((('I', 'A', 1), 4), (('I', 'B', 1), 10), (('I', 'B', 2), 16), (('II', 'A', 1), 22), (('II', 'B', 1), 28), (('II', 'B', 2), 34))), (('II', 'B', 2), ((('I', 'A', 1), 5), (('I', 'B', 1), 11), (('I', 'B', 2), 200), (('II', 'A', 1), 200), (('II', 'B', 1), 200), (('II', 'B', 2), 200))))
        )



    def test_hierarchy_frame_b(self):
        OD = OrderedDict
        tree = OD([
                ('I', OD([
                        ('A', (1,)), ('B', (1, 2))
                        ])
                ),
                ('II', OD([
                        ('A', (1,)), ('B', (1, 2))
                        ])
                ),
                ])

        ih = IndexHierarchyGO.from_tree(tree)
        data = np.arange(6*6).reshape(6, 6)
        # TODO: this only works if own_columns is True for now
        f1 = FrameGO(data, index=range(6), columns=ih, own_columns=True)
        f1[('II', 'B', 3)] = 0

        f2 = f1[HLoc[:, 'B']]
        self.assertEqual(f2.shape, (6, 5))
        self.assertEqual(f2.to_pairs(0),
                ((('I', 'B', 1), ((0, 1), (1, 7), (2, 13), (3, 19), (4, 25), (5, 31))), (('I', 'B', 2), ((0, 2), (1, 8), (2, 14), (3, 20), (4, 26), (5, 32))), (('II', 'B', 1), ((0, 4), (1, 10), (2, 16), (3, 22), (4, 28), (5, 34))), (('II', 'B', 2), ((0, 5), (1, 11), (2, 17), (3, 23), (4, 29), (5, 35))), (('II', 'B', 3), ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0))))
                )

        f3 = f1[HLoc[:, :, 1]]
        self.assertEqual(f3.to_pairs(0), ((('I', 'A', 1), ((0, 0), (1, 6), (2, 12), (3, 18), (4, 24), (5, 30))), (('I', 'B', 1), ((0, 1), (1, 7), (2, 13), (3, 19), (4, 25), (5, 31))), (('II', 'A', 1), ((0, 3), (1, 9), (2, 15), (3, 21), (4, 27), (5, 33))), (('II', 'B', 1), ((0, 4), (1, 10), (2, 16), (3, 22), (4, 28), (5, 34)))))


        f4 = f1.loc[[2, 5], HLoc[:, 'A']]
        self.assertEqual(f4.to_pairs(0),
                ((('I', 'A', 1), ((2, 12), (5, 30))), (('II', 'A', 1), ((2, 15), (5, 33)))))



    def test_hierarchy_index_go_a(self):

        OD = OrderedDict
        tree1 = OD([
                ('I', OD([
                        ('A', (1,)), ('B', (1, 2))
                        ])
                ),
                ('II', OD([
                        ('A', (1,)), ('B', (1, 2))
                        ])
                ),
                ])
        ih1 = IndexHierarchyGO.from_tree(tree1)

        tree2 = OD([
                ('III', OD([
                        ('A', (1,)), ('B', (1, 2))
                        ])
                ),
                ('IV', OD([
                        ('A', (1,)), ('B', (1, 2))
                        ])
                ),
                ])
        ih2 = IndexHierarchyGO.from_tree(tree2)

        ih1.extend(ih2)

        # self.assertEqual(ih1.loc_to_iloc(('IV', 'B', 2)), 11)
        self.assertEqual(len(ih2), 6)

        # need tuple here to distinguish from iterable type selection
        self.assertEqual([ih1.loc_to_iloc(tuple(v)) for v in ih1.values],
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
                )



    def test_hierarchy_relabel_a(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'A'),
                ('II', 'B'),
                )

        ih = IndexHierarchy.from_labels(labels)

        ih.relabel({('I', 'B'): ('I', 'C')})

        ih2 = ih.relabel({('I', 'B'): ('I', 'C')})

        self.assertEqual(ih2.values.tolist(),
                [['I', 'A'], ['I', 'C'], ['II', 'A'], ['II', 'B']])

        with self.assertRaises(Exception):
            ih3 = ih.relabel({('I', 'B'): ('I', 'C', 1)})

        ih3 = ih.relabel(lambda x: tuple(e.lower() for e in x))

        self.assertEqual(
                ih3.values.tolist(),
                [['i', 'a'], ['i', 'b'], ['ii', 'a'], ['ii', 'b']])



    def test_hierarchy_intersection_a(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'A'),
                ('II', 'B'),
                )

        ih1 = IndexHierarchy.from_labels(labels)

        labels = (
                ('II', 'A'),
                ('II', 'B'),
                ('III', 'A'),
                ('III', 'B'),
                )

        ih2 = IndexHierarchy.from_labels(labels)

        post = ih1.intersection(ih2)
        self.assertEqual(post.values.tolist(),
                [['II', 'A'], ['II', 'B']])

        post = ih1.union(ih2)
        self.assertEqual(post.values.tolist(),
                [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B'], ['III', 'A'], ['III', 'B']])



    def test_hierarchy_operators_a(self):

        labels = (
                (1, 1),
                (1, 2),
                (2, 1),
                (2, 2),
                )
        ih1 = IndexHierarchy.from_labels(labels)

        self.assertEqual((ih1*2).tolist(),
                [[2, 2], [2, 4], [4, 2], [4, 4]])

        self.assertEqual((-ih1).tolist(),
                [[-1, -1], [-1, -2], [-2, -1], [-2, -2]])


    def test_hierarchy_flat_a(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'A'),
                ('II', 'B'),
                )

        ih = IndexHierarchy.from_labels(labels)
        self.assertEqual(ih.flat().values.tolist(),
                [('I', 'A'), ('I', 'B'), ('II', 'A'), ('II', 'B')]
                )

    def test_hierarchy_add_level_a(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'A'),
                ('II', 'B'),
                )

        ih = IndexHierarchy.from_labels(labels)
        ih2 = ih.add_level('b')

        self.assertEqual(ih2.values.tolist(),
                [['b', 'I', 'A'], ['b', 'I', 'B'], ['b', 'II', 'A'], ['b', 'II', 'B']])
        self.assertEqual([ih2.loc_to_iloc(tuple(x)) for x in ih2.values],
                [0, 1, 2, 3])



    def test_hierarchy_drop_level_a(self):

        labels = (
                ('I', 'A', 1),
                ('I', 'B', 1),
                ('II', 'A', 1),
                ('II', 'B', 2),
                )

        ih = IndexHierarchy.from_labels(labels)
        ih2 = ih.drop_level(-1)

        self.assertEqual(ih2.values.tolist(),
                [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B']])



    def test_hierarchy_drop_level_b(self):

        labels = (
                ('I', 'A', 1),
                ('I', 'B', 1),
                ('II', 'C', 1),
                ('II', 'C', 2),
                )

        ih = IndexHierarchy.from_labels(labels)
        ih2 = ih.drop_level(1)
        self.assertEqual(ih2.values.tolist(),
            [['A', 1], ['B', 1], ['C', 1], ['C', 2]])

        with self.assertRaises(KeyError):
            ih2.drop_level(1)

    def test_hierarchy_drop_level_c(self):

        labels = (
                ('I', 'A', 1),
                ('I', 'B', 2),
                ('II', 'C', 3),
                ('II', 'C', 4),
                )

        ih = IndexHierarchy.from_labels(labels)
        self.assertEqual(ih.drop_level(1).values.tolist(),
                [['A', 1], ['B', 2], ['C', 3], ['C', 4]])

    def test_hierarchy_drop_level_d(self):

        labels = (
                ('A', 1),
                ('B', 2),
                ('C', 3),
                ('C', 4),
                )

        ih = IndexHierarchy.from_labels(labels)
        self.assertEqual(ih.drop_level(1).values.tolist(),
                [1, 2, 3, 4])


    def test_hierarchy_boolean_loc(self):
        records = (
                ('a', 999999, 0.1),
                ('a', 201810, 0.1),
                ('b', 999999, 0.4),
                ('b', 201810, 0.4))
        f1 = Frame.from_records(records, columns=list('abc'))

        f1 = f1.set_index_hierarchy(['a', 'b'], drop=False)

        f2 = f1.loc[f1['b'] == 999999]

        self.assertEqual(f2.to_pairs(0),
                (('a', ((('a', 999999), 'a'), (('b', 999999), 'b'))), ('b', ((('a', 999999), 999999), (('b', 999999), 999999))), ('c', ((('a', 999999), 0.1), (('b', 999999), 0.4)))))

        f3 = f1.loc[Series([False, True], index=(('b', 999999), ('b', 201810)))]
        self.assertEqual(f3.to_pairs(0),
                (('a', ((('b', 201810), 'b'),)), ('b', ((('b', 201810), 201810),)), ('c', ((('b', 201810), 0.4),))))


    def test_hierarchy_name_a(self):

        idx1 = IndexHierarchy.from_product(list('ab'), list('xy'), name='q')
        self.assertEqual(idx1.name, 'q')

        idx2 = idx1.rename('w')
        self.assertEqual(idx2.name, 'w')


    def test_hierarchy_name_b(self):

        idx1 = IndexHierarchyGO.from_product(list('ab'), list('xy'), name='q')
        idx2 = idx1.rename('w')

        self.assertEqual(idx1.name, 'q')
        self.assertEqual(idx2.name, 'w')

        idx1.append(('c', 'c'))
        idx2.append(('x', 'x'))

        self.assertEqual(
                idx1.values.tolist(),
                [['a', 'x'], ['a', 'y'], ['b', 'x'], ['b', 'y'], ['c', 'c']]
                )

        self.assertEqual(
                idx2.values.tolist(),
                [['a', 'x'], ['a', 'y'], ['b', 'x'], ['b', 'y'], ['x', 'x']]
                )

    def test_hierarchy_display_a(self):

        idx1 = IndexHierarchy.from_product(list('ab'), list('xy'), name='q')

        match = tuple(idx1.display(DisplayConfig(type_color=False)))

        self.assertEqual(
                match,
                (['<IndexHierarchy: q>', ''], ['a', 'x'], ['a', 'y'], ['b', 'x'], ['b', 'y'], ['<<U1>', '<<U1>'])
                )

    def test_hierarchy_to_pandas_a(self):

        idx1 = IndexHierarchy.from_product(list('ab'), list('xy'), name='q')

        pdidx = idx1.to_pandas()
        # NOTE: pandas .values on a hierarchical index returns an array of tuples
        self.assertEqual(
                idx1.values.tolist(),
                [list(x) for x in pdidx.values.tolist()])



    def test_hierarchy_from_pandas_a(self):
        import pandas

        pdidx = pandas.MultiIndex.from_product((('I', 'II'), ('A', 'B')))

        idx = IndexHierarchy.from_pandas(pdidx)

        self.assertEqual(idx.values.tolist(),
                [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B']]
                )


    def test_hierarchy_from_pandas_b(self):
        import pandas

        idx = IndexHierarchy.from_product(('I', 'II'), ('A', 'B'), (1, 2))

        self.assertEqual(list(idx.iter_label(0)), ['I', 'II'])
        self.assertEqual(list(idx.iter_label(1)), ['A', 'B', 'A', 'B'])
        self.assertEqual(list(idx.iter_label(2)), [1, 2, 1, 2, 1, 2, 1, 2])

        post = idx.iter_label(1).apply(lambda x: x.lower())
        self.assertEqual(post.to_pairs(),
                ((0, 'a'), (1, 'b'), (2, 'a'), (3, 'b')))



    def test_hierarchy_from_pandas_c(self):
        import pandas

        pdidx = pandas.MultiIndex.from_product((('I', 'II'), ('A', 'B')))

        idx = IndexHierarchyGO.from_pandas(pdidx)

        self.assertEqual(idx.values.tolist(),
                [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B']]
                )

        self.assertEqual(idx.values.tolist(),
                [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B']])

        idx.append(('III', 'A'))

        self.assertEqual(idx.values.tolist(),
                [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B'], ['III', 'A']])


    def test_hierarchy_copy_a(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'A'),
                ('II', 'B'),
                )

        ih1 = IndexHierarchy.from_labels(labels)
        ih2 = ih1.copy()

        self.assertEqual(ih2.values.tolist(),
            [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B']])



    def test_hierarchy_copy_b(self):

        labels = (
                ('I', 'A'),
                ('I', 'B'),
                ('II', 'A'),
                ('II', 'B'),
                )

        ih1 = IndexHierarchyGO.from_labels(labels)
        ih2 = ih1.copy()
        ih2.append(('II', 'C'))

        self.assertEqual(ih2.values.tolist(),
            [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B'], ['II', 'C']]
            )

        self.assertEqual(ih1.values.tolist(),
            [['I', 'A'], ['I', 'B'], ['II', 'A'], ['II', 'B']]
            )


    def test_hierarchy_cumprod_a(self):

        ih1 = IndexHierarchy.from_product((10, 20), (3, 7))

        # sum applies to the labels
        self.assertEqual(ih1.sum().tolist(),
                [60, 20]
                )

        self.assertEqual(ih1.cumprod().tolist(),
                [[10, 3], [100, 21], [2000, 63], [40000, 441]]
                )

if __name__ == '__main__':
    unittest.main()


