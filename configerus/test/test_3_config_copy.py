"""

Test config's copy()

Here we test that the Config object is able to make copies of itself, and that
changing those copies doesn't affect originals.

"""

from configerus.contrib.dict import PLUGIN_ID_SOURCE_DICT
import configerus
import unittest
import logging

logging.basicConfig()
logger = logging.getLogger('config_copy')
logger.setLevel(level=logging.INFO)


""" TESTS """


class ConfigBehaviour(unittest.TestCase):

    def test_copy_safety(self):
        """ Test that config copy allows overloads and doesn't modify the source """

        logger.debug("Building empty config object")
        config = configerus.new_config()

        config.add_source(PLUGIN_ID_SOURCE_DICT, 'orig', 80).set_data({
            'copy': {
                'one': 'orig 1'
            }
        })

        config_copy_orig = config.load('copy')

        copy1 = config.copy()
        copy1.add_source(PLUGIN_ID_SOURCE_DICT, 'copy1', 81).set_data({
            'copy': {
                'one': 'copy1 1',
                'two': 'copy1 2'
            }
        })
        copy2 = config.copy()
        copy2.add_source(PLUGIN_ID_SOURCE_DICT, 'copy2', 82).set_data({
            'copy': {
                'one': 'copy2 1',
                'two': 'copy2 2'
            }
        })

        config_copy_late = config.load('copy')
        config1_copy = copy1.load('copy')
        config2_copy = copy2.load('copy')

        logger.debug('LOADED: AFTER: orig: %s', config_copy_orig.data)
        logger.debug('LOADED: AFTER: 1   : %s', config1_copy.data)
        logger.debug('LOADED: AFTER: 2   : %s', config2_copy.data)
        logger.debug('LOADED: AFTER: late: %s', config_copy_late.data)

        # check original values
        self.assertEqual(config_copy_orig.get('one'), 'orig 1')
        self.assertIsNone(config_copy_orig.get('two'))
        # check that copied config didn't modify original
        self.assertEqual(config_copy_orig.get('one'), config_copy_late.get('one'))
        self.assertEqual(config_copy_orig.get('two'), config_copy_late.get('two'))

        self.assertEqual(config1_copy.get('one'), 'copy1 1')
        self.assertEqual(config1_copy.get('two'), 'copy1 2')
