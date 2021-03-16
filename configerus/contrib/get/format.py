import re
import logging

from configerus.config import Config

logger = logging.getLogger('configerus.contrib.get:formatter')

CONFIG_DEFAULT_MATCH_PATTERN = r'((?P<label>\w+)\:)?(?P<key>[-\w.]+)'
""" Default regex pattern used detect format targets for config retrieval """


class ConfigFormatGetPlugin():
    """ return a format replacement by retriving data from config """

    def __init__(self, config: Config, instance_id: str):
        """  """
        self.config = config
        self.instance_id = instance_id

        self.pattern = re.compile(CONFIG_DEFAULT_MATCH_PATTERN)

    def format(self, key, default_label: str):
        """ Format a key by returning config values

        Parameters:
        -----------

        key: a string that should gies instructions to the formatter on how to
            create a format replacements

        default_label : if format/replace patterns don't have a label defined
            then this is used as a label.

        Raises:
        -------

        KeyError if the source or the key could not be found.

        """

        match = self.pattern.fullmatch(key.strip())
        if not match:
            raise KeyError("Could not interpret Format action key '{}'".format(key))

        """ from an re.match get data from config """
        label = match.group('label')
        key = match.group('key')

        if label is None:
            label = default_label

        if label is None:
            label = default_label

        loaded = self.config.load(label)
        return loaded.get(key, exception_if_missing=True)
