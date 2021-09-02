"""

Configerus contrib package for config from environment variables.

"""
import logging

from configerus.config import Config
from configerus.plugin import SourceFactory

from .env_specific_source import (
    ConfigSourceEnvSpecificPlugin,
    PLUGIN_ID_SOURCE_ENV_SPECIFIC,
    CONFIGERUS_ENV_SPECIFIC_BASE_KEY,
)
from .env_json_source import (
    ConfigSourceEnvJsonPlugin,
    PLUGIN_ID_SOURCE_ENV_JSON,
    CONFIGERUS_ENV_JSON_ENV_KEY,
)


@SourceFactory(plugin_id=PLUGIN_ID_SOURCE_ENV_SPECIFIC)
def plugin_factory_configsource_env_specific(
    config: Config, instance_id: str = ""
):
    """Create an configsource specific env plugin."""
    return ConfigSourceEnvSpecificPlugin(config, instance_id)


@SourceFactory(plugin_id=PLUGIN_ID_SOURCE_ENV_JSON)
def plugin_factory_configsource_env_json(
    config: Config, instance_id: str = ""
):
    """Create an configsource json env plugin."""
    return ConfigSourceEnvJsonPlugin(config, instance_id)


# Unused config arg is a part of the bootstrap interface.
# pylint: disable=unused-argument
def configerus_bootstrap(config: Config):
    """Bootstrap a config object.

    We don't actually do anything, so this bootstrapper is here only to ensure
    that the above factory decorators are run

    """
