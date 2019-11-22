from urllib.parse import urljoin

import molgenis.client
import pytest

from tests.integration.loader_mock import mock_config
from tests.integration.utils import setup_entity, run_commander, random_name


def pytest_configure(config):
    """Sets the host config values before any tests are run."""

    url = config.getoption('url')
    username = config.getoption('username')
    password = config.getoption('password')

    mock_config(url, username, password)


@pytest.fixture(scope='session')
def session(request):
    url = request.config.getoption('url')
    username = request.config.getoption('username')
    password = request.config.getoption('password')

    session = molgenis.client.Session(urljoin(url, '/api/'))
    session.login(username, password)
    return session


@pytest.fixture
def entity_type():
    return setup_entity()


@pytest.fixture
def user():
    name = random_name()
    run_commander('add user {}'.format(name))
    return name


@pytest.fixture
def group():
    name = random_name()
    run_commander('add group {}'.format(name))
    return name


@pytest.fixture
def package():
    name = random_name()
    run_commander('add package {}'.format(name))
    return name
