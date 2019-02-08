import pytest

from tests.integration.conftest import run_commander, random_name


@pytest.mark.integration
def test_give(session):
    username = random_name()
    run_commander('add user {}'.format(username))

    package_name = random_name()
    run_commander('add package {}'.format(package_name))

    exit_code = run_commander('give {} write {}'.format(username, package_name))
    assert exit_code == 1

