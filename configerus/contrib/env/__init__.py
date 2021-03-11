import logging

from configerus.config import Config
from configerus.plugin import SourceFactory

from .env_specific_source import ConfigSourceEnvSpecificPlugin, PLUGIN_ID_SOURCE_ENV_SPECIFIC, CONFIGERUS_ENV_SPECIFIC_BASE_KEY
from .env_json_source import ConfigSourceEnvJsonPlugin, PLUGIN_ID_SOURCE_ENV_JSON, CONFIGERUS_ENV_JSON_ENV_KEY


@SourceFactory(plugin_id=PLUGIN_ID_SOURCE_ENV_SPECIFIC)
def plugin_factory_configsource_env(config: Config, instance_id: str = ''):
    """ create an configsource specific env plugin """
    return ConfigSourceEnvSpecificPlugin(config, instance_id)


@SourceFactory(plugin_id=PLUGIN_ID_SOURCE_ENV_JSON)
def plugin_factory_configsource_env(config: Config, instance_id: str = ''):
    """ create an configsource json env plugin """
    return ConfigSourceEnvJsonPlugin(config, instance_id)


def configerus_bootstrap(config: Config):
    """ Bootstrap a config object

    We don't actually do anything, so this bootstrapper is here only to ensure
    that the above factory decorators are run

    """
    pass


# export the imported constants to make it easier for consumers to import
__all__ = [
    plugin_factory_configsource_env,
    plugin_factory_configsource_env,
    configerus_bootstrap,
    PLUGIN_ID_SOURCE_ENV_SPECIFIC,
    CONFIGERUS_ENV_SPECIFIC_BASE_KEY,
    PLUGIN_ID_SOURCE_ENV_JSON,
    CONFIGERUS_ENV_JSON_ENV_KEY]
