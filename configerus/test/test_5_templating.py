"""

Test config templating

Here we run some simple config template checking to make sure that template
substitution of whole and partial values works.

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
        "name": "source",
        "priority": 30,
        "type": PLUGIN_ID_CONFIGSOURCE_DICT,
        "data": {
            "config": {
                "1": "first 1",
                "2": {
                    "1": "first 2.1"
                },
                "3": {
                    "1": {
                        "1": "first 3.1.1",
                        "2": "first 3.1.2"
                    },
                    "2": {
                        "1": "first 3.2.1",
                        "2": "first 3.2.2"
                    }
                }
            },
            "variables": {
                "one": "first one",
                "two": "first two",
                "three": 3,
                "four": {
                    "1": "first four.1"
                }
            }
        }
    },
    {
        "name": "simple",
        "priority": 80,
        "type": PLUGIN_ID_CONFIGSOURCE_DICT,
        "data": {
            "config": {
                "10": "{2}",
                "11": "__{2}__"
            }
        }
    },
    {
        "name": "defaults",
        "priority": 80,
        "type": PLUGIN_ID_CONFIGSOURCE_DICT,
        "data": {
            "config": {
                "20": "{does.not.exist?default}",
                "21": "{does.not.exist}",
                "22": "{variables:does.not.exist?megadefault}",
                "23": "{variables:three?default}",
            }
        }
    },
    {
        "name": "special",
        "priority": 80,
        "type": PLUGIN_ID_CONFIGSOURCE_DICT,
        "data": {
            "config": {
                "30": "{path:replace}",
            }
        }
    },
    {
        "name": "deep",
        "priority": 80,
        "type": PLUGIN_ID_CONFIGSOURCE_DICT,
        "data": {
            "config": {
                "40": "deep 40",
                "41": "{40}",
                "42": {
                    "1": "{40}",
                    "2": {
                        "1": "{40}"
                    }
                }
            }
        }
    },
    {
        "name": "replace",
        "priority": 80,
        "type": PLUGIN_ID_CONFIGSOURCE_PATH,
        "data": {
            "replace.json": {
                "id": "test"
            }
        }
    }
]
""" Contents of test config files used as the source for a config object """

""" TESTS """

class ConfigTemplating(unittest.TestCase):

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

    def test_format_sane(self):
        """ simple template replacing using format """

        assert self.config.format('{1}', 'config') == "first 1"
        assert self.loaded_config.format('{1}') == "first 1"
        """ Simple formatting at the config and loadedconfig level """


    def test_format_dot_notation(self):
        """ test that format catches dot notation """

        assert self.config.format('{2.1}', 'config') == "first 2.1"
        assert self.config.format('{3.2.1}', 'config') == "first 3.2.1"
        """ Simple dot notation descending format """

    def test_missing_raises_exceptions(self):
        """ missing values should raise exceptions """

        try:
            assert self.config.format("{does.not.exist}", 'config') == "why-no-exception?"
        except KeyError:
            return

        assert False, "Expected exception"

    def test_format_embedding_and_casting(self):
        """ simple template replacing using format """

        assert self.config.format('12345{1}67890', 'config') == "12345first 167890"
        assert self.config.format('1 23 45 {1}6 78 90', 'config') == "1 23 45 first 16 78 90"
        """ format replacements in the middle of a string """

        assert self.config.format('{2}', 'config') == {"1": "first 2.1"}
        assert self.config.format(' {2} ', 'config') == " {'1': 'first 2.1'} "
        """ format should string cast only not full matches """

    def test_format_with_sources(self):
        """ test that sources work with format """

        variables_two = self.config.format("{two}", 'variables')
        assert variables_two, "Except value for comparison"
        assert self.config.format("{variables:two}", 'config') == variables_two
        assert self.config.format("{variables:two}", 'variables') == variables_two
        """ specifying a source should work """

    def test_format_with_defaults(self):
        """ test the defaulting with formatting """

        assert self.config.format("{does.not.exist?default1}", 'config') == 'default1'
        assert self.config.format("{variables:does.not.exist?default2}", 'config') == 'default2'
        """ defaults should apply """

        variables_two = self.config.format("{two}", 'variables')
        assert variables_two, "Except value for comparison"
        assert self.config.format("{variables:two?default}", 'config') == variables_two
        """ defaults should not overwrite values that can be found """

    def test_get_formatted(self):
        """ test that loadedconfig gets format """

        config_one =self.loaded_config.get("1")
        assert config_one, "Expected value for comparison"
        assert self.config.format('{1}', 'config') == config_one
        """ get should mimic format behaviour, which we tested above """

        variables_three =self.loaded_variables.get("three")
        assert config_one, "Expected value for comparison"
        assert self.loaded_config.format("{variables:three}") == variables_three
        """ test templating for different sources """

        assert self.loaded_config.get("20") == 'default'
        assert self.loaded_config.get("22") == 'megadefault'
        assert self.loaded_config.get("23") == variables_three

        try:
            assert self.loaded_config.get("21")
        except:
            return
        assert False, "expected exception"

    def test_deep_formatting(self):
        """ test that formatting is applied deeply """

        config_fourty =self.loaded_config.get("40")
        assert config_fourty, "Expected value for comparison"

        assert self.loaded_config.get("41") == config_fourty
        assert self.loaded_config.get("42")["1"] == config_fourty
        assert self.loaded_config.get("42")["2"]["1"] == config_fourty
