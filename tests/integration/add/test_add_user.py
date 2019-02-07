import molgenis.client
import pytest
from requests import HTTPError

from tests.integration.conftest import run_commander, random_name


def _user_by_name_query(name):
    return [{
        "field": "username",
        "operator": "EQUALS",
        "value": name
    }]


def _user_can_login(username, password):
    session = molgenis.client.Session('http://localhost:8080/api/')
    try:
        session.login(username, password)
    except HTTPError:
        return False
    else:
        return True


@pytest.mark.integration
def test_add_user(session):
    name = random_name()
    exit_code = run_commander('add user {}'.format(name))
    assert exit_code == 1

    assert _user_can_login(name, name)

    result = session.get('sys_sec_User', q=_user_by_name_query(name))
    assert len(result) == 1

    user = result[0]
    assert user['Email'] == '{}@molgenis.org'.format(name)
    assert user['active'] is True
    assert user['superuser'] is False
    assert user['changePassword'] is False


@pytest.mark.integration
def test_add_user_email(session):
    name = random_name()
    exit_code = run_commander('add user {} --with-email {}@test.nl'.format(name, name))
    assert exit_code == 1

    assert _user_can_login(name, name)

    result = session.get('sys_sec_User', q=_user_by_name_query(name))
    assert len(result) == 1

    user = result[0]
    assert user['Email'] == '{}@test.nl'.format(name)
    assert user['active'] is True
    assert user['superuser'] is False
    assert user['changePassword'] is False


@pytest.mark.integration
def test_add_user_superuser_change_password(session):
    name = random_name()
    exit_code = run_commander('add user {} --is-superuser --change-password'.format(name))
    assert exit_code == 1

    assert _user_can_login(name, name) is False

    result = session.get('sys_sec_User', q=_user_by_name_query(name))
    assert len(result) == 1

    user = result[0]
    assert user['Email'] == '{}@molgenis.org'.format(name)
    assert user['active'] is True
    assert user['superuser'] is True
    assert user['changePassword'] is True


@pytest.mark.integration
def test_add_user_inactive(session):
    name = random_name()
    exit_code = run_commander('add user {} --is-inactive'.format(name))
    assert exit_code == 1

    assert _user_can_login(name, name) is False

    result = session.get('sys_sec_User', q=_user_by_name_query(name))
    assert len(result) == 1

    user = result[0]
    assert user['Email'] == '{}@molgenis.org'.format(name)
    assert user['active'] is False
    assert user['superuser'] is False
    assert user['changePassword'] is False


@pytest.mark.integration
def test_add_user_set_password(session):
    name = random_name()
    password = 's3cr3tp4ssw0rd'
    exit_code = run_commander('add user {} --set-password {}'.format(name, password))
    assert exit_code == 1

    assert _user_can_login(name, password)

    result = session.get('sys_sec_User', q=_user_by_name_query(name))
    assert len(result) == 1

    user = result[0]
    assert user['Email'] == '{}@molgenis.org'.format(name)
    assert user['active'] is True
    assert user['superuser'] is False
    assert user['changePassword'] is False
