"""

Configerus source plugin that retrieves from a passed Dict.

"""
from typing import Dict, Any

import copy

from configerus.config import Config


class ConfigSourceDictPlugin:
    """Config source plugin that looks for data in a passed Dict."""

    def __init__(self, config: Config, instance_id: str):
        """Initialize the plugin."""
        self.config: Config = config
        self.instance_id: str = instance_id

        self.data: Dict[str, Any] = {}
        """Data that we will use for searching."""

    def copy(self):
        """Make a copy of this plugin."""
        plugin_copy = ConfigSourceDictPlugin(self.config, self.instance_id)
        plugin_copy.set_data(copy.copy(self.data))
        return plugin_copy

    def set_data(self, data: Dict[str, Any]):
        """Assign Dict data to this config source plugin."""
        self.data = data

    def load(self, label: str) -> Dict[str, Any]:
        """Load a config label and return a Dict[str, Any] of config data.

        Parameters:
        -----------
        label (str) : label to load
        """
        return self.data[label] if label in self.data else {}
