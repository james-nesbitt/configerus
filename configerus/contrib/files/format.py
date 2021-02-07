
import os.path
import re
import yaml
import json
import logging

from configerus.config import Config

FILES_FORMAT_MATCH_PATTERN = r'(\[(file\:)(?P<file>(\~?\/?\w+\/)*\w*(\.\w+)?)\])'
""" A regex pattern to identify files that should be embedded """

logger = logging.getLogger('configerus.contrib.files:format')


class ConfigFormatFilePlugin:
    """   """

    def __init__(self, config: Config, instance_id: str):
        """  """
        self.config = config
        self.instance_id = instance_id

        self.pattern = re.compile(FILES_FORMAT_MATCH_PATTERN)

    def format(self, target, default_source: str):
        """ Format a string by substituting config values

        Parameters
        ----------

        target: a string that should be formatted. If not a string then no
            formatting is performed

        default_source : if format/replace patterns don't have a source defined
            then this is used as a source.

        """
        if not isinstance(target, str):
            return target

        # if the entire target is the match, then replace whatever type we get
        # out of the config .get() call
        match = self.pattern.fullmatch(target)
        if match:
            return self._get(match, return_only_string=False)

        # search through the target replacing any found matches with
        start = 0
        match = self.pattern.search(target, start)
        while match:
            rep = str(self._get(match))
            target = target[:match.start()] + rep + target[match.end()]
            start = start + len(rep)
            match = self.pattern.search(target, start)

        return target

    def _get(self, match, return_only_string: bool = True):
        """ find a file match and return the file contents

        Parameters
        ----------

        match (re Match) a regex match which we use to determine file path

        return_only_string (bool) optional indictor that the function is
            expecting only a string return.  Knowing this means that we can
            skip unmarshalling file contents which could be expensive.

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
        file = match.group('file')
        extension = os.path.splitext(file)[1].lower()

        try:
            with open(file) as file_o:
                if not return_only_string:
                    # try to parse/unmarshall a file instead of just returing it

                    if extension == ".json":
                        try:
                            data = json.load(file_o)
                        except json.decoder.JSONDecodeError as e:
                            raise ValueError(
                                "Failed to parse one of the config files '{}': {}".format(
                                    os.path.join(
                                        self.path, file), e))
                        return data

                    elif extension == ".yml" or extension == ".yaml":
                        try:
                            data = yaml.load(file_o, Loader=yaml.FullLoader)
                        except yaml.YAMLError as e:
                            raise ValueError(
                                "Failed to parse one of the config files '{}': {}".format(
                                    os.path.join(
                                        self.path, file), e))
                        return data

                # return file contents as a string (above parsing didn't happen)
                return file_o.read()

        except FileNotFoundError as e:
            raise KeyError("Could not embed file as config as file could not be found: {}".format(file))
