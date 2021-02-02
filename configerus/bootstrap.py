import logging
from importlib import metadata

from .config import Config

logger = logging.getLogger('configerus:bootstrap')

CONFIGERUS_BOOTSTRAP_ENTRYPOINT="configerus.bootstrap"
""" SetupTools entrypoint target for bootstrapping """


def bootstrap(bootstrap_id:str, config:Config):
    """
    Make a plugin object instance of a type and key

    A python module out there will need to have declared an entry_point for
    'mirantis.testing.toolbox.{type}' with entry_point key {name}.
    The entrypoint must be a factory method of signature:
    ```
        def XXXX(conf: configerus.config.Config, instance_id:str) -> {plugin}:
    ```

    An alternative would be if the entrypoint refers to a sub-package here. We
    directly

    The factory should return the plugin, which is likely going to be some kind
    of an object which has value to the caller of the function. This function
    does not specify what the return needs to be.
    """
    logger.info("Running bootstrap entrypoint: %s", bootstrap_id)
    eps = metadata.entry_points()[CONFIGERUS_BOOTSTRAP_ENTRYPOINT]
    for ep in eps:
        if ep.name == bootstrap_id:
            plugin = ep.load()
            return plugin(config)
    else:
        logger.error("Plugin loader could not find the requested plugin '%s' of type '%s'.  Valid types are %s", bootstrap_id, CONFIGERUS_BOOTSTRAP_ENTRYPOINT, eps)
        raise KeyError("Plugin not found {}.{}".format(bootstrap_id, CONFIGERUS_BOOTSTRAP_ENTRYPOINT))
