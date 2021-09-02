"""

Configerus validation plugin that uses jsonschema to validate.

"""
from typing import Any
from jsonschema import validate

from configerus.config import Config

PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL = "jsonschema"


class JsonSchemaValidatorPlugin:
    """Configerus validation plugin that uses jsonschema to validate."""

    def __init__(self, config: Config, instance_id: str):
        """Initialize plugin."""
        self.config = config
        self.instance_id = instance_id

    def copy(self):
        """Make a copy of this plugin."""
        plugin_copy = JsonSchemaValidatorPlugin(self.config, self.instance_id)
        return plugin_copy

    def validate(self, validate_target: Any, data):
        """Validate a structure using jsonschema pulled from a config key.

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
            (method, validate_key) = validate_target.split(":")

            if not method == PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL:
                # returns of any value signal validation as validate only
                # catches exceptions
                return

            # This case means that we were told to look for a jsonschema source
            # in config, which we can find by loading jsonschema as a config
            # label and then treating the passed string as a config key for
            # .get()

            try:
                schema_config = self.config.load(
                    PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL
                )
                schema = schema_config.get(validate_key)

            except Exception as err:
                raise NotImplementedError(
                    "Could not access jsonschema validation schema from config"
                    f" target "
                    f"'{PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL}:"
                    f"{validate_key}'"
                ) from err

        elif isinstance(validate_target, dict):
            # in this case, the validate target is itself a Dict JsonSchema
            # validation definition.

            if (
                PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL
                not in validate_target
            ):
                return

            schema = validate_target[
                PLUGIN_ID_VALIDATE_JSONSCHEMA_SCHEMA_CONFIG_LABEL
            ]

            if not isinstance(schema, dict):
                raise ValueError(
                    f"JSONSCHEMA scheme was expected to be a dict: {schema}"
                )

        else:
            # Could not interpret validate target
            return

        # Call the jsonschema validation using the schema.
        # this will raise an exception on validatio failure
        # pylint: disable=not-callable
        validate(data, schema=schema)
