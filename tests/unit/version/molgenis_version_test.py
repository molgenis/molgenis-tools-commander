import unittest

import pytest

from mcmd.core.errors import McmdError
from mcmd.molgenis import version


@pytest.mark.unit
class MolgenisVersionTest(unittest.TestCase):

    @staticmethod
    def test_extract_version_number():
        version = version._extract_version_number('7.0.0')
        assert version == '7.0.0'

    @staticmethod
    def test_extract_version_number_snapshot():
        version = version._extract_version_number('8.0.1-SNAPSHOT')
        assert version == '8.0.1'

    @staticmethod
    def test_extract_version_number_preview():
        version = version._extract_version_number('1.2.3-SNAPSHOT-PR-1234-2')
        assert version == '1.2.3'

    @staticmethod
    def test_extract_version_number_multi():
        version = version._extract_version_number('7.2.3-APP-1.0.0')
        assert version == '7.2.3'

    def test_extract_version_number_invalid(self):
        with self.assertRaises(McmdError):
            version._extract_version_number('4.0-TESTING')
