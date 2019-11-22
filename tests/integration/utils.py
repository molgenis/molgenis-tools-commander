import random
import string

import pytest
from requests import HTTPError

from mcmd.__main__ import start
from tests.integration.test_context import TestContext

"""
At the beginning of the tests, create one test context that will be shared among all tests
"""
_test_context = TestContext()


def run_commander(arg_string):
    """Runs the commander and asserts that the exit code was 0."""
    exit_code = start(['mcmd'] + arg_string.split(' '), _test_context)
    assert exit_code == 0


def run_commander_fail(arg_string):
    """Runs the commander without failing the test if the command fails"""
    with pytest.raises(SystemExit):
        start(['mcmd'] + arg_string.split(' '), _test_context)


def random_name():
    return ''.join(random.choices(string.ascii_uppercase, k=6))


def setup_entity():
    """Imports an entity with a different identifier each time."""
    package_name = random_name()
    run_commander('add package {}'.format(package_name))
    run_commander('import testAutoId_unpackaged --in {}'.format(package_name))
    return '{}_testAutoId'.format(package_name)


def entity_type_exists(session, id_):
    try:
        session.get_entity_meta_data(id_)
    except HTTPError:
        return False
    return True


def package_exists(session, id_):
    try:
        session.get_by_id('sys_md_Package', id_)
    except HTTPError:
        return False
    return True


def entity_is_empty(session, id_):
    return len(session.get(id_)) == 0
