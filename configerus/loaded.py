import logging
from typing import Any
from .shared import tree_get, tree_reduce

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
        assert data is not None, "None data was passed in"

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

    def has(self, key: Any = LOADED_KEY_ROOT):
        """ check if a key value exists in the config

        using a key, traverse a tree of data and return a boolean for if the key
        can be found.

        Parameters:

        key (Varies) : specify the key path down the loaded config data dict.

            This is a very forgiving and adaptive parameter.  You have can pass:

            '1.2.3.4' : "dot" notation which means the steps down the tree are
                1, 2, 3 then 4.

            ['1', '2', '3', '4'] : asks for the same '1.2.3.4' path as above.

            if the loaded data was:
            ```
                {
                    '1': {
                        '2': {
                            '3': {
                                '4': 'my value'
                            }
                        }
                    }
                }
            ```
            Then the returned value would be 'my value'

            You can also mix and match with out worrying about clean formatting:

            ['1.2', '3.4']
            ['1.2.3.4', '', '.']
            ['1', ['2', '3.4']]
            ['1', '2', '3.', '.4']

            (all are equivalent to '1.2.3.4')

            This allows you to pass around keys and append to them on the fly
            without having to be overly concerned about clean formatting.

        Returns:
        --------

        Boolean : if a value exists in loaded config

        """
        try:
            tree_get(self.data, key, ignore=['', LOADED_KEY_ROOT])
            return True
        except KeyError as e:
            return False

    def get(self, key: Any = LOADED_KEY_ROOT, format: bool = True, validator: str = "", default: Any = None):
        """ get a key value from the loaded config

        using a key, traverse a tree of data and return the value, optionally
        formatted, optionally validated.

        Parameters:

        key (Varies) : specify the key path down the loaded config data dict.

            This is a very forgiving and adaptive parameter.  You have can pass:

            '1.2.3.4' : "dot" notation which means the steps down the tree are
                1, 2, 3 then 4.

            ['1', '2', '3', '4'] : asks for the same '1.2.3.4' path as above.

            if the loaded data was:
            ```
                {
                    '1': {
                        '2': {
                            '3': {
                                '4': 'my value'
                            }
                        }
                    }
                }
            ```
            Then the returned value would be 'my value'

            You can also mix and match with out worrying about clean formatting:

            ['1.2', '3.4']
            ['1.2.3.4', '', '.']
            ['1', ['2', '3.4']]
            ['1', '2', '3.', '.4']

            (all are equivalent to '1.2.3.4')

            this allows you to pass around keys and append to them on the fly
            without having to be overly concerned about clean formatting.

        format (bool): should retrieved string values be checked for variable
           substitution?  If so then the str value is checked using regex for
           things that should be replaced with other config values.
           @see self.format_string().)

           Formatting IS NOT APPLIED if the key could not be matched.

        validator (str) : string key passed to the validate() method which will
            validate the retrieved data before returning it.

            Validation IS APPLIED if the key could not be matched.

        default (Any) : default which will be returned if no matching key is
            found.  This means that no Exception will be thrown on KeyError

        Returns:

        (Any) anything in the Dict is a valid return.  The return could be a
            Dict with child elements, an array or any other primitive.
            If the return is a string then it is formatted for variable
            substitution (see self.format_string().)

        Throws:

        Can throw a KeyError if the key cannot be found (which also occurs if
        all sources produced no data and a non-empty key was passed,) ONLY IF
        no default value was provided.

        """
        value = ""

        try:
            value = tree_get(self.data, key, ignore=['', LOADED_KEY_ROOT])

        except KeyError as e:
            if default is None:
                # hand off the exception
                raise e
            else:
                # Use the default value
                logger.debug("Failed to find config key : %s", key)
                value = default

        if format and value is not None:
            # try to format any values
            value = self.format(value)

        if validator:
            self.parent.validate(value, validator)

        return value

    def format(self, data):
        """ Format some data using the config object formatters

        Parameters:

        data (Any): primitive data that should be formatted. The data will be
            passed to the formatter plugins in descending priority order.

        """
        return self.parent.format(data, self.instance_id)

    def validate(self, data, validate_target: Any, exception_if_invalid: bool = True):
        """ Validate some data using the config object validators

        data (Any): primitive data that should be validated. The data will be
            passed to the validator plugins in descending priority order.

        validate_target (Any) : Validation target which will be interpreted by the
            validation plugins.  Two typical formats are common:

            1. a string with some identifiable pattern that a plugi can recognize
            2. a dict with keys that different plugins can recognize.

            if empty/None then no validation is performed.

        Returns:
        --------

        Bool results of validation. If any validation plugin raises an exception
        then it will be false.

        If exception_if_invalid then validation failures with raise and exception

        Raises:
        -------

        ValidationError on any validation exception.

        ValdiationError if any validator ran into an exception internally.

        @TODO can we be more specific in interpreting validation exceptions.

        """
        return self.parent.validate(data=data, validate_target=validate_target,
                                    exception_if_invalid=exception_if_invalid)
