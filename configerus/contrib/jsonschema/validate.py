from typing import Any
from jsonschema import validate

from configerus.config import Config

PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL = 'jsonschema'


class JsonSchemaValidatorPlugin():
    """   """

    def __init__(self, config: Config, instance_id: str):
        """  """
        self.config = config
        self.instance_id = instance_id

    def validate(self, validate_target: Any, data):
        """ Validate a structure using jsonschema pulled from a config key

        Parameters:
        -----------

        validate_target (str|dict[str:dict]) : validation schema indicatior:

            One of two options will be validated, otherwise we will ignore:

            1. A string of the format "jsonschema:{validation-config-key}"
            2. dict with key "jsonschema"

            For #1, the validation target is expected to be a config target
            (label:key) which will retrieve jsonschema schema from config

            For #2 a dict value for key 'jsonschema' is expected to be the
            schema.

        data (Any) : data which should be validated

        Raises:
        -------

        If a jsonchema schema was identified in the validate target, then a
        jsonschema validation error will be raised if the data is not valid.

        """

        if isinstance(validate_target, str):
            (method, validate_key) = validate_target.split(':')

            if not method == PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL:
                # returns of any value signal validation as validate only catches exceptions
                return

            try:
                schema_config = self.config.load(PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL)
                schema = schema_config.get(validate_key, exception_if_missing=True)

            except Exception as e:
                raise NotImplementedError("Could not access jsonschema validation schema from config target '{}:{}'".format(PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL, validate_key))

        elif isinstance(validate_target, dict):
            if not PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL in validate_target:
                return

            schema = validate_target[PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL]

            if not isinstance(schema, dict):
                raise ValueError("JSONSCHEMA scheme was expected to be a dict: {}".format(schema))

        else:
            # Could not interpret validate target
            return

        validate(data, schema=schema)
