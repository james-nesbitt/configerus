from typing import Dict, Any
from configerus.config import Config

class ConfigSourceDictPlugin():
    """   """

    def __init__(self, config:Config, instance_id:str):
        """  """
        self.config = config
        self.instance_id = config

        self.data = {}
        """ keep the data that we will use for searching """

    def set_data(self, data: Dict[str,Any]):
        """ Assign Dict data to this config source plugin """
        self.data = data

    def load(self, label: str):
        """ Load a config label and return a Dict[str, Any] of config data

        Parameters:

        label (str) : label to load

        """
        if label in self.data:
            return self.data[label]
        else:
            return {}
