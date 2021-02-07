from .config import Config
import logging
from typing import List

logger = logging.getLogger('configerus')


CONFIGERUS_BOOSTRAP_DEFAULT = [
    'deep',
    'get',
    'files'
]
""" Default list of modules to bootstrap for a new config object """


def new_config(bootstraps: List[str] = CONFIGERUS_BOOSTRAP_DEFAULT):
    """ Get a new Config object

    bootstraps (List[str]) : list of modules to bootstrap for this config object
        For each string, config will try to run a setuptools entrypoint bootstrap
        function, passing in the config object.

        This can be used for 2 purposes:
        1. the bootstrap function may be in a file which registers plugins that
            can be used in the config object
        2. the bootstrap can modify the config object as needed.

    """
    # start with a new config object
    config = Config()

    for bootstrap_entrypoint_id in bootstraps:
        logger.debug('bootstrapping: {}'.format(bootstrap_entrypoint_id))
        config.bootstrap(bootstrap_entrypoint_id)

    return config
