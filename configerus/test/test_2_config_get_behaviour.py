"""
test_config

Unit and functional testing for the config handler

Here we test that config can load() and get() config and that those operations
behave as expected.
To get some good coverage we try to use both the DICT and PATH based config
plugins.  To do that we define a list of config and use a configerus.test
utility method which turns the PATH content into files in a temp directory
before adding it to the config object.
This makes this test harder to read, but it is a clean way to get better tests.

"""
import logging
import unittest

import configerus
from configerus.loaded import LOADED_KEY_ROOT
from configerus.contrib.env import PLUGIN_ID_SOURCE_ENV
from configerus.contrib.dict import PLUGIN_ID_SOURCE_DICT
from configerus.contrib.files import PLUGIN_ID_SOURCE_PATH

from configerus.test import make_test_config, test_config_cleanup

logger = logging.getLogger("test_config_behaviour")
logger.setLevel(logging.INFO)

config_sources = [
    {
        'name': 'first',
        'priority': 30,
        'type': PLUGIN_ID_SOURCE_DICT,
        'data': {
            'config': {
                '1': "first 1"
            },
            'variables': {
                'one': "first one",
                'two': "first two"
            }
        }
    },
    {
        'name': 'second',
        'priority': 20,
        'type': PLUGIN_ID_SOURCE_PATH,
        'data': {
            'config.json': {
                '1': "second 1",
                '2': "second 2"
            },
            'variables.json': {
                'one': "second one",
                'two': "second two"
            }
        }
    },
    {
        'name': 'third',
        'priority': 40,
        'type': PLUGIN_ID_SOURCE_PATH,
        'data': {
            'config.yaml': {
                '3': {
                    '1': "third 3.1",
                    '2': {
                        '1': "third 3.2.1",
                        '2': "third 3.2.2"
                    }
                },
                '4': {
                    '1': "third 4.1"
                },
                '5': "third 5"
            }
        }
    },
    {
        'name': 'fourth',
        'priority': 75,
        'type': PLUGIN_ID_SOURCE_PATH,
        'data': {
            'config.json': {
                '4': "fourth 4"
            }
        }
    },
    {
        'name': 'fifth',
        'priority': 75,
        'type': PLUGIN_ID_SOURCE_PATH,
        'data': {
            'config.json': {
                '5': "fifth 5",
                '6': "fifth 6"
            }
        }
    },
    {
        'name': 'sixth',
        'priority': 75,
        'type': PLUGIN_ID_SOURCE_PATH,
        'data': {
            'config.json': {
                '6': {
                    '1': "sixth 6.1"
                }
            }
        }
    },
    {
        'name': 'seventh',
        'priority': 85,
        'type': PLUGIN_ID_SOURCE_PATH,
        'data': {
            'config.json': {
                '5': "seventh 5 json",
                '6': "seventh 6 json"
            },
            'config.yaml': {
                '5': "seventh 5 yaml",
                '6': "seventh 6 yaml",
                '7': {
                    '1': ['1']
                }
            }
        }
    },
    {
        'name': 'eighth',
        'priority': 85,
        'type': PLUGIN_ID_SOURCE_ENV,
        'data': {
            'env_one': "env eighth env one",
            'env_two_one': "env eighth env two.one",
        }
    }
]
""" Contents of test config files used as the source for a config object """

""" TESTS """


class ConfigBehaviour(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ make a Config test object from some inline data

        First this dumps the data into json files, and then points the config object
        to the various paths for loading. The data can then be used to test funct.
        The data contains only values that are usefull for confirming that config
        behaviour is as expected, and is not meant to be useful.

        We also preload some of the config
        """

        logger.debug("Building empty config object")
        config = configerus.new_config()
        make_test_config(config, config_sources)
        cls.config = config
        cls.loaded_config = config.load('config')
        cls.loaded_variables = config.load('variables')

    @classmethod
    def tearDownClass(cls):
        test_config_cleanup(cls.config)

    def test_source_env_basic(self):
        """ test the env source basically """
        all_env = self.config.load('env')
        self.assertIsNotNone(all_env.get('one'))
        self.assertEqual(all_env.get('one'), "env eighth env one")
        self.assertEqual(all_env.get('two.one'), "env eighth env two.one")

    def test_basic_combined(self):
        """ test some basic file combining by the config object """

        self.assertEqual(self.loaded_config.get('1'), "first 1")
        self.assertEqual(self.loaded_config.get('2'), "second 2")

    def test_dot_notation(self):
        """ Confirm that we can retrieve data using the dot notation """

        self.assertEqual(self.loaded_config.get('3.1'), "third 3.1")

    def test_overrides(self):
        """ confirm that keys defined in more than one source get overriden """

        self.assertEqual(self.loaded_config.get('4'), "fourth 4")
        self.assertIsNone(self.loaded_config.get('5.1', exception_if_missing=False))
        self.assertEqual(self.loaded_config.get('5'), "seventh 5 json")

    def test_get_multiple_keys(self):
        """ test the the loaded get of various key formats """

        third_3_base = self.loaded_config.get('3')
        third_3_2 = self.loaded_config.get('3.2')
        third_3_2_1 = self.loaded_config.get('3.2.1')

        # sanity check on the comparison values
        self.assertIsNotNone(third_3_base)
        self.assertIsInstance(third_3_base, dict)
        self.assertIsInstance(third_3_2, dict)
        self.assertEqual(third_3_2_1, "third 3.2.1")

        # pull some values with a base
        third_3_base_A = self.loaded_config.get(['3', '2'])
        third_3_base_B = self.loaded_config.get(['3', '2.1'])
        third_3_base_C = self.loaded_config.get(['3', ['2', '1']])
        third_3_base_D = self.loaded_config.get([['3', '2'], '1'])

        self.assertEqual(third_3_2, third_3_base_A)
        self.assertEqual(third_3_2_1, third_3_base_B)
        self.assertEqual(third_3_2_1, third_3_base_C)
        self.assertEqual(third_3_2_1, third_3_base_D)

        # Load with some root keys involved
        third_root_base_3 = self.loaded_config.get([LOADED_KEY_ROOT, '3'])
        third_3_base_root = self.loaded_config.get([LOADED_KEY_ROOT, '3'])

        self.assertEqual(third_3_base, third_root_base_3)
        self.assertEqual(third_3_base, third_3_base_root)
