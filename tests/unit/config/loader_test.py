import unittest

import pytest
from ruamel.yaml import YAML

# noinspection PyProtectedMember
from mcmd.config.loader import _merge

DEFAULTS = """
git:
  paths:
    - path/1
    - path/2
    - path/new
new-property: 1
old-property: a
host:
    auth:
        - url: localhost
          username: admin
"""

USER_CONFIG = """
git:
  paths:
    - path/1
    - path/2
    - path/custom
old-property: overwrite
host:
    auth:
        - url: localhost
          username: henk
        - url: master.dev.molgenis.org
          username: admin
"""

MERGED_CONFIG = """
git:
  paths:
    - path/1
    - path/2
    - path/new
    - path/custom
new-property: 1
old-property: overwrite
host:
    auth:
        - url: localhost
          username: henk
        - url: master.dev.molgenis.org
          username: admin
"""


@pytest.mark.unit
class ConfigLoaderTest(unittest.TestCase):
    def test_merge_list(self):
        yaml = YAML()
        defaults = yaml.load(DEFAULTS)
        user_config = yaml.load(USER_CONFIG)

        _merge(defaults, user_config)

        expected = yaml.load(MERGED_CONFIG)
        self.assertEqual(expected, defaults)
