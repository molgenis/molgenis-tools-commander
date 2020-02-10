from unittest.mock import patch

import pytest

from tests.integration.utils import run_commander, random_name


def _get_user_id(username, session):
    return session.get('sys_sec_User', q=[{
        'field': 'username',
        'operator': 'EQUALS',
        'value': username
    }])[0]['id']


def _get_role_id(rolename, session):
    return session.get('sys_sec_Role', q=[{
        'field': 'name',
        'operator': 'EQUALS',
        'value': rolename
    }])[0]['id']


def _get_memberships_by_username(username, session):
    memberships = session.get('sys_sec_RoleMembership',
                              q=[{
                                  'field': 'user',
                                  'operator': 'EQUALS',
                                  'value': _get_user_id(username, session)
                              }],
                              expand=['user', 'role'])
    return memberships


def _get_memberships_by_user_and_role(username, rolename, session):
    memberships = session.get('sys_sec_RoleMembership',
                              q=[{
                                  'field': 'user',
                                  'operator': 'EQUALS',
                                  'value': _get_user_id(username, session)
                              }, {
                                  'operator': 'AND'
                              }, {
                                  'field': 'role',
                                  'operator': 'EQUALS',
                                  'value': _get_role_id(rolename, session)
                              }],
                              expand=['user', 'role'])
    return memberships


@pytest.mark.integration
def test_make_group_member(session, user, group):
    role_name = '{}_MANAGER'.format(group)

    run_commander('make {} {}'.format(user, role_name))

    memberships = _get_memberships_by_username(user, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == role_name


# noinspection DuplicatedCode
@pytest.mark.integration
@patch('mcmd.io.ask.confirm')
def test_make_group_member_update_cancel(update_yes_no, session, user, group):
    update_yes_no.return_value = False
    original_role_name = '{}_VIEWER'.format(group)
    run_commander('make {} {}'.format(user, original_role_name))

    new_role_name = '{}_MANAGER'.format(group)
    run_commander('make {} {}'.format(user, new_role_name))

    memberships = _get_memberships_by_username(user, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == original_role_name


# noinspection DuplicatedCode
@pytest.mark.integration
@patch('mcmd.io.ask.confirm')
def test_make_group_member_update(update_yes_no, session, user, group):
    update_yes_no.return_value = True
    original_role_name = '{}_VIEWER'.format(group)
    run_commander('make {} {}'.format(user, original_role_name))

    new_role_name = '{}_MANAGER'.format(group)
    run_commander('make {} {}'.format(user, new_role_name))

    memberships = _get_memberships_by_username(user, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == new_role_name


@pytest.mark.integration
def test_make_group_member_update_identical(session, user, group):
    role_name = '{}_VIEWER'.format(group)
    run_commander('make {} {}'.format(user, role_name))
    run_commander('make {} {}'.format(user, role_name))

    memberships = _get_memberships_by_username(user, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == role_name


@pytest.mark.integration
def test_make_role_member(session, user):
    role_name = random_name()
    run_commander('add role {}'.format(role_name))
    run_commander('make {} {}'.format(user, role_name))

    memberships = _get_memberships_by_user_and_role(user, role_name, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == role_name


# noinspection DuplicatedCode
@pytest.mark.integration
def test_make_role_member_update_identical(session, user):
    role_name = random_name()
    run_commander('add role {}'.format(role_name))
    run_commander('make {} {}'.format(user, role_name))
    run_commander('make {} {}'.format(user, role_name))

    memberships = _get_memberships_by_user_and_role(user, role_name, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == role_name
