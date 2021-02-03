import logging
from typing import List

logger = logging.getLogger('configerus')

from .config import Config
from .bootstrap import bootstrap

CONFIGERUS_BOOSTRAP_DEFAULT = [
    'deep',
    'get'
]
""" Default list of modules to bootstrap for a new config object """

def new_config(bootstraps:List[str]=CONFIGERUS_BOOSTRAP_DEFAULT):
    """ Get a new Config object

    bootstraps (List[str]) : list of modules to bootstrap for this config object
        For each string, config will try to run a setuptools entrypoint bootstrap
        function, passing in the config object.

        This can be used for 2 purposes:
        1. the bootstrap function may be in a file which registers plugins that
            can be used in the config object
        2. the bootstrap can modify the config object as needed.

    """
    config = Config()

    for bootstrap_entrypoint_id in bootstraps:
        logger.debug('bootstrapping: {}'.format(bootstrap_entrypoint_id))
        bootstrap(bootstrap_entrypoint_id, config)

    return config
