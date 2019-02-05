import molgenis.client
import pytest

# noinspection PyUnresolvedReferences
import tests.integration.fake_home
# noinspection PyUnresolvedReferences
import tests.integration.fake_loader
from mcmd.__main__ import start


@pytest.fixture
def session():
    session = molgenis.client.Session('http://localhost:8080/api/')
    session.login('admin', 'admin')
    return session


def run_commander(arg_string):
    return start(['mcmd'] + arg_string.split(' '))
