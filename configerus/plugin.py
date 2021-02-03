
import functools
import logging
import copy
from enum import Enum, unique

logger = logging.getLogger('configerus.plugin')
# logger.setLevel(level=logging.DEBUG)

@unique
class Type(Enum):
    """ Enumerator to match plugin types to plugin labels """
    CONFIGSOURCE = "configerus.plugin.configsource"
    """ A Config source handler """
    FORMATTER    = "configerus.plugin.formatter"
    """ A string formatter plugin """
    VALIDATOR    = "configerus.plugin.validator"
    """ A data result validator plugin """

class Factory():
    """ Python decorator class for configuerus Plugin factories

    This class should be used to decorate any function which is meant to be a
    factory for plugins.

    If you are writing a plugin factory, decorate it with this class, provide
    the factory type and id values, and then the factory will be avaialble to
    other code.

    If you are trying to get an instance of a plugin, then create an instance of
    this class and use the create() method
    """

    registry = {}
    """ A static list of all of the registered factory functions """

    def __init__(self, type: Type, plugin_id: str):
        """ register the decoration """
        self.plugin_id = plugin_id
        self.type = type

        if not self.type.value in self.registry:
            self.registry[self.type.value] = {}

    def __call__(self, func):
        """ call the decorated function

        Returns:

        wrapped function(config: Config)
        """
        def wrapper(config, instance_id: str):
            logger.debug("plugin factory exec: %s:%s", self.type.value, self.plugin_id)
            return func(config=config, instance_id=instance_id)

        logger.debug("Plugin factory registered `%s:%s`", self.type.value, self.plugin_id)
        self.registry[self.type.value][self.plugin_id] = wrapper
        return wrapper

    def create(self, config, instance_id: str):
        """ Get an instance of a plugin as created by the decorated """
        try:
            factory = self.registry[self.type.value][self.plugin_id]
        except KeyError:
            raise NotImplementedError("Configerus Plugin instance '{}:{}' has not been registered.".format(self.type.value, self.plugin_id))
        # except Exception as e:
        #     raise Exception("Could not create Plugin instance '{}:{}' as the plugin factory produced an exception".format(self.type.value, self.plugin_id)) from e

        return factory(config=config, instance_id=instance_id)


CONFIGERUS_FORMATTER_TYPE = Type.FORMATTER
""" Short cut to the config source plugin type enum """
class FormatFactory(Factory):
    """ Decoration class for registering a config source plugin

    This decorator is just a shortcut to allow skipping identifying the plugin
    type using the core factory decorator class.

    All we do is extend the core Factory plugin and pass in the plugin type
    for formatters.
    """
    def __init__(self, plugin_id: str):
        """ register the decoration """
        super().__init__(CONFIGERUS_FORMATTER_TYPE, plugin_id)


CONFIGERUS_SOURCE_TYPE = Type.CONFIGSOURCE
""" Short cut to the config source plugin type enum """
class SourceFactory(Factory):
    """ Decoration class for registering a config source plugin

    This decorator is just a shortcut to allow skipping identifying the plugin
    type using the core factory decorator class.

    All we do is extend the core Factory plugin and pass in the plugin type
    for formatters.
    """
    def __init__(self, plugin_id: str):
        """ register the decoration """
        super().__init__(CONFIGERUS_SOURCE_TYPE, plugin_id)


CONFIGERUS_VALIDATOR_TYPE = Type.VALIDATOR
""" Short cut to the validate plugin type enum """
class ValidatorFactory(Factory):
    """ Decoration class for registering a validate plugin

    This decorator is just a shortcut to allow skipping identifying the plugin
    type using the core factory decorator class.

    All we do is extend the core Factory plugin and pass in the plugin type
    for formatters.
    """
    def __init__(self, plugin_id: str):
        """ register the decoration """
        super().__init__(CONFIGERUS_VALIDATOR_TYPE, plugin_id)


class PluginInstances:
    """ List of plugins wrapped in the PluginInstance struct so that it can be
        prioritized and managed.
    """

    def __init__(self, config):
        self.instances = []
        """ keep a list of all of the plugins as PluginInstance wrappers

            This mixes plugin types together but but it simplifies management
            and storage of plugins """

        self.config = config
        """ A config object is needed for the plugin factories, and it doesn't
            make sense to use a different config for different plugins """

    def copy(self, new_config):
        """ Make a copy of this plugin list.

        This copies the instance list and by copying every plugin, overriding
        its config and adding it to the new list

        @TODO this is not really very good and should be fixed

        """
        instances_copy = PluginInstances(new_config)
        """A new instance list which we will return after copying over plugins """

        for instance in self.instances:
            plugin_copy = copy.deepcopy(instance.plugin)
            plugin_copy.config = new_config
            instances_copy.instances.append(PluginInstance(instance.type, instance.instance_id, instance.priority, plugin_copy))
        return instances_copy

    def add_plugin(self, type:Type, plugin_id:str, instance_id:str, priority:int):
        """ Create a configerus plugin and add it to the config object

        Parameters:
        -----------

        plugin_id (str) : id of the plugin as registered using the plugin
            factory decorater. This has to match a plugin's registration with

        instance_id (str) : Optionally give a plugin instance a name, which it
            might use for internal functionality.
            The "path" source plugin allows string template substitution of the
            "__paths__:instance_id" for the path.

        priority (int) : plugin priority. Use this to set this plugins as
            higher or lower priority than others.

        Returns:
        --------

        Returns the plugin so that you can do any actions to the plugin that it
        supports, and the code here doesn't need to get fancy with function
        arguments

        """
        if not plugin_id:
            raise KeyError("Could not create a plugin as an invalid plugin_id was given: '{}'".format(plugin_id))

        if not type:
            raise KeyError("Could not create a plugin as an invalid type was given: '{}'".format(plugin_id))

        if not instance_id:
            # generate some kind of unique instance_id key
            base_instance_id = "{}_{}".format(type.value, plugin_id)
            index = 1
            instance_id = "{}_{}".format(base_instance_id, index)
            while self.has_plugin(instance_id):
                index = 1
                instance_id = "{}_{}".format(base_instance_id, index)

        if self.has_plugin(instance_id, plugin_id):
            self.warn("Replacing '{}.{}' with new plugin instance".format(plugin_id, instance_id))

        try:
            fac = Factory(type, plugin_id)
            plugin = fac.create(self.config, instance_id)
            instance = PluginInstance(type, instance_id, priority, plugin)

        except NotImplementedError as e:
            raise NotImplementedError("Could not create configerus plugin '{}:{}' as that plugin_id could not be found.".format(type.value, plugin_id)) from e

        self.instances.append(instance)
        return plugin

    def get_plugin(self, instance_id, type:Type=None, exception_if_missing: bool=True):
        """ Retrieve a plugin from its instance_id, optionally of a specific type """
        for plugin_instance in self.instances:
            if plugin_instance.instance_id==instance_id and (type==None or type==plugin_instance.type):
                return plugin_instance.plugin

        if exception_if_missing:
            raise KeyError("Could not find plugin {}".format(instance_id if type is None else "{}:{}".format(type.value, instance_id)))
        return False

    def has_plugin(self, instance_id, type:Type=None):
        """ Discover if a plugin had been added with an instance_id, optionally
            of a specific type """
        return bool(self.get_plugin(instance_id, type, exception_if_missing=False))

    def get_ordered_plugins(self, type:Type=None):
        """ order plugin, optionally just one type, by their top down priority

        we process the plugins in three steps:
        1. Optionally filter for type
        2. sort based on priority
        3. collect just the instance plugin objects

        """
        typed_instances = [instance for instance in self.instances if (type is None or instance.type==type)]
        sorted_instances = sorted(typed_instances, key=lambda instance: instance.priority)
        sorted_instances.reverse()
        return [instance.plugin for instance in sorted_instances]

class PluginInstance:
    """ a struct for a plugin instance that also keeps metadata about the instance """

    def __init__(self, type:Type, instance_id:str, priority:int, plugin):
        self.type = type
        self.instance_id = instance_id
        self.priority = priority
        self.plugin = plugin
