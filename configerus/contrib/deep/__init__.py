
from configerus.config import Config
from configerus.plugin import FormatFactory

from .format import ConfigFormatDeepPlugin

PLUGIN_ID_FORMAT_DEEP = 'deep'
PLUGIN_PRIORITY_FORMAT_DEEP = 90

""" Format plugin_id for the configerus deep format plugin """
@FormatFactory(plugin_id=PLUGIN_ID_FORMAT_DEEP)
def plugin_factory_format_deep(config: Config, instance_id: str = ''):
    """ create an format plugin which recursiveley formats data """
    return ConfigFormatDeepPlugin(config, instance_id)


def configerus_bootstrap(config: Config):
    """ Bootstrap a config object by adding our formatter """
    config.add_formatter(PLUGIN_ID_FORMAT_DEEP, priority=PLUGIN_PRIORITY_FORMAT_DEEP)
