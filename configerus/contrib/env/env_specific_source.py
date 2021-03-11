"""

Config source from JSON contents of an ENV variable

This plugin allows you to include JSON in a single ENV variable which if present
will be used as a config source.

This allows large runtime config overrides with out a lot of individual ENV
variables being needed.

If you find that your JSON is tiny and difficult to design/manage, then confider
usng the 'specific' env source plugin.

string case for keys is a weird topic.  We .lower() all keys as it seems a
decent convention.

"""
from typing import Dict, Any
import logging
import os

from configerus.config import Config

logger = logging.getLogger('configerus.contrib.env.source.specific')

PLUGIN_ID_SOURCE_ENV_SPECIFIC = 'env-specific'
""" ConfigSource plugin_id for the configerus env configsource plugin """

CONFIGERUS_ENV_SPECIFIC_BASE_KEY = 'base'
""" Config key for retreiving the env specific base value from config """


class ConfigSourceEnvSpecificPlugin():
    """ Get config from all ENV variables """

    def __init__(self, config: Config, instance_id: str):
        """  """
        self.config = config
        self.instance_id = instance_id

        self.base = ''
        """ keep the ENV base prefix that should limit what gets pulled in """

    def set_base(self, base: str):
        self.base = base

    def load(self, label: str):
        """ Load a config label and return a Dict[str, Any] of config data

        Parameters:

        label (str) : label to load

        """

        if self.base:
            label_prefix = '{}_{}_'.format(self.base, label).upper()
        else:
            label_prefix = '{}_'.format(label).upper()

        filtered = {}
        for env_key, env_value in os.environ.items():
            if env_key.upper().startswith(label_prefix):
                filtered[env_key[len(label_prefix):].lower()] = env_value

        organized = {}
        for (key, value) in filtered.items():
            if key.startswith('_'):
                continue

            base = organized
            key_steps = key.lower().split('_')

            last_step = key_steps.pop()

            for key_step in key_steps:
                if not isinstance(base, dict):
                    base = {}
                if not key_step in base:
                    base[key_step] = {}
                base = base[key_step]
            if not isinstance(base, dict):
                base = {}
            base[last_step] = value

        return organized
