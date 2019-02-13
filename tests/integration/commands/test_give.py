import pytest

from tests.integration.permission_client import get_user_plugin_permissions, get_user_entity_permissions, \
    get_user_package_permissions, get_role_entity_permissions
from tests.integration.utils import run_commander, setup_entity


@pytest.fixture(scope='module')
def entity_type():
    return setup_entity()


@pytest.mark.integration
def test_give_user_plugin(session, user):
    run_commander('give {} read mappingservice'.format(user))

    permissions = get_user_plugin_permissions(session, user)
    assert permissions['mappingservice'] == ['read']


@pytest.mark.integration
def test_give_user_plugin_explicit(session, user):
    run_commander('give --user {} read --plugin dataexplorer'.format(user))

    permissions = get_user_plugin_permissions(session, user)
    assert permissions['dataexplorer'] == ['read']


@pytest.mark.integration
def test_give_user_entity(session, entity_type, user):
    run_commander('give {} write {}'.format(user, entity_type))

    permissions = get_user_entity_permissions(session, user)
    assert permissions[entity_type] == ['write']


@pytest.mark.integration
def test_give_user_entity_explicit(session, entity_type, user):
    run_commander('give --user {} count --entity-type {}'.format(user, entity_type))

    permissions = get_user_entity_permissions(session, user)
    assert permissions[entity_type] == ['count']


@pytest.mark.integration
def test_give_user_package(session, user, package):
    run_commander('give {} writemeta {}'.format(user, package))

    permissions = get_user_package_permissions(session, user)
    assert permissions[package] == ['writemeta']


@pytest.mark.integration
def test_give_user_package_explicit(session, user, package):
    run_commander('give --user {} writemeta --package {}'.format(user, package))

    permissions = get_user_package_permissions(session, user)
    assert permissions[package] == ['writemeta']


@pytest.mark.integration
def test_give_role_entity_explicit(session, entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give {} read {}'.format(role_name, entity_type))

    permissions = get_role_entity_permissions(session, role_name)
    assert permissions[entity_type] == ['read']


@pytest.mark.integration
def test_give_role_entity_explicit(session, entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give --role {} write --entity-type {}'.format(role_name, entity_type))

    permissions = get_role_entity_permissions(session, role_name)
    assert permissions[entity_type] == ['write']


@pytest.mark.integration
def test_give_permission_synonyms(session, entity_type, user):
    run_commander('give {} view {}'.format(user, entity_type))

    permissions = get_user_entity_permissions(session, user)
    assert permissions[entity_type] == ['read']
