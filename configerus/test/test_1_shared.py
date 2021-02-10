"""

Test .sharted functions

Simple tests that ensure that the .shared functionality works

"""

import unittest
import logging

import configerus.shared as shared

logger = logging.getLogger("shared")


class BasicConstruct(unittest.TestCase):

    def test_1_tree_reduce(self):
        """ can we reduce trees to lists """
        tree = ['1', '2', '3']
        self.assertEqual(shared.tree_reduce(tree), tree)

        tree = ['1', '2', ['3', '4']]
        flat = ['1', '2', '3', '4']
        self.assertEqual(shared.tree_reduce(tree, glue='.'), flat)

        tree = ['1', '2', ['3', '4'], [['5'], '6', '7', [[['8']]]]]
        flat = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.assertEqual(shared.tree_reduce(tree, glue='.'), flat)

    def test_2_tree_reduce_ignore(self):
        """ test the tree_reduce respects ignore """
        tree = ['1', '2', ['3', '4'], [['5'], '6', '7', [[['8']]]]]
        ignore = ['2', '4', '7']
        flat = ['1', '3', '5', '6', '8']
        self.assertEqual(shared.tree_reduce(tree, glue='.', ignore=ignore), flat)

    def test_3_tree_reduce_real(self):
        """ some gets that failed once upon a time """
        tree = ['', 'validators']
        ignore = ['', '']
        flat = ['validators']
        self.assertEqual(shared.tree_reduce(tree, glue='.', ignore=ignore), flat)

        tree = [['backend.outputs', 'mke_cluster'], 'validators']
        ignore = ['', '']
        flat = ['backend', 'outputs', 'mke_cluster', 'validators']
        self.assertEqual(shared.tree_reduce(tree, glue='.', ignore=ignore), flat)

    def test_4_tree_get(self):
        """ does tree_get() work with all sorts of messy keys """

        tree = {
            '1': {
                '2': {
                    '3': {
                        '4': 'my value'
                    }
                }
            }
        }

        self.assertEqual(shared.tree_get(tree, '1.2.3'), {'4': 'my value'})
        self.assertEqual(shared.tree_get(tree, '1.2.3.4'), 'my value')
        self.assertEqual(shared.tree_get(tree, '1.2.3.4.'), 'my value')
        self.assertEqual(shared.tree_get(tree, '1.2.3.4'), 'my value')
        self.assertEqual(shared.tree_get(tree, ['1', '2', '3', '4']), 'my value')
        self.assertEqual(shared.tree_get(tree, ['1.2', '3.4']), 'my value')
        self.assertEqual(shared.tree_get(tree, ['1', ['2', '3.4']]), 'my value')

        self.assertEqual(shared.tree_get(tree, ['1', '2', '.', '', '3.', '.4']), 'my value')
        self.assertEqual(shared.tree_get(tree, [['.', ''], '1.2.3.4', '..', ['.', ['.']]]), 'my value')

    def test_5_tree_merge(self):

        source = {
            '1': "source 1",
            '2': "source 2",
            '4': "source 4",
            '5': {
                '1': "source 5.1"
            }
        }
        destination = {
            '3': {
                '1': "destination 3.1",
                '2': {
                    '1': "destination 3.2.1",
                    '2': "destination 3.2.2"
                }
            },
            '4': {
                '1': "third 4.1"
            },
            '5': "third 5"
        }

        merged = shared.tree_merge(source, destination)

        self.assertIsNotNone(merged)
        self.assertEqual(shared.tree_get(merged, '3.1'), "destination 3.1")
        self.assertEqual(shared.tree_get(merged, '4'), "source 4")
        self.assertEqual(shared.tree_get(merged, '5.1'), "source 5.1")

        third = {}

    def test_get_listindexes(self):
        """ can get reach into lists using numberic indexes """

        test_list = [
            '1.2 0',
            '1.2 1',
            '1.2 2',
        ]
        wrapper_dict = {'2': test_list}
        tree = {
            '1': wrapper_dict
        }

        self.assertEqual(shared.tree_get(tree, '1'), wrapper_dict)
        self.assertEqual(shared.tree_get(tree, '1.2'), test_list)
        self.assertEqual(shared.tree_get(tree, '1.2.0'), test_list[0])
        self.assertEqual(shared.tree_get(tree, '1.2.2'), test_list[2])

        with self.assertRaises(IndexError):
            shared.tree_get(tree, '1.2.5')

        with self.assertRaises(ValueError):
            shared.tree_get(tree, '1.2.string')
