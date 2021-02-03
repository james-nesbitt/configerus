"""

Test config validation

Here we run some simple config validation on both load() and get() operations
using the configerus.contric.jsonscheme validator plugin.

"""

import unittest
import logging

logging.basicConfig()
logger = logging.getLogger('validate')
logger.setLevel(level=logging.INFO)

import configerus
from configerus.contrib.dict import PLUGIN_ID_CONFIGSOURCE_DICT
from configerus.contrib.jsonschema import PLUGIN_ID_VALIDATE_JSONSCHEMA

""" TESTS """

class JsonSchemaValidate(unittest.TestCase):
    """ Some simple validation testing usinf jsonschema """

    # examples from https://python-jsonschema.readthedocs.io/en/stable/
    valid_instance = {"name" : "Eggs", "price" : 34.99}
    invalid_instance = {"name" : "Eggs", "price" : "Invalid"}
    instance_schema = {
        "type" : "object",
        "properties" : {
            "price" : {"type" : "number"},
            "name" : {"type" : "string"},
        }
    }

    def _simple_validate_config(self):
        """ use a common config across some tests """

        logger.debug("Building jsonschema config object")
        config = configerus.new_config()
        config.add_validator(PLUGIN_ID_VALIDATE_JSONSCHEMA)
        config.add_source(PLUGIN_ID_CONFIGSOURCE_DICT).set_data({
            'valid_load_test': self.valid_instance,
            'invalid_load_test': self.invalid_instance,
            'get_test': {
                'valid': self.valid_instance,
                '1': {
                    'invalid': self.invalid_instance
                }
            },
            'jsonschema': {
                'instance': self.instance_schema
            }
        })

        return config

    def test_validate_jsonschema_load_valid(self):
        """ just do a minimal jsonschema validation """

        config = self._simple_validate_config()
        load_config = config.load('valid_load_test', validator='jsonschema:instance')

    def test_validate_jsonschema_load_invalid(self):
        """ just do a minimal jsonschema validation """

        config = self._simple_validate_config()
        try:
            load_config = config.load('invalid_load_test', validator='jsonschema:instance')
        except Exception:
            return
        assert False, "Expected validation exception did not occur"

    def test_validate_jsonschema_get(self):
        """ just do a minimal jsonschema validation """

        config = self._simple_validate_config()
        test_config = config.load('get_test')

        # this should be valid
        valid_instance = test_config.get('valid', validator='jsonschema:instance')

        try:
            # this should be invalid
            invalid_instance = test_config.get('1.invalid', validator='jsonschema:instance')
        except Exception:
            return
        assert False, "Expected validation exception did not occur"
