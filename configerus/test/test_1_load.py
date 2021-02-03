"""

Test config construction

Simple tests that ensure that the Config construction isn't broken

"""

import unittest
import logging

logger = logging.getLogger("basic_construct")
logger.setLevel(level=logging.INFO)

import configerus

class BasicConstruct(unittest.TestCase):

    def test_construct_1_naked(self):
        """ just make sure we can create a Configs object, without any bootstraps """
        config = configerus.new_config(bootstraps=[])

    def test_construct_2_single_bootstrap(self):
        """ make sure we can create a Configs object, without a single bootstrap """
        config = configerus.new_config(bootstraps=['dict'])

    def test_construct_3_bootsraps(self):
        """ Make sure we can create a Configs object, with default bootstraps """
        config = configerus.new_config()

if __name__ == '__main__':
    unittest.main()
