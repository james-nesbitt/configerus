"""

Test config templating

Here we run some simple config template checking to make sure that template
substitution of whole and partial values works.

"""
import logging
import unittest
import os.path
import json

import configerus
from configerus.config import CONFIG_PATH_LABEL
from configerus.loaded import LOADED_KEY_ROOT
from configerus.contrib.dict import PLUGIN_ID_SOURCE_DICT
from configerus.contrib.files import PLUGIN_ID_SOURCE_PATH

from configerus.test import make_test_config, test_config_cleanup

logger = logging.getLogger('test_config_behaviour')
logger.setLevel(logging.INFO)

config_sources = [
    {
        'name': 'source',
        'priority': 30,
        'type': PLUGIN_ID_SOURCE_DICT,
        'data': {
            'config': {
                '1': "first 1",
                '2': {
                    '1': "first 2.1"
                },
                '3': {
                    '1': {
                        '1': "first 3.1.1",
                        '2': "first 3.1.2"
                    },
                    '2': {
                        '1': "first 3.2.1",
                        '2': "first 3.2.2"
                    }
                }
            },
            'variables': {
                'one': "first one",
                'two': "first two",
                'three': 3,
                'four': {
                    '1': "first four.1"
                }
            }
        }
    },
    {
        'name': 'simple',
        'priority': 80,
        'type': PLUGIN_ID_SOURCE_DICT,
        'data': {
            'config': {
                '10': "{2}",
                '11': "__{2}__"
            }
        }
    },
    {
        'name': 'defaults',
        'priority': 80,
        'type': PLUGIN_ID_SOURCE_DICT,
        'data': {
            'config': {
                '20': "{does.not.exist?default}",
                '21': "{does.not.exist}",
                '22': "{variables:does.not.exist?megadefault}",
                '23': "{variables:three?default}",
            }
        }
    },
    {
        'name': 'special',
        'priority': 80,
        'type': PLUGIN_ID_SOURCE_DICT,
        'data': {
            'config': {
                '30': "{path:replace}",
            }
        }
    },
    {
        'name': 'deep',
        'priority': 80,
        'type': PLUGIN_ID_SOURCE_DICT,
        'data': {
            'config': {
                '40': "deep 40",
                '41': "{40}",
                '42': {
                    '1': "{40}",
                    '2': {
                        '1': "{40}"
                    }
                }
            }
        }
    },
    {
        'name': 'replace',
        'priority': 80,
        'type': PLUGIN_ID_SOURCE_PATH,
        'data': {
            'replace.json': {
                'id': "test"
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

        cls.loaded_config = config.load('config')
        cls.loaded_variables = config.load('variables')

    @classmethod
    def tearDownClass(cls):
        test_config_cleanup(cls.config)

    def test_format_sane(self):
        """ simple template replacing using format """

        self.assertEqual(self.config.format('{1}', 'config'), "first 1")
        self.assertEqual(self.loaded_config.format('{1}'), "first 1")
        """ Simple formatting at the config and loadedconfig level """

    def test_format_dot_notation(self):
        """ test that format catches dot notation """

        self.assertEqual(self.config.format('{2.1}', 'config'), "first 2.1")
        self.assertEqual(self.config.format('{3.2.1}', 'config'), "first 3.2.1")
        """ Simple dot notation descending format """

    def test_format_embedding_and_casting(self):
        """ simple template replacing using format """

        self.assertEqual(self.config.format('12345{1}67890', 'config'), "12345first 167890")
        self.assertEqual(self.config.format('1 23 45 {1}6 78 90', 'config'), "1 23 45 first 16 78 90")
        """ format replacements in the middle of a string """

        self.assertEqual(self.config.format('{2}', 'config'), {'1': "first 2.1"})
        self.assertEqual(self.config.format(' {2} ', 'config'), " {'1': 'first 2.1'} ")
        """ format should string cast only not full matches """

    def test_format_with_sources(self):
        """ test that sources work with format """

        variables_two = self.config.format("{two}", 'variables')
        self.assertEqual(variables_two, "first two")
        self.assertEqual(self.config.format("{variables:two}", 'config'), variables_two)
        self.assertEqual(self.config.format("{variables:two}", 'variables'), variables_two)
        """ specifying a source should work """

    def test_format_with_defaults(self):
        """ test the defaulting with formatting """

        self.assertEqual(self.config.format("{does.not.exist?default1}", 'config'), 'default1')
        self.assertEqual(self.config.format("{variables:does.not.exist?default2}", 'config'), 'default2')
        """ defaults should apply """

        variables_two = self.config.format("{two}", 'variables')
        self.assertEqual(variables_two, "first two")
        self.assertEqual(self.config.format("{variables:two?default}", 'config'), variables_two)
        """ defaults should not overwrite values that can be found """

    def test_get_formatted(self):
        """ test that loadedconfig gets format """

        config_one = self.loaded_config.get('1')
        self.assertEqual(config_one, "first 1")
        self.assertEqual(self.config.format('{1}', 'config'), config_one)
        """ get should mimic format behaviour, which we tested above """

        variables_three = self.loaded_variables.get('three')
        self.assertEqual(variables_three, 3)
        self.assertEqual(self.loaded_config.format("{variables:three}"), variables_three)
        self.assertEqual(self.loaded_config.format(" {variables:three} "), " {} ".format(variables_three))
        """ test templating for different sources """

        self.assertEqual(self.loaded_config.get('20'), "default")
        self.assertEqual(self.loaded_config.get('22'), "megadefault")
        self.assertEqual(self.loaded_config.get('23'), variables_three)
        """ test the templateing on get() """

    def test_missing_raises_exceptions(self):
        """ missing values should raise exceptions """

        with self.assertRaises(KeyError):
            self.config.format("{does.not.exist}", 'config')
            """ test template fails on missing keys in config format """

        with self.assertRaises(Exception):
            self.loaded_config.format("{does.not.exist}")
            """ test template fails on missing keys in loaded format """

        with self.assertRaises(Exception):
            self.loaded_config.get('21')
            """ test template fails on missing keys in get """

    def test_deep_formatting(self):
        """ test that formatting is applied deeply """

        config_fourty = self.loaded_config.get('40')
        self.assertEqual(config_fourty, "deep 40")

        self.assertEqual(self.loaded_config.get('41'), config_fourty)
        self.assertEqual(self.loaded_config.get('42')['1'], config_fourty)
        self.assertEqual(self.loaded_config.get('42')['2']['1'], config_fourty)

    def test_file_templating(self):
        """ test that file contents can be used as a formatting target """

        replace_config = self.config.load('replace')
        replace_json = replace_config.get(LOADED_KEY_ROOT)

        self.assertIsNotNone(replace_json)

        replace_path = replace_config.format('{paths:replace}')
        self.assertIsNotNone(replace_path)

        replace_full_path = os.path.join(replace_path, 'replace.json')
        with open(replace_full_path) as f:
            replace_json = json.load(f)
        self.assertIsNotNone(replace_json)

        # confirm that a file replace full match works
        self.assertEqual(replace_json, replace_config.format('[file:' + replace_full_path + ']'))
        self.assertEqual(
            ' {} '.format(
                json.dumps(replace_json)), replace_config.format(
                ' [file:' + replace_full_path + '] '))
        # confirm mixed templating
        self.assertEqual(replace_json, replace_config.format('[file:{paths:replace}/replace.json]'))
