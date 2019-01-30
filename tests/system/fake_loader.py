import pkg_resources
from ruamel.yaml import YAML

import mcmd.config.loader
from mcmd.config.config import set_config

_TEST_CONFIG = pkg_resources.resource_stream('tests.system', 'test.yaml')


def load_test_config():
    yaml = YAML()
    test_config = yaml.load(_TEST_CONFIG)
    set_config(test_config)


mcmd.config.loader.load_config = load_test_config
