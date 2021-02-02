import os
import re
import json
import yaml

from configerus.config import Config
from configerus.shared import tree_merge

# FileTypes that this class can use at this time
FILESOURCE_FILETYPES = [ "json", "yaml", "yml" ]
""" Valid config types that the config loader can currently handled """

CONFIGERUS_PATH_LABEL = 'paths'
""" If you load this label, it is meant to be return a keyed path """

class ConfigSourcePathPlugin:
    """   """

    def __init__(self, config:Config, instance_id:str):
        """  """
        self.config = config
        self.instance_id = config

        self.path = ''

    def set_path(self, path: str):
        """ Set the config path source """
        self.path = path

    def load(self, label: str):
        """ load config for a name

        Parameters:
        -----------

        lable (str) : config label to load, should correlated to a json or yaml
            file of the same name in the path, otherwise an empty Dict is
            returned.

            **There is 1 special case, where if MTT_CONFIG_PATH_LABEL is passed
              then the function returns a Dict of 'instance_id:path' which can
              be used for string substitution**

        Returns:
        --------

        Dict[str, Any] of data that was loaded for the label
        """

        if not os.path.isdir(self.path):
            raise ValueError("Could not load '{}' path config, as the source path does not exist: {}".format(self.instance_id, self.path))

        # Special case for retreiving paths instead of config
        if label == CONFIGERUS_PATH_LABEL:
            return {self.instance_id: self.path}

        data = {}
        """ hold all merged data from found source files """

        file_types_re = "|".join(FILESOURCE_FILETYPES)
        """ regex part for allowed file extensions """
        config_files_re = rf"({label})\.({file_types_re})"
        """ regex that matches all valid config filenames for the label """

        for file in [f for f in os.listdir(self.path) if re.match(config_files_re, f)]:
            with open(os.path.join(self.path, file)) as matching_file:
                extension = os.path.splitext(file)[1].lower()
                if extension == ".json":
                    try:
                        file_config = json.load(matching_file)
                    except json.decoder.JSONDecodeError as e:
                        raise ValueError("Failed to parse one of the config files '{}': {}".format(os.path.join(self.path, file), e))

                    assert file_config, "Empty config in {} from file {}".format(path, file)
                    data = tree_merge(file_config, data)
                elif extension == ".yml" or extension == ".yaml":
                    try:
                        file_config = yaml.load(matching_file, Loader=yaml.FullLoader)
                    except yaml.YAMLError as e:
                        raise ValueError("Failed to parse one of the config files '{}': {}".format(os.path.join(self.path, file), e))

                    assert file_config, "Empty config in {} [{}]".format(file, self.path)
                    data = tree_merge(file_config, data)

                else:
                    raise ValueError("Unknown config filetype. Cannot parse '{}' files, but it matches our regex".format(extension))

        return data
