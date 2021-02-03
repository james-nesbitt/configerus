import logging

from .shared import tree_get

logger = logging.getLogger('configerus:loaded')

class Loaded:
    """ A loaded config which contains all of the file config for a single label

    This is an easy to useconfig object for a single load. From this you can get
    config using dot notation.

    Think of this as relating to a single filename, merged from different paths
    as opposed to the Config object which loads config and hands off to this one.

    """

    def __init__(self, data, parent, instance_id:str):
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
        """ Allow new data to be passed in

        this is meant to be used by the core only, and is used to update config
        when new config paths are added, typically by boostrapping.

        Hopeully this is done before the config is really used
        """
        self.data = data

    def get(self, key: str, format: bool=True, exception_if_missing: bool=False, validator:str=""):
        """ get a key value from the active label

        Here you can use "." (dot) notation to indicated a path down the config
        tree.
        so "one.two.three" should match the descending path:

        one
        --two
            --three

        Parameters:

        key (str): the dot notation key that should match a value in Dict

        format (bool): should retrieved string values be checked for variable
           substitution?  If so then the str value is checked using regex for
           things that should be replaced with other config values.
           @see self.format_string()

        validator (str) : string key passed to the validate() method which will
            validate the retrieved data before returning it.

        Returns:

        (Any) anything in the Dict is a valid return.  The return could be a
            Dict with child elements, an array or any other primitive.
            If the return is a string then it is formatted for variable
            substitution (see self.format_string())

        Throws:

        Can throw a KeyError if the key cannot be found (which also occurs if
        all sources produced no data)
        """
        value = ""

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
