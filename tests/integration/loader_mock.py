from pathlib import Path

from ruamel.yaml import YAML

import mcmd.config.config as config

_TEST_CONFIG = """
git:
  root:
  paths:
  - molgenis-platform-integration-tests/src/test/resources/xls
  - molgenis-platform-integration-tests/src/test/resources/csv
  - molgenis-platform-integration-tests/src/test/resources/obo
resources:
  dataset_folders: 
  - {dataset_folder}
host:
  selected: {url}
  auth:
  - url: {url}
    username: {username}
    password: {password}
settings:
  import_action: add_update_existing
api:
  rest1: api/v1/
  rest2: api/v2/
  login: api/v1/login/
  group: api/plugin/security/group/
  member: api/plugin/security/group/{{}}/member
  import: plugin/importwizard/importFile/
  import_url: plugin/importwizard/importByUrl
  perm: menu/admin/permissionmanager/update/
  rls: menu/admin/permissionmanager/update/entityclass/rls
"""


def load_config():
    yaml = YAML()
    test_config = yaml.load(_TEST_CONFIG)
    config._config = test_config


def get_dataset_folder():
    return Path(__file__).parent.joinpath('resources').absolute()


def mock_config(url, username, password):
    global _TEST_CONFIG
    _TEST_CONFIG = _TEST_CONFIG.format(url=url,
                                       username=username,
                                       password=password,
                                       dataset_folder=str(get_dataset_folder()))
