from urllib.parse import urljoin

import molgenis.client
import pytest

from tests.integration.loader_mock import mock_config
from tests.integration.utils import setup_entity, run_commander, random_name


def pytest_configure(config):
    """Sets the host config values before any tests are run."""

    options = dict()
    if 'integration' in config.getoption('-m'):
        options['url'] = config.getoption('url')
        options['username'] = config.getoption('username')
        options['password'] = config.getoption('password')

    if 'local' in config.getoption('-m'):
        options['pg_user'] = config.getoption('pg_user')
        options['pg_password'] = config.getoption('pg_password')
        options['db_name'] = config.getoption('db_name')
        options['molgenis_home'] = config.getoption('molgenis_home')
        options['minio_data'] = config.getoption('minio_data')

    mock_config(options)



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
