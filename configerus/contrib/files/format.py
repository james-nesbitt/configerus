"""

Configerus format plugins which can replace markers with file contents.

Replacing can be with flat file contents or with parsed json or yml.

"""
import os.path
import re
import json
import logging

import yaml

from configerus.config import Config

FILES_FORMAT_MATCH_PATTERN = r"(?P<file>(\~?\/?\w+\/)*\w*(\.\w+)?)"
""" A regex pattern to identify files that should be embedded """

logger = logging.getLogger("configerus.contrib.files:format")


class ConfigFormatFilePlugin:
    """Format a key by returning the contents of a file."""

    def __init__(self, config: Config, instance_id: str):
        """Initialize the plugin."""
        self.config = config
        self.instance_id = instance_id

        self.pattern = re.compile(FILES_FORMAT_MATCH_PATTERN)

    def copy(self):
        """Make a copy of this plugin."""
        plugin_copy = ConfigFormatFilePlugin(self.config, self.instance_id)
        return plugin_copy

    # pylint: disable=unused-argument
    def format(self, key, default_label: str):
        """Format a string by substituting config values.

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
            raise KeyError(
                "Could not interpret Format action target '{}'".format(key)
            )

        # path to the file to return as a replacement
        file = match.group("file")
        # file extension, used to make decisions about parsing/unmarshallin
        extension = ""
        file_split = os.path.splitext(file)
        if len(file_split) > 0:
            extension = file_split[1].lower()

        try:
            with open(file) as file_object:
                if extension == ".json":
                    try:
                        return json.load(file_object)
                    except json.decoder.JSONDecodeError as err:
                        raise ValueError(
                            f"Failed to parse one of the config files '{file}'"
                        ) from err

                elif extension in [".yml", ".yaml"]:
                    try:
                        return yaml.safe_load(file_object)
                    except yaml.YAMLError as err:
                        raise ValueError(
                            f"Failed to parse one of the config files '{file}'"
                        ) from err

                # return file contents as a string (above parsing didn't happen)
                return file_object.read()

        except FileNotFoundError as err:
            raise KeyError(
                f"Could not embed file as config as file could not be found: {file}"
            ) from err
