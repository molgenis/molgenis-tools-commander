import random
import string
from urllib.parse import urljoin

import molgenis.client
import pytest

from mcmd.__main__ import start
from tests.integration.loader_mock import set_login


def pytest_configure(config):
    """Sets the host config values before any tests are run."""

    url = config.getoption('url')
    username = config.getoption('username')
    password = config.getoption('password')

    set_login(url, username, password)


@pytest.fixture
def session(request):
    url = request.config.getoption('url')
    username = request.config.getoption('username')
    password = request.config.getoption('password')

    session = molgenis.client.Session(urljoin(url, '/api/'))
    session.login(username, password)
    return session


def run_commander(arg_string):
    """Runs the commander and asserts that the exit code was 1."""
    exit_code = start(['mcmd'] + arg_string.split(' '))
    assert exit_code == 1


def random_name():
    return ''.join(random.choices(string.ascii_uppercase, k=6))
