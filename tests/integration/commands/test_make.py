import pytest
from mock import patch

from tests.integration.utils import run_commander


def _get_memberships_by_name_and_group(username, session):
    memberships = session.get('sys_sec_RoleMembership', expand=['user', 'role'])
    found = []
    for membership in memberships:
        if membership['user']['username'] == username:
            found.append(membership)
    return found


@pytest.mark.integration
def test_make(session, user, group):
    role_name = '{}_MANAGER'.format(group.upper())
    run_commander('make {} {}'.format(user, role_name))

    memberships = _get_memberships_by_name_and_group(user, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == role_name


@pytest.mark.integration
@patch('mcmd.io.ask.confirm')
def test_make_update_cancel(update_yes_no, session, user, group):
    update_yes_no.return_value = False
    original_role_name = '{}_VIEWER'.format(group.upper())
    run_commander('make {} {}'.format(user, original_role_name))

    new_role_name = '{}_MANAGER'.format(group.upper())
    run_commander('make {} {}'.format(user, new_role_name))

    memberships = _get_memberships_by_name_and_group(user, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == original_role_name


@pytest.mark.integration
@patch('mcmd.io.ask.confirm')
def test_make_update(update_yes_no, session, user, group):
    update_yes_no.return_value = True
    original_role_name = '{}_VIEWER'.format(group.upper())
    run_commander('make {} {}'.format(user, original_role_name))

    new_role_name = '{}_MANAGER'.format(group.upper())
    run_commander('make {} {}'.format(user, new_role_name))

    memberships = _get_memberships_by_name_and_group(user, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == new_role_name


@pytest.mark.integration
def test_make_update_identical(session, user, group):
    role_name = '{}_VIEWER'.format(group.upper())
    run_commander('make {} {}'.format(user, role_name))
    run_commander('make {} {}'.format(user, role_name))

    memberships = _get_memberships_by_name_and_group(user, session)
    assert len(memberships) == 1
    assert memberships[0]['role']['name'] == role_name
