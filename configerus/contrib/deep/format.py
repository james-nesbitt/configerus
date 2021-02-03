from typing import List, Dict, Any

from configerus.config import Config

class ConfigFormatDeepPlugin():
    """   """

    def __init__(self, config:Config, instance_id:str):
        """  """
        self.config = config
        self.instance_id = config

    def format(self, target, default_source:str):
        """ Deep formatter for formatting that reruns formatting across iterables

        this formatter just reruns formatting on elements of primitive iterables.

        """
        # try to iterate across the target
        # There is probably a more `python` approach that would cover more
        # iterables, as long as we can re-assign
        if isinstance(target, Dict):
            return self.format_dict(target, default_source)
        elif isinstance(target, List):
            return self.format_list(target, default_source)

        # anything we can't iterate through we just return
        return target

    def format_list(self, target: List[Any], default_source:str):
        """ Search a List for strings to format @see format_string """
        for index, value in enumerate(target):
            target[index] = self.config.format(value, default_source)
        return target

    def format_dict(self, target: Dict[str, Any], default_source:str):
        """ Search a Dict for strings to format @see format_string """
        for key, value in target.items():
            target[key] = self.config.format(value, default_source)
        return target
