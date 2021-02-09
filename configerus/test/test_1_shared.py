"""

Test .sharted functions

Simple tests that ensure that the .shared functionality works

"""

import unittest
import logging

import configerus.shared as shared

logger = logging.getLogger("shared")


class BasicConstruct(unittest.TestCase):

    def test_1_tree_get(self):
        """ does tree_get() work """

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

    def test_2_tree_reduce_simple(self):
        """ can we reduce trees to  dot notation strings """

        tree = ['1', '2', '3']
        self.assertEqual(shared.tree_reduce(tree), '1.2.3')
        self.assertEqual(shared.tree_reduce(tree, glue=':'), '1:2:3')

    def test_3_tree_reduce_nested(self):
        """ can we reduce trees to  dot notation strings """

        tree = ['1', '2', ['3', '4']]
        self.assertEqual(shared.tree_reduce(tree, glue='.'), '1.2.3.4')

        tree = ['1', '2', ['3', '4'], [['5'], '6', '7', [[['8']]]]]
        self.assertEqual(shared.tree_reduce(tree, glue='.'), '1.2.3.4.5.6.7.8')

    def test_3_tree_reduce_ignore(self):
        """ test the tree_reduce respects ignore """

        tree = ['1', '2', ['3', '4'], [['5'], '6', '7', [[['8']]]]]
        ignore = ['2', '4', '7']

        self.assertEqual(shared.tree_reduce(tree, glue='.', ignore=ignore), '1.3.5.6.8')

        tree = [['backend', 'outputs', 'mke_cluster'], 'validators']
        ignore = ['', '']
        self.assertEqual(shared.tree_reduce(tree, glue='.', ignore=ignore), 'backend.outputs.mke_cluster.validators')
