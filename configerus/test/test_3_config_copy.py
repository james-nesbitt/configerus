"""

Test config's copy()

Here we test that the Config object is able to make copies of itself, and that
changing those copies doesn't affect originals.

"""

import unittest
import logging

logging.basicConfig()
logger = logging.getLogger('config_copy')
logger.setLevel(level=logging.INFO)

import configerus
from configerus.contrib.dict import PLUGIN_ID_CONFIGSOURCE_DICT

""" TESTS """

class ConfigBehaviour(unittest.TestCase):

    def test_copy_safety(self):
        """ Test that config copy allows overloads and doesn't modify the source """

        logger.debug("Building empty config object")
        config = configerus.new_config()

        config.add_source(PLUGIN_ID_CONFIGSOURCE_DICT, 'orig', 80).set_data({
            'copy': {
                'one': 'orig 1'
            }
        })

        config_copy_orig = config.load('copy')

        copy1 = config.copy()
        copy1.add_source(PLUGIN_ID_CONFIGSOURCE_DICT, 'copy1', 80).set_data({
            'copy': {
                'one': 'copy1 1',
                'two': 'copy1 2'
            }
        })
        copy2 = config.copy()
        copy2.add_source(PLUGIN_ID_CONFIGSOURCE_DICT, 'copy2', 81).set_data({
            'copy': {
                'one': 'copy2 1',
                'two': 'copy2 2'
            }
        })

        config_copy_late = config.load('copy')
        config1_copy = copy1.load('copy')
        config2_copy = copy2.load('copy')

        logger.debug('LOADED: AFTER: orig: %s',config_copy_orig.data )
        logger.debug('LOADED: AFTER: 1   : %s',config1_copy.data )
        logger.debug('LOADED: AFTER: 2   : %s',config2_copy.data )
        logger.debug('LOADED: AFTER: late: %s',config_copy_late.data )

        # check original values
        assert config_copy_orig.get('one') == 'orig 1'
        assert config_copy_orig.get('two') == None
        # check that copied config didn't modify original
        assert config_copy_orig.get('one') == config_copy_late.get('one')
        assert config_copy_orig.get('two') == config_copy_late.get('two')

        assert config1_copy.get('one') == 'copy1 1'
        assert config1_copy.get('two') == 'copy1 2'
