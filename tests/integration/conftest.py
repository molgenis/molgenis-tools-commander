import random
import string
import sys

import molgenis.client
import pytest

from tests.integration import fake_loader, fake_home

sys.modules['mcmd.config.loader'] = fake_loader
sys.modules['mcmd.config.home'] = fake_home

# IMPORTANT: importing __main__ must come last!
from mcmd.__main__ import start


@pytest.fixture
def session():
    # TODO get from config
    session = molgenis.client.Session('http://localhost:8080/api/')
    session.login('admin', 'admin')
    return session


def run_commander(arg_string):
    return start(['mcmd'] + arg_string.split(' '))


def random_name():
    return ''.join(random.choices(string.ascii_uppercase, k=6))
