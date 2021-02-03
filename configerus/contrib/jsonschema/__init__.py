
from configerus.config import Config
from configerus.plugin import ValidatorFactory

from .validate import JsonSchemaValidatorPlugin

PLUGIN_ID_VALIDATE_JSONSCHEMA = 'jsonschema'
""" Format plugin_id for the configerus jsonschema validator plugin """
PLUGIN_PRIORITY_VALIDATE_JSONSCHEMA_PRIORITY = 60
""" bootstrapping jsonschema validate plugin priority """

@ValidatorFactory(plugin_id=PLUGIN_ID_VALIDATE_JSONSCHEMA)
def plugin_factory_validator_schema(config: Config, instance_id: str = ''):
    """ create a validate plugin which applies json schema validation """
    return JsonSchemaValidatorPlugin(config, instance_id)

def configerus_bootstrap(config: Config):
    """ Bootstrap a config object by adding our formatter """
    config.add_validator(PLUGIN_ID_VALIDATE_JSONSCHEMA, priority=PLUGIN_PRIORITY_VALIDATE_JSONSCHEMA_PRIORITY)
