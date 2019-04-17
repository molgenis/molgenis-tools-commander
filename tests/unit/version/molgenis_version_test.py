import unittest

import pytest

from mcmd.version import molgenis_version


@pytest.mark.unit
class MolgenisVersionTest(unittest.TestCase):

    @staticmethod
    def test_extract_version_number():
        version = molgenis_version._extract_version_number('7.0.0')
        assert version == '7.0.0'

    @staticmethod
    def test_extract_version_number_snapshot():
        version = molgenis_version._extract_version_number('8.0.1-SNAPSHOT')
        assert version == '8.0.1'

    @staticmethod
    def test_extract_version_number_preview():
        version = molgenis_version._extract_version_number('1.2.3-SNAPSHOT-PR-1234-2')
        assert version == '1.2.3'

    @staticmethod
    def test_extract_version_number_multi():
        version = molgenis_version._extract_version_number('7.2.3-APP-1.0.0')
        assert version == '7.2.3'
