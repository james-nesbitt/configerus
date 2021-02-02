import logging
from tempfile import mkdtemp
from shutil import rmtree
from typing import List
import os.path
import json
import yaml

from configerus.config import Config
from configerus.contrib.dict import PLUGIN_ID_CONFIGSOURCE_DICT
from configerus.contrib.files import PLUGIN_ID_CONFIGSOURCE_PATH

logger = logging.getLogger('configerus:tests')

TEST_CONFIG_TEMP_DIR = ''
""" on first use, we will populate this with a str path to a parent tmp dir that
    will contain any file config that we use """

def make_test_config(config:Config, sources: List):
    """ Make config of various types from a list, and add it to a config object """
    global TEST_CONFIG_TEMP_DIR

    logger.info("Building sources from source list")
    for source in sources:
        name = source["name"]
        priority = source["priority"] if "priority" in source else config.default_priority()
        type = source["type"]
        data = source["data"]

        if type == PLUGIN_ID_CONFIGSOURCE_DICT:
            logger.info("Adding 'dict' source '%s' [%s]: %s", name, priority, data.keys())
            config.add_source(type, name, priority).set_data(data)

        elif type == PLUGIN_ID_CONFIGSOURCE_PATH:
            # on first use, get a temp dir
            if not TEST_CONFIG_TEMP_DIR:
                TEST_CONFIG_TEMP_DIR = mkdtemp()

            # first make files for all of the data
            path = name
            full_path = os.path.join(TEST_CONFIG_TEMP_DIR, path)
            os.makedirs(full_path)
            for file_name, file_data in data.items():
                full_file = os.path.join(full_path, file_name)
                logger.debug("path source '%s' writing file '%s' : %s", name, full_file, file_data)
                with open(full_file, 'w') as config_file_pointer:
                    extension = os.path.splitext(file_name)[1].lower()[1:]
                    if extension == "json":
                        json.dump(file_data, config_file_pointer)
                    elif extension == "yaml" or extension == "yml":
                        yaml.dump(file_data, config_file_pointer)

            # then add the created paths to the config sources
            logger.info("Adding 'path' source '%s' [%s]: %s : %s", name, priority, path, data.keys())
            config.add_source(type, name, priority).set_path(full_path)

def test_config_cleanup(config:Config):
    """ clean up any created temporary folder created """
    if TEST_CONFIG_TEMP_DIR:
        rmtree(TEST_CONFIG_TEMP_DIR)
