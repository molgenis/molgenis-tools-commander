from unittest.mock import patch

import pytest

from tests.integration.loader_mock import get_host
from tests.integration.utils import run_commander, random_name, entity_type_exists


@pytest.mark.integration
@patch('mcmd.config.config.set_token')
def test_login_password(set_token, session):
    run_commander('set app title login1')

    assert set_token.called
    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'login1'


@pytest.mark.integration
@patch('mcmd.in_out.ask.password')
@patch('mcmd.config.config._get_selected_host_auth')
@patch('mcmd.config.config.set_token')
def test_login_no_password(set_token_mock, host_mock, enter_password, session):
    test_host = get_host()
    password = test_host['password']
    enter_password.return_value = password

    # remove the password from the host and run a command that requires a login
    test_host.pop('password')
    host_mock.return_value = test_host

    run_commander('set app title login2')

    # after the login a new token should've been set
    assert set_token_mock.called
    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'login2'


@pytest.mark.integration
@patch('mcmd.config.config._get_selected_host_auth')
@patch('mcmd.config.config.set_token')
def test_login_token(set_token_mock, host_mock, session):
    test_host = get_host()
    host_mock.return_value = test_host

    # login and capture the token
    run_commander('set app title something')
    token = set_token_mock.call_args[0][0]
    set_token_mock.reset_mock()

    # use the token on a subsequent command
    test_host['token'] = token
    host_mock.return_value = test_host

    run_commander('set app title login3')

    # because a token was present, no new token should've been set
    assert not set_token_mock.called
    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'login3'


@pytest.mark.integration
@patch('mcmd.config.config._get_selected_host_auth')
@patch('mcmd.config.config.set_token')
def test_login_token_invalid(set_token_mock, host_mock, session):
    # run a command with an invalid token
    test_host = get_host()
    test_host['token'] = 'nonexistingtoken'
    host_mock.return_value = test_host

    run_commander('set app title login4')

    # a new token should've been set
    assert set_token_mock.called
    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'login4'


@pytest.mark.integration
@patch('mcmd.config.config._get_selected_host_auth')
@patch('mcmd.config.config.set_token')
def test_login_token_invalid_login_page(set_token_mock, host_mock, session, package):
    test_host = get_host()
    test_host['token'] = 'nonexistingtoken'
    host_mock.return_value = test_host

    # the import endpoint returns an html login page when the token is invalid
    run_commander('import testAutoId_unpackaged --in {}'.format(package))

    # a new token should've been set
    assert set_token_mock.called
    assert entity_type_exists(session, '{}_testAutoId'.format(package))


@pytest.mark.integration
@patch('mcmd.config.config.set_token')
def test_as_user(set_token_mock, session, user):
    run_commander('give {} write sys_set_app'.format(user))
    set_token_mock.reset_mock()

    run_commander('--as-user {} set app title login5'.format(user))

    # running as a user uses arguments as credentials so no token should've been set
    assert not set_token_mock.called
    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'login5'


@pytest.mark.integration
@patch('mcmd.config.config.set_token')
def test_as_user_with_password(set_token_mock, session):
    name = random_name()
    run_commander('add user {} --set-password test'.format(name))
    run_commander('give {} write sys_set_app'.format(name))
    set_token_mock.reset_mock()

    run_commander('--as-user {} --with-password test set app title login5'.format(name))

    # running as a user uses arguments as credentials so no token should've been set
    assert not set_token_mock.called
    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'login5'
