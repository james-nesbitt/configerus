import logging

from .loaded import Loaded
from .plugin import FormatFactory, SourceFactory, Type
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
        self.sources = {PLUGIN_DEFAULT_PRIORITY: []}
        """ Keep the collection of config sources in a Dict where the keys are
            priority and the values are a list of plugins at that priority.
        """
        self.formatters = {PLUGIN_DEFAULT_PRIORITY: []}
        """ Keep the collection of config formatters in a Dict where the keys are
            priority and the values are a list of plugins at that priority.
        """

        # save all loaded config when it is first loaded to save load costs on repeat calls
        self.loaded = {}
        """ Loaded map for config that has been loaded """

    def copy(self):
        """ return a copy of this Config object """
        logger.debug("Config is copying")
        copy = Config()
        # we copy the dict of plugins, not to get copies of the plugins, just to
        # get copies of the dicts so that modifying the copy does not affect the
        # original.
        copy.sources = self._copy_plugin_prioritymap(self.sources)
        copy.formatters = self._copy_plugin_prioritymap(self.formatters)
        # note that we don't copy the loaded config list, which means that any
        # load() runs on the copy will reload from sources.
        return copy

    def _copy_plugin_prioritymap(self, plugin_map):
        """ safely copy a priority map of plugins without copying the plugins """
        copy =  {}
        for key in plugin_map:
            copy[key] = []
            for plugin in plugin_map[key]:
                copy[key].append(plugin)
        return copy

    def paths_label(self):
        """ retrieve the special config label which is a list of paths """
        return CONFIG_PATH_LABEL

    def default_priority(self):
        """ Return the default priority for relative priority setting """
        return PLUGIN_DEFAULT_PRIORITY

    def has_source(self, instance_id:str):
        """ Check if a source instance has already been added

        You can use this in abstracts to detect if you've already added a plugin

        """
        for priority in self.sources.keys():
            if instance_id in self.sources[priority]:
                return True
        return False;

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
        if not plugin_id:
            raise KeyError("Could not create a config source as an invalid plugin_id was given: '{}'".format(plugin_id))

        try:
            source_fac = SourceFactory(plugin_id)
            source = source_fac.create(self, instance_id)

        except NotImplementedError as e:
            raise NotImplementedError("Could not create config source '{}' as that plugin_id could not be found.".format(plugin_id)) from e
        # except Exception as e:
        #     raise Exception("Could not create config source '{}' as the plugin factory produced an exception".format(plugin_id)) from e


        if not priority in self.sources:
            self.sources[priority] = []
        self.sources[priority].append(source)
        return source

    def load(self, label:str, force_reload:bool=False):
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

        Returns:
        --------

        A Loaded object from which you can .get() specific pieces of config

        Throws:
        -------

        Some source plugins will throw Exceptions if they have internal problems

        """
        if force_reload or label not in self.loaded:
            data = self._get_config_data(label)
            self.loaded[label] = Loaded(data=data, parent=self, instance_id=label)

        return self.loaded[label]

    def _get_ordered_sources(self):
        """ retrieve a flat List of config sources ordered high to low by priority """
        ordered = []
        """ Keep the uber list of sorted sources """
        for priority in sorted(self.sources.keys()):
            ordered += self.sources[priority]
        ordered.reverse()
        return ordered

    def has_formatter(self, instance_id:str):
        """ Check if a formatter instance has already been added

        You can use this in abstracts to detect if you've already added a plugin
        """
        for priority in self.sources.keys():
            if instance_id in self.sources[priority]:
                return True
        return False;

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
        if not plugin_id:
            raise KeyError("Could not create a formatter source as an invalid plugin_id was given: '{}'".format(plugin_id))

        try:
            format_fac = FormatFactory(plugin_id)
            formatter = format_fac.create(self, instance_id)

        except NotImplementedError as e:
            raise NotImplementedError("Could not create config formatter '{}' as that plugin_id could not be found.".format(plugin_id)) from e
        # except Exception as e:
        #     raise Exception("Could not create config formatter '{}' as the plugin factory produced an exception".format(plugin_id)) from e


        if not priority in self.formatters:
            self.formatters[priority] = []
        self.formatters[priority].append(formatter)
        return formatter

    def format(self, data, default_label:str):
        """ Format some data using the config object formatters

        data (Any): primitive data that should be formatted. The data will be
            passed to the formatter plugins in descending priority order.

        """
        for formatter in self._get_ordered_formatters():
            data = formatter.format(data, default_label)
        return data

    def _get_ordered_formatters(self):
        """ retrieve a flat List of config sources ordered high to low by priority """
        ordered = []
        """ Keep the uber list of sorted sources """
        for priority in sorted(self.formatters.keys()):
            ordered += self.formatters[priority]
        ordered.reverse()
        return ordered

    def reload_configs(self):
        """ Get new data for all loaded configs

        In case it isn't clear, this is expensive, but might be needed if you
        know that config has changed in the background.

        """
        self.loaded = {}

    def _get_config_data(self, label: str):
        """ load data from all of the sources for a label """
        logger.debug("Loading Config '%s' from all sources", label)

        data = {}
        # merge in data from the higher priorty into the lower priority
        for source in self._get_ordered_sources():
            source_data = source.load(label)
            data = tree_merge(data, source_data)

        if not data:
            raise KeyError("Config '{}' loaded data came out empty.  That means that no config source could find that label.  That is likely a problem".format(label))

        return data

    def _get_ordered_sources(self):
        """ retrieve a flat List of config sources ordered high to low by priority """
        ordered = []
        """ Keep the uber list of sorted sources """
        for priority in sorted(self.sources.keys()):
            ordered += self.sources[priority]
        ordered.reverse()
        return ordered
