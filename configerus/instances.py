"""

Plugin Instance managements

This was separated from the plugin module to keep it shorter.  Here we keep
tools for centrally managing plugins and lists of plugins.

"""
import logging
from typing import List

logger = logging.getLogger('configerus.instance')


class PluginInstances:
    """ List of plugins wrapped in the PluginInstance struct so that it can be
        prioritized and managed.

        Question: Why take a factory/copy function instead of just building here?
        Answer: this functionality ended up being useful as an export but was
            limited in reusability without dynamic construction and copying
    """

    def __init__(self, plugin_factory):
        """
        Parameters:
        -----------

        plugin_factory (Callable) : function to product new plugin objects on
            request.

            signature is:
                plugin_factory(type, plugin_id, instance_id, priority)

        """
        self.instances = []
        """ keep a list of all of the plugins as PluginInstance wrappers

            This mixes plugin types together but but it simplifies management
            and storage of plugins """

        self.plugin_factory = plugin_factory
        """ A factory method to produce new plugins """

    def copy(self, new_plugin_factory, plugin_copier):
        """ Make a copy of this plugin list.

        This copies the instance list and by copying every plugin, overriding
        its config and adding it to the new list

        Parameters:
        -----------

        new_plugin_factory (Callable) : a new callable to replace the one for this
            instance.

        plugin_copier (Callable) : a callable which should accept the plugin
            object, and produce a copy of it.

        Returns:
        --------

        A copy of this InstanceList, with copies of all of the PluginInstance
        instances with copies of the plugins.
        Changing/Using the copy should not affect the original.

        """
        instances_copy = PluginInstances(new_plugin_factory)
        """A new instance list which we will return after copying over plugins """

        for instance in self.instances:
            plugin_copy = plugin_copier(instance.plugin)
            instances_copy.instances.append(
                PluginInstance(
                    instance.type,
                    instance.plugin_id,
                    instance.instance_id,
                    instance.priority,
                    plugin_copy))
        return instances_copy

    def add_plugin(self, type: str, plugin_id: str, instance_id: str, priority: int) -> object:
        """ Create a plugin and add it to the list

        Parameters:
        -----------

        type (str) : plugin type as a string (used for filtering)

        plugin_id (str) : id of the plugin as registered using the plugin
            factory decorater. This has to match a plugin's registration with

        instance_id (str) : Optionally give a plugin instance a name, which it
            might use for internal functionality.

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
            # ask our factory to create the new plugin
            plugin_factory = self.plugin_factory
            plugin = plugin_factory(type=type, plugin_id=plugin_id, instance_id=instance_id, priority=priority)
            instance = PluginInstance(type, plugin_id, instance_id, priority, plugin)

        except NotImplementedError as e:
            raise NotImplementedError(
                "Could not create configerus plugin '{}:{}' as that plugin_id could not be found.".format(
                    type.value, plugin_id)) from e

        self.instances.append(instance)
        return plugin

    def __len__(self) -> int:
        """ Return how many plugin instances we have """
        return len(self.instances)

    def __getitem__(self, instance_id: str) -> object:
        """ Handle subscription request

        For subscriptions assume that an instance_id is being retrieved and that
        a plugin is desired for return.

        Parameters:
        -----------

        instance_id (str) : Instance instance_id to look for

        Returns:

        Plugin object for highest priority plugin with the matching instance_id

        Raises:
        -------

        KeyError if the key cannot be matched,

        """
        return self.get_plugin(instance_id=instance_id)

    """ Accessing plugins """

    def get_plugin(self, plugin_id: str = '', instance_id: str = '',
                   type: str = '', exception_if_missing: bool = True) -> object:
        """ Retrieve the highest priority matching plugin

        Parameters:
        -----------

        instance_id (str) : plugin Instance intance_id for matching
        plugin_id (str) : plugin Instance plugin_id for matching
        type (Type) : plugin Instance type for matching

        All filter parameters are optional.  Asking for none retrieves just the
        highest priority plugin.

        Returns:
        --------

        Highest priority matching plugin object

        """
        instance = self.get_instance(plugin_id=plugin_id, instance_id=instance_id, type=type,
                                     exception_if_missing=exception_if_missing)

        if instance is not None:
            return instance.plugin

    def get_plugins(self, plugin_id: str = '', instance_id: str = '',
                    type: str = '', exception_if_missing: bool = True) -> object:
        """ Retrieve matching plugins

        Parameters:
        -----------

        instance_id (str) : plugin Instance intance_id for matching
        plugin_id (str) : plugin Instance plugin_id for matching
        type (Type) : plugin Instance type for matching

        All filter parameters are optional.  Asking for none retrieves just the
        highest priority plugin.

        Returns:
        --------

        List of sorted matching plugin objects

        """
        instances = self.get_instances(plugin_id=plugin_id, instance_id=instance_id, type=type)

        if not instances:
            if exception_if_missing:
                raise KeyError("Could not find any matching plugins[{}][{}][{}]".format(
                    plugin_id, instance_id, type))
            return []

        return [instance.plugin for instance in instances]

    def has_plugin(self, plugin_id: str = '', instance_id: str = '', type: str = '') -> bool:
        """ does a matching plugin exist

        Parameters:
        -----------

        instance_id (str) : plugin Instance intance_id for matching
        plugin_id (str) : plugin Instance plugin_id for matching
        type (Type) : plugin Instance type for matching

        All filter parameters are optional.  Asking for none retrieves just the
        highest priority plugin.

        Returns:
        --------

        bool if a plugin match can be found

        """
        return bool(len(self.get_instances(plugin_id=plugin_id, instance_id=instance_id, type=type)))

    def get_instance(self, plugin_id: str = '', instance_id: str = '',
                     type: str = '', exception_if_missing: bool = True) -> 'PluginInstance':
        """ Retrieve amatching instance

        Parameters:
        -----------

        instance_id (str) : plugin Instance intance_id for matching
        plugin_id (str) : plugin Instance plugin_id for matching
        type (Type) : plugin Instance type for matching

        All filter parameters are optional.  Asking for none retrieves just the
        highest priority plugin.

        Returns:
        --------

        the highest priority matching Instance object

        """
        try:
            sorted_and_filtered = self.get_instances(plugin_id=plugin_id, instance_id=instance_id, type=type)
            return sorted_and_filtered[0]
        except (IndexError, KeyError) as e:
            if exception_if_missing:
                raise KeyError(
                    "No instances matched filter requirements [{}][{}][{}]".format(
                        plugin_id, instance_id, type)) from e
            else:
                logger.debug("No instances matched for filter requirements")

    def get_instances(self, plugin_id: str = '', instance_id: str = '',
                      type: str = '') -> List['PluginInstance']:
        """ filter and order plugins by their top down priority

        Parameters:
        -----------

        instance_id (str) : plugin Instance intance_id for matching
        plugin_id (str) : plugin Instance plugin_id for matching
        type (Type) : plugin Instance type for matching

        All filter parameters are optional.  Asking for none retrieves just the
        highest priority plugin.

        Returns:
        --------

        List of filtered and sorted PluginInstance objects

        """
        matched_instances = []
        for plugin_instance in self.instances:
            if plugin_id and not plugin_instance.plugin_id == plugin_id:
                continue
            elif instance_id and not plugin_instance.instance_id == instance_id:
                continue
            elif type and not type == plugin_instance.type:
                continue

            matched_instances.append(plugin_instance)

        if not len(matched_instances):
            # no need to put more work into it if we have no instances
            return []

        # sort from high to low (avoid divide by zero)
        sorted_instances = sorted(matched_instances, key=lambda instance: 1 /
                                  instance.priority if instance.priority > 1 else 1)
        return sorted_instances


class PluginInstance:
    """ a struct for a plugin instance that also keeps metadata about the instance """

    def __init__(self, type: str, plugin_id: str, instance_id: str, priority: int, plugin):
        self.type = type
        self.plugin_id = plugin_id
        self.instance_id = instance_id
        self.priority = priority
        self.plugin = plugin
