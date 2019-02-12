import random
import string
from urllib.parse import urljoin

import molgenis.client
import pytest

from mcmd.__main__ import start
from tests.integration.loader_mock import mock_config


def pytest_configure(config):
    """Sets the host config values before any tests are run."""

    url = config.getoption('url')
    username = config.getoption('username')
    password = config.getoption('password')

    mock_config(url, username, password)


@pytest.fixture
def session(request):
    url = request.config.getoption('url')
    username = request.config.getoption('username')
    password = request.config.getoption('password')

    session = molgenis.client.Session(urljoin(url, '/api/'))
    session.login(username, password)
    return session


def run_commander(arg_string):
    """Runs the commander and asserts that the exit code was 0."""
    exit_code = start(['mcmd'] + arg_string.split(' '))
    assert exit_code == 0


def run_commander_fail(arg_string):
    """Runs the commander without failing the test if the command fails"""
    with pytest.raises(SystemExit):
        start(['mcmd'] + arg_string.split(' '))


def random_name():
    return ''.join(random.choices(string.ascii_uppercase, k=6))


def setup_entity():
    """Imports an entity with a different identifier each time."""
    package_name = random_name()
    run_commander('add package {}'.format(package_name))
    run_commander('import testAutoId_unpackaged --in {}'.format(package_name))
    return '{}_testAutoId'.format(package_name)
