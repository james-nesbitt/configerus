import logging
from typing import Any
from .shared import tree_get

logger = logging.getLogger('configerus:loaded')

LOADED_KEY_ROOT = ''
""" If this key is requested in .get() then the root data dict is returned """


class Loaded:
    """ A loaded config which contains all of the file config for a single label

    This is an easy to useconfig object for a single load. From this you can get
    config using dot notation.

    Think of this as relating to a single filename, merged from different paths
    as opposed to the Config object which loads config and hands off to this one.

    """

    def __init__(self, data, parent, instance_id: str):
        """
        parameters
        ----------

        data (Dict[str, Any]): deep dict struct that contains all of the merged
           configuration that is te be used for config retrieval. It is often
           a nested Dict with standard primitives as can be loaded from json/yml

        parent (Config): The parent Config object which created this object
           which is used for backreferencing, primarily when trying to perform
           template string substitution as substitution can refer to config from
           other sources.

        """
        self.data = data
        self.parent = parent
        self.instance_id = instance_id

    def _reload(self, data):
        """ Force new data to be used

        This is meant to be used by the parent only, and is used to update config
        when new config paths are added, typically by boostrapping.

        Hopeully this is done before the config is really used.

        @TODO signal on this?

        """
        self.data = data

    def get(self, key: Any = LOADED_KEY_ROOT, format: bool = True,
            exception_if_missing: bool = False, validator: str = ""):
        """ get a key value from the active label

        Here you can use "." (dot) notation to indicated a path down the config
        tree.
        so "one.two.three" should match the descending path:

        one
        --two
            --three

        Parameters:

        key (Varies) : specify the key path down the loaded config data .dict to
            retrieve.
            If empty (LOADED_KEY_ROOT) then the entire .data dict is returned
            If List[str] then then list is concatenated into a single dot
            notation string, ignoring any empty (LOADED_KEY_ROOT) values to
            create a single "dot notation" paths string.

            The string is then exploded on "." where each value must correlate
            to a descending dict key, until we reach a value.

        format (bool): should retrieved string values be checked for variable
           substitution?  If so then the str value is checked using regex for
           things that should be replaced with other config values.
           @see self.format_string().)

        validator (str) : string key passed to the validate() method which will
            validate the retrieved data before returning it.

        Returns:

        (Any) anything in the Dict is a valid return.  The return could be a
            Dict with child elements, an array or any other primitive.
            If the return is a string then it is formatted for variable
            substitution (see self.format_string().)

        Throws:

        Can throw a KeyError if the key cannot be found (which also occurs if
        all sources produced no data and a non-empty key was passed.)

        """
        value = ""

        if key is None or key == '' or key == LOADED_KEY_ROOT:
            value = self.data

        else:
            # check if key is an iterable of strings
            try:
                if isinstance(key, list):
                    keys = '.'.join([key_part for key_part in key if not (
                        key_part == '' or key_part == LOADED_KEY_ROOT)])
                    key = keys
            except TypeError as e:
                raise e

            if key == '' or key == LOADED_KEY_ROOT:
                value = self.data
            else:
                try:
                    value = tree_get(self.data, key)
                except KeyError as e:
                    if exception_if_missing:
                        # hand off the exception
                        raise e
                    else:
                        logger.debug("Failed to find config key : %s", key)
                        return None

        # try to format any string values
        value = self.format(value)

        if validator:
            self.parent.validate(value, validator)

        return value

    def format(self, data):
        """ Format some data using the config object formatters

        data (Any): primitive data that should be formatted. The data will be
            passed to the formatter plugins in descending priority order.


        """
        return self.parent.format(data, self.instance_id)
