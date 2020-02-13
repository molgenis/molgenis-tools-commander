from pathlib import Path

from ruamel.yaml import YAML

from mcmd.config import config

_TEST_CONFIG = """
git:
  root: 
  paths: []
resources:
  dataset_folders: 
  - {dataset_folder}
  resource_folders:
  - {resource_folder}
host:
  selected: {url}
  auth:
  - url: {url}
    username: {username}
    password: {password}
settings:
  import_action: add_update_existing
"""

_url: str = None
_username: str = None
_password: str = None


def load_config():
    yaml = YAML()
    test_config = yaml.load(_TEST_CONFIG)
    config._config = test_config


def get_dataset_folder():
    return get_files_folder().joinpath('datasets')


def get_resource_folder():
    return get_files_folder().joinpath('resources')


def get_files_folder():
    return Path(__file__).parent.joinpath('files').absolute()


def get_host():
    return {
        'url': _url,
        'username': _username,
        'password': _password
    }


def mock_config(url, username, password):
    global _url, _username, _password
    _url = url
    _username = username
    _password = password

    global _TEST_CONFIG
    _TEST_CONFIG = _TEST_CONFIG.format(url=url,
                                       username=username,
                                       password=password,
                                       dataset_folder=get_dataset_folder(),
                                       resource_folder=get_resource_folder())
