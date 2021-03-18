
import os.path
import re
import yaml
import json
import logging

from configerus.config import Config

FILES_FORMAT_MATCH_PATTERN = r'(?P<file>(\~?\/?\w+\/)*\w*(\.\w+)?)'
""" A regex pattern to identify files that should be embedded """

logger = logging.getLogger('configerus.contrib.files:format')


class ConfigFormatFilePlugin:
    """ Format a key by returning the contents of a file """

    def __init__(self, config: Config, instance_id: str):
        """  """
        self.config = config
        self.instance_id = instance_id

        self.pattern = re.compile(FILES_FORMAT_MATCH_PATTERN)

    def format(self, key, default_label: str):
        """ Format a string by substituting config values

        Parameters
        ----------

        key: a string that should gies instructions to the formatter on how to
            create a format replacements

        default_label : if format/replace patterns don't have a source defined
            then this is used as a source.

        Raises
        ------

        FileNotFound is a file replacement is requested but the file path
            cannot be opened

        json.decoder.JSONDecodeError if a json file cannot be unmarshalled

        yaml.YAMLError if a yaml file cannot be unmarshalled

        Returns
        -------

        unmarshalled json/yml file or string contents of the file

        """

        match = self.pattern.fullmatch(key.strip())
        if not match:
            raise KeyError("Could not interpret Format action target '{}'".format(key))

        file = match.group('file')
        """ path to the file to return as a replacement """

        extension = ''
        """ file extension, used to make decisions about parsing/unmarshalling """
        file_split = os.path.splitext(file)
        if len(file_split) > 0:
            extension = file_split[1].lower()

        try:
            with open(file) as fo:
                if extension == ".json":
                    try:
                        return json.load(fo)
                    except json.decoder.JSONDecodeError as e:
                        raise ValueError(
                            "Failed to parse one of the config files '{}': {}".format(
                                os.path.join(
                                    self.path, file), e))

                elif extension == ".yml" or extension == ".yaml":
                    try:
                        return yaml.load(fo, Loader=yaml.FullLoader)
                    except yaml.YAMLError as e:
                        raise ValueError(
                            "Failed to parse one of the config files '{}': {}".format(
                                os.path.join(
                                    self.path, file), e))

                # return file contents as a string (above parsing didn't happen)
                return fo.read()

        except FileNotFoundError as e:
            raise KeyError("Could not embed file as config as file could not be found: {}".format(file))
