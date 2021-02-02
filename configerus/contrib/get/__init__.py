
from configerus.config import Config
from configerus.plugin import FormatFactory

from .format import ConfigFormatGetPlugin

PLUGIN_ID_FORMAT_GET = 'get'
""" Format plugin_id for the configerus get format plugin """
PLUGIN_PRIORITY_FORMAT_GET_PRIORITY = 80
""" bootstrapping get formatter plugin priority """

@FormatFactory(plugin_id=PLUGIN_ID_FORMAT_GET)
def plugin_factory_format_get(config: Config, instance_id: str = ''):
    """ create an format plugin which replaces from config.get """
    return ConfigFormatGetPlugin(config, instance_id)

def configerus_bootstrap(config: Config):
    """ Bootstrap a config object by adding our formatter """
    config.add_formatter(PLUGIN_ID_FORMAT_GET, priority=PLUGIN_PRIORITY_FORMAT_GET_PRIORITY)
