import unittest
from unittest.mock import patch

import pytest

from mcmd.core.compatibility import version, deprecated
from mcmd.core.errors import McmdError


@version('2.0.0')
def get_impl():
    return '2.0.0'


@version('3.0.0')
def get_impl():
    return '3.0.0'


@version('2.2.2')
def get_impl():
    return '2.2.2'


@deprecated(since='2.0.0',
            action='doing something')
def do_something():
    return 'doing something'


@pytest.mark.unit
class CompatibilityTest(unittest.TestCase):

    @patch('mcmd.molgenis.version.get_version_number')
    def test_version_exact(self, version_number):
        version_number.return_value = '2.2.2'
        assert get_impl() == '2.2.2'

    @patch('mcmd.molgenis.version.get_version_number')
    def test_version_between(self, version_number):
        version_number.return_value = '2.5.0'
        assert get_impl() == '2.2.2'

    @patch('mcmd.molgenis.version.get_version_number')
    def test_version_lower(self, version_number):
        version_number.return_value = '1.0.0'
        assert get_impl() == '2.0.0'

    @patch('mcmd.molgenis.version.get_version_number')
    def test_version_higher(self, version_number):
        version_number.return_value = '4.0.0'
        assert get_impl() == '3.0.0'

    def test_version_duplicate(self):
        with self.assertRaises(ValueError):
            # noinspection PyShadowingNames
            @version('2.0.0')
            def get_impl():
                return 'not allowed'

    @patch('mcmd.molgenis.version.get_version')
    @patch('mcmd.molgenis.version.get_version_number')
    def test_deprecated_lower(self, version_number, get_version):
        version_number.return_value = '1.0.0'
        get_version.return_value = '1.0.0'
        assert do_something() == 'doing something'

    @patch('mcmd.molgenis.version.get_version')
    @patch('mcmd.molgenis.version.get_version_number')
    def test_deprecated_equal(self, version_number, get_version):
        version_number.return_value = '2.0.0'
        get_version.return_value = '2.0.0'
        with self.assertRaises(McmdError):
            do_something()

    @patch('mcmd.molgenis.version.get_version')
    @patch('mcmd.molgenis.version.get_version_number')
    def test_deprecated_higher(self, version_number, get_version):
        version_number.return_value = '2.0.1'
        get_version.return_value = '2.0.1-SNAPSHOT'
        with self.assertRaises(McmdError):
            do_something()
