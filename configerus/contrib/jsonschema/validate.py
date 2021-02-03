from jsonschema import validate

from configerus.config import Config

PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL = 'jsonschema'

class JsonSchemaValidatorPlugin():
    """   """

    def __init__(self, config:Config, instance_id:str):
        """  """
        self.config = config
        self.instance_id = config

    def validate(self, validate_target:str, data):
        """ Validate a structure using jsonschema pulled from a config key """

        (method, validate_key) = validate_target.split(':')

        if not method == PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL:
            # returns of any value signal validation as validate only catches exceptions
            return

        try:
            schema_config = self.config.load(PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL)
            schema = schema_config.get(validate_key, exception_if_missing=True)

        except Exception as e:
            raise NotImplemented("Could not access jsonschema validation schema from config target '{}:{}'".format(PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL, validate_key))

        validate(data, schema=schema)
