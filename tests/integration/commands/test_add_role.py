import pytest

from tests.integration.utils import run_commander, random_name


def role_by_name_query(name):
    return 'name=={}'.format(name)


@pytest.mark.integration
def test_add_role(session):
    name = random_name()
    run_commander('add role {}'.format(name))

    result = session.get('sys_sec_Role', q=role_by_name_query(name))
    assert len(result) == 1


@pytest.mark.integration
def test_add_role_to_group(session, group):
    name = random_name()
    run_commander('add role {} --to-group {}'.format(name, group))

    result = session.get('sys_sec_Role', expand='group', q=role_by_name_query(name))
    assert len(result) == 1
    assert result[0]['group']['name'] == group


@pytest.mark.integration
def test_add_role_includes(session):
    name = random_name()
    run_commander('add role {} --includes VIEWER'.format(name))

    result = session.get('sys_sec_Role', expand='includes', q=role_by_name_query(name))
    assert len(result) == 1
    assert result[0]['includes'][0]['name'] == 'VIEWER'


@pytest.mark.integration
def test_add_role_includes_multiple(session):
    name = random_name()
    run_commander('add role {} --includes VIEWER MANAGER'.format(name))

    result = session.get('sys_sec_Role', expand='includes', q=role_by_name_query(name))
    assert len(result) == 1

    includes = {item['name'] for item in result[0]['includes']}
    assert includes == {'VIEWER', 'MANAGER'}


@pytest.mark.integration
def test_add_role_to_group_and_includes(session, group):
    name = random_name()
    run_commander('add role {} --to-group {} --includes {}_EDITOR'.format(name, group, group))

    result = session.get('sys_sec_Role', expand='group,includes', q=role_by_name_query(name))
    assert len(result) == 1
    assert result[0]['group']['name'] == group
    assert result[0]['includes'][0]['name'] == '{}_EDITOR'.format(group)
