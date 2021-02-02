import re

from configerus.config import Config

CONFIG_DEFAULT_MATCH_PATTERN = r'\{((?P<source>\w+):)?(?P<key>[\w.]+)(\?(?P<default>[^\}]+))?\}'
""" Default regex pattern used to string template, which needs to identify
keys that can be used for replacement. Needs to have a named group for
key, and can have named group for source and default

The above regex pattern resolves for three named groups: source, key and default:

the {first?check} value          : key=first, default=check
a {common.dot.notation} test     : key=commond.dot.notation
a {label:dot.notation.test} here : source=label, key=dot.notation.test

so:
1. all replacements are wrapped in "{}"
2. an optional "source:" group tells config to look in a specifig label
3. a "?default" group allows a default (untemplated) value to be used if the
   key cannot be found
"""

class ConfigFormatGetPlugin():
    """   """

    def __init__(self, config:Config, instance_id:str):
        """  """
        self.config = config
        self.instance_id = config

        self.pattern = re.compile(CONFIG_DEFAULT_MATCH_PATTERN)

    def format(self, target, default_source:str):
        """ Format a string by substituting config values

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
            return self._get(match, default_source)

        # search through the target replacing any found matches with
        start = 0
        match = self.pattern.search(target, start)
        while match:
            rep = str(self._get(match, default_source))
            target = target[:match.start()] + rep + target[match.end()]
            start = start + len(rep)
            match = self.pattern.search(target, start)

        return target

    def _get(self, match, default_source:str):
        """ from an re.match get data from config """
        key = match.group('key')
        source = match.group('source')
        default = match.group('default')

        if source is None:
            source = default_source
        source_config = self.config.load(source)

        try:
            return source_config.get(key, exception_if_missing=True)
        except KeyError as e:
            if match.group('default'):
                return match.group('default')
            else:
                # if a template string wasn't found then exception
                raise e
