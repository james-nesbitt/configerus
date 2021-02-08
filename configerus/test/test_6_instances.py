"""

test the plugin instance functionality

"""
import logging
import unittest

from configerus.config import Config
from configerus.plugin import SourceFactory, FormatFactory, ValidatorFactory, Type
from configerus.instances import PluginInstance, PluginInstances

logger = logging.getLogger("test_instances")

""" register a bunch of dummy plugins which do nothing but can be used for testing """


@SourceFactory(plugin_id='dummy_1')
def plugin_factory_source_1(config: Config, instance_id: str = ''):
    """ create a dummy configsource plugin """
    return DummyPlugin(config, instance_id)


@SourceFactory(plugin_id='dummy_2')
def plugin_factory_source_2(config: Config, instance_id: str = ''):
    """ create a dummy configsource plugin """
    return DummyPlugin(config, instance_id)


@FormatFactory(plugin_id='dummy_1')
def plugin_factory_format_1(config: Config, instance_id: str = ''):
    """ create a dummy formatter plugin """
    return DummyPlugin(config, instance_id)


@FormatFactory(plugin_id='dummy_2')
def plugin_factory_format_2(config: Config, instance_id: str = ''):
    """ create a dummy formatter plugin """
    return DummyPlugin(config, instance_id)


@ValidatorFactory(plugin_id='dummy_1')
def plugin_factory_validate_1(config: Config, instance_id: str = ''):
    """ create a dummy formatter plugin """
    return DummyPlugin(config, instance_id)


@ValidatorFactory(plugin_id='dummy_2')
def plugin_factory_validate_2(config: Config, instance_id: str = ''):
    """ create a dummy formatter plugin """
    return DummyPlugin(config, instance_id)


class DummyPlugin:
    """ Just a placehold plugin object  """

    def __init__(self, config: Config, instance_id: str):
        self.config = config
        self.instance_id = instance_id


class ConfigTemplating(unittest.TestCase):

    def test_instance_struct_sanity(self):
        """ just test that the Instance struct has the properties that we use """
        config = Config()

        instance = PluginInstance(
            plugin_id='dummy',
            instance_id='dummy',
            type=Type.SOURCE,
            priority=60,
            plugin=DummyPlugin(config, 'dummy')
        )

        self.assertEqual(instance.plugin_id, 'dummy')
        self.assertEqual(instance.priority, 60)

    def test_instances_sanity(self):
        """ Test some construction sanity on the instances object """
        config = Config()
        instances = PluginInstances(config.make_plugin)

        self.assertEqual(len(instances), 0)

        instances.add_plugin(Type.SOURCE, 'dummy_1', 'dummy_instance_1', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_1', 'dummy_instance_2', config.default_priority())

        self.assertEqual(len(instances), 2)

    def test_instances_plugin_get_simple(self):
        """ test that we can add plugins and then retrieve them """
        config = Config()
        instances = PluginInstances(config.make_plugin)

        instances.add_plugin(Type.SOURCE, 'dummy_1', 'dummy_instance_1', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_1', 'dummy_instance_2', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_2', 'dummy_instance_3', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_2', 'dummy_instance_4', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_1', 'dummy_instance_5', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_2', 'dummy_instance_6', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_1', 'dummy_instance_7', config.default_priority())

        len(instances) == 7

        get_4 = instances['dummy_instance_4']
        self.assertTrue(get_4)
        self.assertEqual(get_4.instance_id, 'dummy_instance_4')
        self.assertEqual(instances.get_plugin(instance_id='dummy_instance_4').instance_id, 'dummy_instance_4')
        with self.assertRaises(KeyError):
            instances.get_plugin(instance_id='no_such_instance')

    def test_instances_get_plugins(self):
        """ get plugins based on multiple search parameters """
        config = Config()
        instances = PluginInstances(config.make_plugin)

        instances.add_plugin(Type.SOURCE, 'dummy_1', 'dummy_source_1', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_1', 'dummy_source_2', config.default_priority())
        instances.add_plugin(Type.SOURCE, 'dummy_2', 'dummy_instance', config.default_priority())
        instances.add_plugin(Type.FORMATTER, 'dummy_2', 'dummy_formatter_4', config.default_priority())
        instances.add_plugin(Type.FORMATTER, 'dummy_1', 'dummy_formatter_5', config.default_priority())
        instances.add_plugin(Type.FORMATTER, 'dummy_2', 'dummy_formatter_6', config.default_priority())
        instances.add_plugin(Type.VALIDATOR, 'dummy_1', 'dummy_instance', config.default_priority())
        instances.add_plugin(Type.VALIDATOR, 'dummy_2', 'dummy_validator_8', config.default_priority())

        self.assertTrue(instances.has_plugin(instance_id='dummy_formatter_4'))
        self.assertTrue(instances.has_plugin(instance_id='dummy_validator_8'))
        self.assertTrue(instances.has_plugin(instance_id='dummy_formatter_4'))
        self.assertTrue(instances.has_plugin(instance_id='dummy_source_2'))

        self.assertEqual(len(instances.get_instances(type=Type.SOURCE)), 3)
        self.assertEqual(len(instances.get_instances(type=Type.FORMATTER)), 3)
        self.assertEqual(len(instances.get_instances(type=Type.VALIDATOR)), 2)

        self.assertEqual(len(instances.get_instances(type=Type.SOURCE, plugin_id='dummy_1')), 2)
        self.assertEqual(len(instances.get_instances(type=Type.VALIDATOR, plugin_id='dummy_1')), 1)

        # Plugin ID only search should cross type
        self.assertEqual(len(instances.get_instances(plugin_id='dummy_1')), 4)
        # There are no rules against repeated instance_ids
        self.assertEqual(len(instances.get_instances(instance_id='dummy_instance')), 2)
        # no rule against empty filtering (gets sorted instances)
        self.assertEqual(len(instances.get_instances()), len(instances))

    def test_instance_priority_simple(self):
        """ test that retrieving instances sorts """
        config = Config()
        instances = PluginInstances(config.make_plugin)

        starting_range = range(30, 71, 10)
        priority_list = range(70, 29, -10)

        for priority in starting_range:
            instances.add_plugin(Type.SOURCE, 'dummy_1', 'instance_{}'.format(priority), priority)

        instance_list = instances.get_instances(type=Type.SOURCE)
        self.assertEqual(len(instance_list), len(starting_range))

        for index, priority in enumerate(priority_list):
            self.assertEqual(instance_list[index].priority, priority)

        # let's see what happens as things change
        instances.add_plugin(Type.SOURCE, 'dummy_1', 'instance_{}'.format(90), 90)
        instance_list = instances.get_instances(type=Type.SOURCE)

        self.assertEqual(len(instance_list), len(starting_range) + 1)
        self.assertEqual(instance_list[0].priority, 90)
        self.assertEqual(instance_list[1].priority, 70)
        self.assertEqual(instance_list[len(starting_range)].priority, 30)
