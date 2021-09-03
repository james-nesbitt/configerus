"""

Get config overrides for specific config values from different ENV variables

With this plugin, all ENV variables are interpreted as different config values
dependening on their name, and the values are added as a config source.

This allows small single ENV variable overrides for specific values at runtime.

If you find that you are using a large number of ENV variables for your
overrides, consider using the JSON plugin instead.

"""
from typing import Dict, Any
import logging
import os
import json

import copy

from configerus.config import Config

logger = logging.getLogger("configerus.contrib.env.source.json")

PLUGIN_ID_SOURCE_ENV_JSON = "env-json"
""" ConfigSource plugin_id for the configerus json env configsource plugin """

CONFIGERUS_ENV_JSON_ENV_KEY = "env"
""" Config key for retreiving the env json env value from config """


class ConfigSourceEnvJsonPlugin:
    """Get config from  a single ENV variables."""

    def __init__(self, config: Config, instance_id: str):
        """Initialize the plugin."""
        self.config: Config = config
        self.instance_id: str = instance_id

        self.source: Dict[str, Any] = {}
        """ default to empty source """

    def copy(self):
        """Make a copy of this plugin."""
        plugin_copy = ConfigSourceEnvJsonPlugin(self.config, self.instance_id)
        plugin_copy.source = copy.copy(self.source)
        return plugin_copy

    def set_env(self, env: str):
        """Assign json data from an env variable."""
        logger.debug("Setting new ENV source: %s", env)
        env_json = os.getenv(env)

        # Allow the env variable to be empty
        if env_json is None or env_json == "":
            self.source = {}
        else:
            try:
                self.source = json.loads(env_json)
            except json.decoder.JSONDecodeError as err:
                raise ValueError("Invalid json in {} ENV variable.") from err

    def load(self, label: str) -> Dict[str, Any]:
        """Load a config label and return a Dict[str, Any] of config data.

        Parameters:
        -----------
        label (str) : label to load
        """
        return self.source[label] if label in self.source else {}
