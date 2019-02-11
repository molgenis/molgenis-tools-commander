import pytest

from tests.integration.conftest import random_name, run_commander


def _get_memberships_by_name_and_role(username, role_name, session):
    memberships = session.get('sys_sec_RoleMembership', expand=['user', 'role'])
    found = []
    for membership in memberships:
        if membership['user']['username'] == username and membership['role']['name'] == role_name:
            found.append(membership)
    return found


@pytest.mark.integration
def test_make(session):
    username = random_name()
    run_commander('add user {}'.format(username))

    group_name = random_name()
    run_commander('add group {}'.format(group_name))

    role_name = '{}_MANAGER'.format(group_name.upper())
    run_commander('make {} {}'.format(username, role_name))

    memberships = _get_memberships_by_name_and_role(username, role_name, session)

    assert len(memberships) == 1
