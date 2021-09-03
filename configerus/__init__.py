"""

Configerus base package.

Contains typical config constructor for starting to use configerus.

"""
import logging
from typing import List

from .config import Config

logger = logging.getLogger("configerus")


CONFIGERUS_BOOSTRAP_DEFAULT = ["get", "files"]
""" Default list of modules to bootstrap for a new config object """


def new_config(bootstraps: List[str] = None):
    """Get a new Config object.

    bootstraps (List[str]) : list of modules to bootstrap for this config
        object For each string, config will try to run a setuptools entrypoint
        bootstrap function, passing in the config object.

        This can be used for 2 purposes:
        1. the bootstrap function may be in a file which registers plugins that
            can be used in the config object
        2. the bootstrap can modify the config object as needed.

    """
    # start with a new config object
    config = Config()

    if bootstraps is None:
        bootstraps = CONFIGERUS_BOOSTRAP_DEFAULT

    for bootstrap_entrypoint_id in bootstraps:
        logger.debug("bootstrapping: %s", bootstrap_entrypoint_id)
        config.bootstrap(bootstrap_entrypoint_id)

    return config
