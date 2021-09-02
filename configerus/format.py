"""

Config formatting code.

@NOTE this code has gone through three major iterations, starting with a single
  function, expanded to be module, expanded further with regex, expanded again
  with centralized processing using regex, and finally this parser.  Some
  of the comments may be out of date.

"""
import logging
from typing import Any, Dict, List
from enum import Enum

from .plugin import Type

logger = logging.getLogger("configerus.format")

DEFAULT_FORMATTER_PLUGIN_ID = "get"
"""This plugin is used for formatting when a target doesn't specify plugin."""
FORMATTER_PLUGIN_ID_PASSTHROUGH = "value"
"""This config formatter plugin id just passes the target through."""
FORMATTER_PLUGIN_ID_INTEPRET = "special"
"""This config formatter plugin id to intepret the value."""

FORMATTER_SPECIAL_VALUES: Dict[str, Any] = {
    "Null": None,
    "None": None,
    "{}": {},
    "[]": [],
    "empty": "",
}
""" A map of interpation values for the interpet target """


class ParserState(Enum):
    """What the parser currently thinks it is looking at."""

    OUTSIDE = 0  # we are outside of a matching pattern
    START = 1  # we are inside a matching pattern, either a plugin or a target
    KEY = 2  # we know we are in a target key name
    IGNORE = 3  # we are ignoring the current context


class ParserStackNode:
    """Node in the stack.

    We parse a string using a language stack.
    """

    def __init__(self, parent, state=ParserState.OUTSIDE):
        """Initialize the language stack node.

        Parameters:
        -----------
        parent (node) : a stack needs to know its parent for popping
        state (State) : every node corresponds to a single state
        """
        self.parent = parent
        self.state = state

        self.plugin = None
        self.key = None
        """ some nodes track information collected for interpretation """

        self.parts = []
        """ list of subject parts that are a part of this node """

    def push(self, state):
        """Push a state child and return it."""
        return ParserStackNode(parent=self, state=state)

    def pop(self):
        """Get the node parent."""
        return self.parent

    def __str__(self):
        """Write to a string for debugging."""
        return "{}:{}[{}][p:{},k:{}]".format(
            self.parent, self.state.value, self.join(), self.plugin, self.key
        )

    def join(self):
        """Join the parts back together.

        Returns:
        --------
        If only 1 item is in the node, then it is returned raw, otherwise we
        return a string joing of all of the parts.

        @NOTE this can result in false identities when comparing dicts as
            strings to things like json, as Python uses single quotes, but
            JSON uses double.

        """
        if len(self.parts) == 1:
            return self.parts[0]

        return "".join(["{}".format(part) for part in self.parts])

    def append(self, part):
        """Append a part to the node."""
        self.parts.append(part)


class Formatter:
    """Object which replaces found syntax matches using formatting plugins."""

    START_MATCH = "{{"
    STOP_MATCH = "}}"
    PLUGINEND_MATCH = "::"
    DEFAULT_MATCH = "?"

    def __init__(
        self,
        config,
        default_plugin_for_target: str = DEFAULT_FORMATTER_PLUGIN_ID,
        default_plugin_for_default: str = FORMATTER_PLUGIN_ID_PASSTHROUGH,
        fail_on: List[str] = None,
    ):
        """Initialize the formatter."""
        self.config = config
        self.default_plugin_for_target = default_plugin_for_target
        self.default_plugin_for_default = default_plugin_for_default

        self.fail_on = fail_on if fail_on is not None else []
        """ For debugging, always fail on these values """

        self.special_values: Dict[str, Any] = FORMATTER_SPECIAL_VALUES
        """Special formatter key values."""

    def format(self, data: Any, default_label: str):
        """Perform a deep format."""
        return self.recursive_format(data=data, default_label=default_label)

    def recursive_format(self, data: Any, default_label: str):
        """Perform recursive deep formatting."""
        # try to iterate across the target
        # There is probably a more `python` approach that would cover more
        # iterables, as long as we can re-assign
        if isinstance(data, list):
            for index, value in enumerate(data):
                data[index] = self.recursive_format(
                    data=value, default_label=default_label
                )
        if isinstance(data, dict):
            for index, value in data.items():
                data[index] = self.recursive_format(
                    data=value, default_label=default_label
                )

        # strings get some searching for format actions
        elif isinstance(data, str):
            # if the entire target is the match, then replace whatever type
            # we get out of the config .get() call
            data = self.format_string(
                subject=data, default_label=default_label
            )

        else:
            # all sorts of primitives and custom objects are just ignored.
            pass

        return data

    # Not sure how to reduce branching here. This is the primary stack
    # processing method.
    # pylint: disable=too-many-branches
    def format_string(self, subject: str, default_label: str):
        """Format subject string.

        Looks for and processes any formatting tags in the subject.
        """
        # fast stop test.  if no start tags are in the string then just abort
        if self.START_MATCH not in subject:
            return subject

        subject_tokenized = subject
        for token in [
            self.START_MATCH,
            self.STOP_MATCH,
            self.PLUGINEND_MATCH,
            self.DEFAULT_MATCH,
        ]:
            subject_tokenized = subject_tokenized.replace(
                token, "@@@{}@@@".format(token)
            )
        # subject string split/exploded into words
        subject_parts: List[str] = subject_tokenized.split("@@@")

        stack = ParserStackNode(parent=None, state=ParserState.OUTSIDE)
        # print ("PRE: {} => {}".format(subject, subject_parts))

        for part in subject_parts:

            if part == "":
                # print("SKIP EMPTY -> {}".format(part))
                continue

            if part in [self.START_MATCH]:
                stack = stack.push(ParserState.START)
                stack.plugin = self.default_plugin_for_target
                # print("START: '{}' :: {}".format(part, stack))

            elif part in [self.STOP_MATCH]:

                if stack.state is ParserState.START:
                    # we had started a tag, we had collected only a tag key
                    # and now we see s stop tag, so assume that is all we get
                    key = stack.join()
                    stack = stack.pop()
                    plugin = (
                        stack.plugin
                        if stack.plugin is not None
                        else self.default_plugin_for_target
                    )

                    replace = self.find_replacement(
                        plugin, key, default_label=default_label
                    )
                    stack.append(replace)
                    # print("STOP: (start) '{}' :: {}".format(part, stack))

                elif stack.state is ParserState.KEY:
                    # we had started a tag, and had collected
                    key = stack.join()
                    stack = stack.pop()
                    plugin = (
                        stack.plugin
                        if stack.plugin is not None
                        else self.default_plugin_for_target
                    )

                    replace = self.find_replacement(
                        plugin, key, default_label=default_label
                    )
                    stack.append(replace)
                    # print("STOP: (key) '{}' :: {}".format(part, stack))

                elif stack.state is ParserState.IGNORE:
                    # we are ignoring this stuff
                    stack = stack.pop()
                    # print("STOP: (ignore) '{}' :: {}".format(part, stack))

                else:
                    # print("STOP: (what's this)'{}'::{}".format(part, stack))
                    raise ValueError("Unexpected tag end : {}".format(stack))

            elif stack.state in [ParserState.IGNORE]:
                # If we are in an ignore state, only track tag start and stop
                # so skip everything below
                # print("IGNORING: {}".format(part))
                pass

            elif part in [self.PLUGINEND_MATCH]:
                plugin = stack.join()
                stack = stack.pop()

                stack.plugin = plugin
                stack = stack.push(ParserState.KEY)
                # print("PLUGIN: '{}' :: {}".format(part, stack))

            elif part in [self.DEFAULT_MATCH]:
                key = stack.join()
                stack = stack.pop()

                stack.key = key
                plugin = (
                    stack.plugin
                    if stack.plugin is not None
                    else self.default_plugin_for_target
                )

                try:
                    replace = self.find_replacement(
                        plugin, key, default_label=default_label
                    )
                    stack.append(replace)

                    # if the replacement retrieval did not throw an exception
                    # then ignore the rest of the tag
                    stack = stack.push(ParserState.IGNORE)
                    # print(f"DEFAULT:IGNORING'{part}'::{stack}")
                except KeyError:
                    # if retrieving a replacement raised an exception then we
                    # switch into DEFAULT mode
                    stack.plugin = self.default_plugin_for_default
                    stack = stack.push(ParserState.START)
                    # print(f"DEFAULT: PROCESSING DEFAULT '{part}' :: {stack}")

            else:
                stack.append(part)
                # print("INC: {}".format(part))

        # print("DONE:  {}".format(stack))
        return stack.join()

    def find_replacement(self, plugin: str, key: str, default_label: str):
        """Use a plugin and key to find a replacement."""
        if plugin == FORMATTER_PLUGIN_ID_PASSTHROUGH:
            # In this case we are just passing through.  This is used
            # primarily by the default processor as it has little value from
            # real source.
            return key

        if plugin == FORMATTER_PLUGIN_ID_INTEPRET:
            # In this case interpret the value as something special
            return self.interpret(key)

        if self.config.plugins.has_plugin(
            instance_id=plugin, type=Type.FORMATTER
        ):
            plugin = self.config.plugins.get_plugin(
                instance_id=plugin, type=Type.FORMATTER
            )
        elif self.config.plugins.has_plugin(
            plugin_id=plugin, type=Type.FORMATTER
        ):
            plugin = self.config.plugins.get_plugin(
                plugin_id=plugin, type=Type.FORMATTER
            )
        else:
            logger.error(
                [
                    instance.instance_id
                    for instance in self.config.plugins.instances
                ]
            )
            raise RuntimeError(
                f"Unknown format plugin '{Type.FORMATTER.value}::{plugin}', "
                "no such plugin has been added."
            )

        return plugin.format(key=key, default_label=default_label)

    def interpret(self, key: str):
        """Interpret that value to mean something special."""
        try:
            return self.special_values[key.strip()]
        except Exception as err:
            raise ValueError(
                "Could not interpret special key '{}'".format(key)
            ) from err
