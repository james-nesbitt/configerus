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

from configerus.config import Config

logger = logging.getLogger('configerus.contrib.env.source.json')

PLUGIN_ID_SOURCE_ENV_JSON = 'env-json'
""" ConfigSource plugin_id for the configerus json env configsource plugin """

CONFIGERUS_ENV_JSON_ENV_KEY = 'env'
""" Config key for retreiving the env json env value from config """


class ConfigSourceEnvJsonPlugin():
    """ Get config from  a single ENV variables """

    def __init__(self, config: Config, instance_id: str):
        """  """
        self.config = config
        self.instance_id = instance_id

        self.source = {}
        """ default to empty source """

    def set_env(self, env: str):
        logger.debug("Setting new ENV source: {}".format(env))
        env_json = os.getenv(env)

        # Allow the env variable to be empty
        if env_json is None or env_json == '':
            self.source = {}
        else:
            try:
                self.source = json.loads(env_json)
            except json.decoder.JSONDecodeError as e:
                raise ValueError("Invalid json in {} ENV variable: {}".format(env, e)) from e

    def load(self, label: str):
        """ Load a config label and return a Dict[str, Any] of config data

        Parameters:

        label (str) : label to load

        """
        if label in self.source:
            return self.source[label]

        return {}
