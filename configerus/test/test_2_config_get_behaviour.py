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
from configerus.contrib.dict import PLUGIN_ID_CONFIGSOURCE_DICT
from configerus.contrib.files import PLUGIN_ID_CONFIGSOURCE_PATH

from configerus.test import make_test_config, test_config_cleanup

logger = logging.getLogger("test_config_behaviour")
logger.setLevel(logging.INFO)

config_sources = [
    {
        "name": "first",
        "priority": 30,
        "type": PLUGIN_ID_CONFIGSOURCE_DICT,
        "data": {
            "config": {
                "1": "first 1"
            },
            "variables": {
                "one": "first one",
                "two": "first two"
            }
        }
    },
    {
        "name": "second",
        "priority": 20,
        "type": PLUGIN_ID_CONFIGSOURCE_PATH,
        "data": {
            "config.json": {
                "1": "second 1",
                "2": "second 2"
            },
            "variables.json": {
                "one": "second one",
                "two": "second two"
            }
        }
    },
    {
        "name": "third",
        "priority": 40,
        "type": PLUGIN_ID_CONFIGSOURCE_PATH,
        "data": {
            "config.yaml": {
                "3": {
                    "1": "third 3.1"
                },
                "4": {
                    "1": "third 4.1"
                },
                "5": "third 5"
            }
        }
    },
    {
        "name": "fourth",
        "priority": 75,
        "type": PLUGIN_ID_CONFIGSOURCE_PATH,
        "data": {
            "config.json": {
                "4": "fourth 4"
            }
        }
    },
    {
        "name": "fifth",
        "priority": 75,
        "type": PLUGIN_ID_CONFIGSOURCE_PATH,
        "data": {
            "config.json": {
                "5": "fifth 5",
                "6": "fifth 6"
            }
        }
    },
    {
        "name": "sixth",
        "priority": 75,
        "type": PLUGIN_ID_CONFIGSOURCE_PATH,
        "data": {
            "config.json": {
                "6": {
                    "1": "sixth 6.1"
                }
            }
        }
    },
    {
        "name": "seventh",
        "priority": 85,
        "type": PLUGIN_ID_CONFIGSOURCE_PATH,
        "data": {
            "config.json": {
                "5": "seventh 5 json",
                "6": "seventh 6 json"
            },
            "config.yaml": {
                "5": "seventh 5 yaml",
                "6": "seventh 6 yaml"
            }
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

        cls.loaded_config = config.load("config")
        cls.loaded_variables =config.load("variables")

    @classmethod
    def tearDownClass(cls):
        test_config_cleanup(cls.config)

    def test_basic_combined(self):
        """ test some basic file combining by the config object """

        assert self.loaded_config.get("1") == "first 1"
        assert self.loaded_config.get("2") == "second 2"

    def test_dot_notation(self):
        """ Confirm that we can retrieve data using the dot notation """

        assert self.loaded_config.get("3.1") == "third 3.1"

    def test_overrides(self):
        """ confirm that keys defined in more than one source get overriden """

        assert self.loaded_config.get("4") == "fourth 4"
        assert self.loaded_config.get("5.1", exception_if_missing=False) == None
        assert self.loaded_config.get("5") == "seventh 5 json"
