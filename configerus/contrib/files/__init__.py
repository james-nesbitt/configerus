"""

Configerus contrib package for config from files.

"""
from configerus.config import Config
from configerus.plugin import FormatFactory, SourceFactory

from .source import ConfigSourcePathPlugin
from .format import ConfigFormatFilePlugin


CONFIGERUS_PATH_KEY = "path"
"""Default key that for the path."""

PLUGIN_ID_SOURCE_PATH = "path"
"""ConfigSource plugin_id for the configerus path configsource plugin."""


@SourceFactory(plugin_id=PLUGIN_ID_SOURCE_PATH)
def plugin_factory_configsource_path(config: Config, instance_id: str = ""):
    """Create an configsource path plugin."""
    return ConfigSourcePathPlugin(config, instance_id)


PLUGIN_ID_FORMAT_FILE = "file"
"""Format plugin_id for the configerus filepath format plugin."""


@FormatFactory(plugin_id=PLUGIN_ID_FORMAT_FILE)
def plugin_factory_format_file(config: Config, instance_id: str = ""):
    """Create an format plugin which replaces from file contents."""
    return ConfigFormatFilePlugin(config, instance_id)


def configerus_bootstrap(config: Config):
    """Bootstrap a config object."""
    config.add_formatter(
        plugin_id=PLUGIN_ID_FORMAT_FILE,
        instance_id=PLUGIN_ID_FORMAT_FILE,
        priority=40,
    )
