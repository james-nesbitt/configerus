"""

Test config construction

Simple tests that ensure that the Config construction isn't broken

"""

import unittest
import logging

import configerus
from configerus.config import Config

logger = logging.getLogger("basic_construct")


class BasicConstruct(unittest.TestCase):

    def test_construct_1_naked(self):
        """ just make sure we can create a Configs object, without any bootstraps """
        config = configerus.new_config(bootstraps=[])
        self.assertIsInstance(config, Config)

    def test_construct_2_single_bootstrap(self):
        """ make sure we can create a Configs object, without a single bootstrap """
        configerus.new_config(bootstraps=['dict'])

    def test_construct_3_default_bootsraps(self):
        """ Make sure we can create a Configs object, with default bootstraps """
        configerus.new_config()

    def test_construct_3_bad_bootsraps(self):
        """ Make sure we can create a Configs object, with default bootstraps """
        with self.assertRaises(KeyError):
            configerus.new_config(bootstraps=['I do not exist'])
