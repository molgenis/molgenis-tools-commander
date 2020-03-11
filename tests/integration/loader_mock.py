from pathlib import Path
from typing import Optional

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
local:
  database:
    pg_user: {pg_user}
    pg_password: {pg_password}
    name: {db_name}
  molgenis_home: {molgenis_home}
  minio_data: {minio_data}
"""

_url: Optional[str] = None
_username: Optional[str] = None
_password: Optional[str] = None


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


def mock_config(options):
    global _url, _username, _password
    _url = options.get('url')
    _username = options.get('username')
    _password = options.get('password')

    global _TEST_CONFIG
    _TEST_CONFIG = _TEST_CONFIG.format(url=options.get('url'),
                                       username=options.get('username'),
                                       password=options.get('password'),
                                       dataset_folder=get_dataset_folder(),
                                       resource_folder=get_resource_folder(),
                                       pg_user=options.get('pg_user'),
                                       pg_password=options.get('pg_password'),
                                       db_name=options.get('db_name'),
                                       molgenis_home=options.get('molgenis_home'),
                                       minio_data=options.get('minio_data'))
