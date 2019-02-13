import pytest

from tests.integration.utils import run_commander


def _get_memberships_by_name_and_role(username, role_name, session):
    memberships = session.get('sys_sec_RoleMembership', expand=['user', 'role'])
    found = []
    for membership in memberships:
        if membership['user']['username'] == username and membership['role']['name'] == role_name:
            found.append(membership)
    return found


@pytest.mark.integration
def test_make(session, user, group):
    role_name = '{}_MANAGER'.format(group.upper())
    run_commander('make {} {}'.format(user, role_name))

    memberships = _get_memberships_by_name_and_role(user, role_name, session)

    assert len(memberships) == 1
