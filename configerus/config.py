import logging

from .plugin import Factory, Type, PluginInstances
from .shared import tree_merge
from .loaded import Loaded

logger = logging.getLogger('configerus:config')

CONFIG_PATH_LABEL = 'paths'
""" If you load this label, it is meant to be return a keyed path """

PLUGIN_DEFAULT_PRIORITY = 75
""" Default plugin priority, which should be a common unprioritized value

General approach:

<35 Low priority defaults (system)
<50 Higher priority defaults (contrib)
<75 Low prority setting (project)
 75 default
<90 High priority settings (project, contrib)
>90 !important (project)

"""

class Config:
    """ Config management class (v3)

    Allows some sourced file based project configuration with some pattern
    templating and path set overriding.

    To allow easy separation of config into manageable files, all config is
    grouped into "label" strings which correlate to config files with matching
    names.
    Before accessing a config label, it has to be loaded, which you can do with
    the load() method.
    Then all get() calls use the most recently loaded config label.

    Templating: some string substitution can be done based on config values
        and some path keys. Templating options are based on a custom syntax

    Overriding: tell config about multiple paths in order of priority, and it
        will allow higher priority values to override lower priority values

    Dot notation retrival: you can treat your data as a tree, and config will
        allow you to retrieve tree nodes using a syntax where "." is a node
        label delimiter.

    """

    def __init__(self):
        self.plugins = PluginInstances(self)
        """ keep a list of all of the plugins as PluginInstance wrappers

            This mixes plugin types together but but it simplifies management
            and storage of plugins """

        self.loaded = {}
        """ cache of config that has been loaded """

    def copy(self):
        """ make a copy of this config object so that we can independently edit
            the copy without affecting the original.
        """
        copy = Config()
        copy.plugins = self.plugins.copy(copy)
        return copy

    """ Pass through accessors

    These methods just give access to some values used to govern config without
    having to import the module and directly access constants.

    """

    def paths_label(self):
        """ retrieve the special config label which is a list of paths """
        return CONFIG_PATH_LABEL

    def default_priority(self):
        """ Return the default priority for relative priority setting """
        return PLUGIN_DEFAULT_PRIORITY

    """ Source plugins

    All methods related to managing and using source plugins.

    Some methods are short wrappers on the plugin abstractions, but that allows
    consumers to not have to import the .plugin.Type enums

    """

    def has_source(self, instance_id:str):
        """ Check if a source instance has already been added """
        return self.plugns.has_plugin(instance_id, Type.CONFIGSOURCE)

    def add_source(self, plugin_id:str, instance_id:str='', priority:int=PLUGIN_DEFAULT_PRIORITY):
        """ add a new config source to the config object and return it

        Parameters:
        -----------

        plugin_id (str) : id of the plugin as registered using the plugin factory
            decorater for a source plugin.  This has to match a plugin's registration
            with the plugin factory as a part of the Factory decoration

        instance_id (str) : Optionally give a source plugin instance a name, which
            it might use for internal functionality.
            The "path" source plugin allows string template substitution of the
            "__paths__:instance_id" for the path.

        priority (int) : source priority. Use this to set this source values as
            higher or lower priority than others.

        Returns:
        --------

        Returns the source plugin so that you can do any actions to the plugin that it
        supports, and the code here doesn't need to get fancy with function arguments

        """
        return self.plugins.add_plugin(Type.CONFIGSOURCE, plugin_id, instance_id, priority)

    def load(self, label:str, force_reload:bool=False, validator:str=""):
        """ Load a config label

        This queries all sources for the label and merges the loaded config data
        into a single Loaded object.
        The loads are cached per Config instance to make repeated calls cheap.

        Parameters:
        -----------

        label (str) : Config label to load.  Every config source can provide
            config data sets for labels, which correspond to things like
            "all files with a matching filename", or all "records in a matching
            db table"

        force_reload (bool) : if true, and data has been loaded before, this
            forces a fresh reload of data from the sources

        validator (str) : string key passed to the validate() method which will
            validate the retrieved data before returning it.

        Returns:
        --------

        A Loaded object from which you can .get() specific pieces of config

        Throws:
        -------

        Some source plugins will throw Exceptions if they have internal problems

        If you request a validation, and validation fails, then a Validation
        error with be raised.

        """
        if force_reload or label not in self.loaded:
            """ load data from all of the sources for a label """
            logger.debug("Loading Config '%s' from all sources", label)

            data = {}
            # merge in data from the higher priorty into the lower priority
            for source in self.plugins.get_ordered_plugins(Type.CONFIGSOURCE):
                source_data = source.load(label)
                if source_data:
                    data = tree_merge(data, source_data)

            if not data:
                raise KeyError("Config '{}' loaded data came out empty.  That means that no config source could find that label.  That is likely a problem".format(label))

            self.loaded[label] = Loaded(data=data, parent=self, instance_id=label)

        if validator:
            self.validate(self.loaded[label].data, validator)

        return self.loaded[label]

    """ Formatter plugin usage and management



    """

    def has_formatter(self, instance_id:str):
        """ Check if a formatter instance has already been added

        You can use this in abstracts to detect if you've already added a plugin
        """
        return self.plugns.has_plugin(instance_id, Type.FORMATTER)

    def add_formatter(self, plugin_id:str, instance_id:str='', priority:int=PLUGIN_DEFAULT_PRIORITY):
        """ add a new config formatter to the config object and return it

        Parameters:
        -----------

        plugin_id (str) : id of the plugin as registered using the plugin
            factory  decorater for a formatter plugin.  This has to match a
            plugin's registration  with the plugin factory as a part of the
            Factory decoration

        instance_id (str) : Optionally give a formatters plugin instance a name,
            which it might use for internal functionality.

        priority (int) : source priority. Use this to set this source values as
            higher or lower priority than others.

        Returns:
        --------

        Returns the source plugin so that you can do any actions to the plugin that it
        supports, and the code here doesn't need to get fancy with function arguments

        """
        return self.plugins.add_plugin(Type.FORMATTER, plugin_id, instance_id, priority)

    def format(self, data, default_label:str):
        """ Format some data using the config object formatters

        data (Any): primitive data that should be formatted. The data will be
            passed to the formatter plugins in descending priority order.

        """
        for formatter in self.plugins.get_ordered_plugins(Type.FORMATTER):
            data = formatter.format(data, default_label)
        return data


    """ Validator plugin usage and management



    """

    def has_validator(self, instance_id:str):
        """ Check if a formatter instance has already been added

        You can use this in abstracts to detect if you've already added a plugin
        """
        return self.plugns.has_plugin(instance_id, Type.VALIDATOR)

    def add_validator(self, plugin_id:str, instance_id:str='', priority:int=PLUGIN_DEFAULT_PRIORITY):
        """ add a new config validator to the config object and return it

        Parameters:
        -----------

        plugin_id (str) : id of the plugin as registered using the plugin
            factory  decorater for a validator plugin.  This has to match a
            plugin's registration  with the plugin factory as a part of the
            Factory decoration

        instance_id (str) : Optionally give a validator plugin instance a name,
            which it might use for internal functionality.

        priority (int) : source priority. Use this to set this source values as
            higher or lower priority than others.

        Returns:
        --------

        Returns the source plugin so that you can do any actions to the plugin that it
        supports, and the code here doesn't need to get fancy with function arguments

        """
        return self.plugins.add_plugin(Type.VALIDATOR, plugin_id, instance_id, priority)

    def validate(self, data, validate_target:str, exception_if_invalid:bool=True):
        """ Format some data using the config object formatters

        data (Any): primitive data that should be formatted. The data will be
            passed to the formatter plugins in descending priority order.

        validate_target : A config key which can be used

        """

        try:
            for validator in self.plugins.get_ordered_plugins(Type.VALIDATOR):
                validator.validate(validate_target, data)
        except Exception as e:
            if exception_if_invalid:
                raise e
