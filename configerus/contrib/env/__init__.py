import logging

from configerus.config import Config
from configerus.plugin import SourceFactory

from .source import ConfigSourceEnvPlugin

PLUGIN_ID_SOURCE_ENV = 'env'
""" ConfigSource plugin_id for the configerus env configsource plugin """
CONFIGERUS_ENV_BASE_KEY = 'base'
""" Config key for retrieving an env plugin base value from config """


@SourceFactory(plugin_id=PLUGIN_ID_SOURCE_ENV)
def plugin_factory_configsource_env(config: Config, instance_id: str = ''):
    """ create an configsource env plugin """
    return ConfigSourceEnvPlugin(config, instance_id)


def configerus_bootstrap(config: Config):
    """ Bootstrap a config object

    We don't actually do anything, so this bootstrapper is here only to ensure
    that the above factory decorator is run

    """
    pass
