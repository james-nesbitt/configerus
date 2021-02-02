import logging

from configerus.config import Config
from configerus.plugin import SourceFactory

from .source import ConfigSourceDictPlugin

PLUGIN_ID_CONFIGSOURCE_DICT = 'dict'
""" ConfigSource plugin_id for the configerus dict configsource plugin """
@SourceFactory(plugin_id=PLUGIN_ID_CONFIGSOURCE_DICT)
def plugin_factory_configsource_dict(config: Config, instance_id: str = ''):
    """ create an configsource dict plugin """
    return ConfigSourceDictPlugin(config, instance_id)


def configerus_bootstrap(config: Config):
    """ Bootstrap a config object

    We don't actually do anything, so this bootstrapper is here only to ensure
    that the above factory decorator is run

    """
    pass
