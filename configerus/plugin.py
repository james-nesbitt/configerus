"""

Configerus Plugins.

Typing and Factory decoration for configerus plugins.

"""
import logging
from typing import Dict, Callable
from enum import Enum, unique

logger = logging.getLogger("configerus.plugin")


@unique
class Type(Enum):
    """Enumerator to match plugin types to plugin labels."""

    SOURCE = "configerus.plugin.configsource"
    """ A Config source handler """
    FORMATTER = "configerus.plugin.formatter"
    """ A string formatter plugin """
    VALIDATOR = "configerus.plugin.validator"
    """ A data result validator plugin """


class Factory:
    """Python decorator class for configuerus Plugin factories.

    This class should be used to decorate any function which is meant to be a
    factory for plugins.

    If you are writing a plugin factory, decorate it with this class, provide
    the factory type and id values, and then the factory will be avaialble to
    other code.

    If you are trying to get an instance of a plugin, then create an instance
    of this class and use the create() method
    """

    registry: Dict[str, Dict[str, Callable]] = {}
    """ A static list of all of the registered factory functions """

    # pylint: disable=redefined-builtin
    def __init__(self, type: Type, plugin_id: str):
        """Register the favtory using a decoration."""
        self.plugin_id = plugin_id
        self.type = type

        if self.type.value not in self.registry:
            self.registry[self.type.value] = {}

    def __call__(self, func):
        """Call the factory function decorator.

        Returns:
        --------
        wrapped function(config: Config)
        """

        def wrapper(config, instance_id: str):
            logger.debug(
                "plugin factory exec: %s:%s", self.type.value, self.plugin_id
            )
            return func(config=config, instance_id=instance_id)

        logger.debug(
            "Plugin factory registered `%s:%s`",
            self.type.value,
            self.plugin_id,
        )
        self.registry[self.type.value][self.plugin_id] = wrapper
        return wrapper

    def create(self, config, instance_id: str):
        """Get an instance of a plugin as created by the decorated."""
        try:
            factory = self.registry[self.type.value][self.plugin_id]
        except KeyError as err:
            raise NotImplementedError(
                f"Configerus Plugin instance '{self.type.value}:"
                f"{self.plugin_id}' has not been registered."
            ) from err

        except Exception as err:
            raise Exception(
                "Could not create Plugin instance '{self.type.value}:"
                f"{self.plugin_id}' as the plugin factory raised an exception"
            ) from err

        return factory(config=config, instance_id=instance_id)


CONFIGERUS_FORMATTER_TYPE = Type.FORMATTER
""" Short cut to the config source plugin type enum """


# public methods are in the parent class.
# pylint: disable=too-few-public-methods
class FormatFactory(Factory):
    """Decoration class for registering a config source plugin.

    This decorator is just a shortcut to allow skipping identifying the plugin
    type using the core factory decorator class.

    All we do is extend the core Factory plugin and pass in the plugin type
    for formatters.
    """

    def __init__(self, plugin_id: str):
        """Register the decoration."""
        super().__init__(CONFIGERUS_FORMATTER_TYPE, plugin_id)


CONFIGERUS_SOURCE_TYPE = Type.SOURCE
""" Short cut to the config source plugin type enum """


# public methods are in the parent class.
# pylint: disable=too-few-public-methods
class SourceFactory(Factory):
    """Decoration class for registering a config source plugin.

    This decorator is just a shortcut to allow skipping identifying the plugin
    type using the core factory decorator class.

    All we do is extend the core Factory plugin and pass in the plugin type
    for formatters.
    """

    def __init__(self, plugin_id: str):
        """Register the decoration."""
        super().__init__(CONFIGERUS_SOURCE_TYPE, plugin_id)


CONFIGERUS_VALIDATOR_TYPE = Type.VALIDATOR
""" Short cut to the validate plugin type enum """


# public methods are in the parent class.
# pylint: disable=too-few-public-methods
class ValidatorFactory(Factory):
    """Decoration class for registering a validate plugin.

    This decorator is just a shortcut to allow skipping identifying the plugin
    type using the core factory decorator class.

    All we do is extend the core Factory plugin and pass in the plugin type
    for formatters.
    """

    def __init__(self, plugin_id: str):
        """Register the decoration."""
        super().__init__(CONFIGERUS_VALIDATOR_TYPE, plugin_id)
