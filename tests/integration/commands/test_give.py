import pytest

from tests.integration.permission_client import get_user_plugin_permission, get_user_entity_type_permission, \
    get_user_package_permission, get_role_entity_type_permission, get_user_entity_permission, get_role_entity_permission
from tests.integration.utils import run_commander, setup_entity, run_commander_fail


@pytest.fixture(scope='module')
def entity_type():
    return setup_entity()


@pytest.fixture(scope='module')
def rls_entity_type():
    run_commander('import {}'.format('mcmd_person'))
    run_commander('enable rls mcmd_person')
    yield 'mcmd_person'
    run_commander('delete --force --entity-type mcmd_person')


@pytest.mark.integration
def test_give_user_plugin(session, user):
    run_commander('give {} read mappingservice'.format(user))

    permission = get_user_plugin_permission(session, 'mappingservice', user)
    assert permission == 'READ'


@pytest.mark.integration
def test_give_user_plugin_explicit(session, user):
    run_commander('give --user {} read --plugin dataexplorer'.format(user))

    permission = get_user_plugin_permission(session, 'dataexplorer', user)
    assert permission == 'READ'


@pytest.mark.integration
def test_give_user_entity_type(session, entity_type, user):
    run_commander('give {} write {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(session, entity_type, user)
    assert permission == 'WRITE'


@pytest.mark.integration
def test_give_user_entity_type_overwrite(session, entity_type, user):
    run_commander('give {} write {}'.format(user, entity_type))
    run_commander('give {} read {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(session, entity_type, user)
    assert permission == 'READ'


@pytest.mark.integration
def test_give_user_entity_type_none(session, entity_type, user):
    run_commander('give {} write {}'.format(user, entity_type))
    run_commander('give {} none {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(session, entity_type, user)
    assert permission is None


@pytest.mark.integration
def test_give_user_entity_type_explicit(session, entity_type, user):
    run_commander('give --user {} count --entity-type {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(session, entity_type, user)
    assert permission == 'COUNT'


@pytest.mark.integration
def test_give_user_package(session, user, package):
    run_commander('give {} writemeta {}'.format(user, package))

    permission = get_user_package_permission(session, package, user)
    assert permission == 'WRITEMETA'


@pytest.mark.integration
def test_give_user_package_explicit(session, user, package):
    run_commander('give --user {} writemeta --package {}'.format(user, package))

    permission = get_user_package_permission(session, package, user)
    assert permission == 'WRITEMETA'


@pytest.mark.integration
def test_give_role_entity_type_explicit(session, entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give {} read {}'.format(role_name, entity_type))

    permission = get_role_entity_type_permission(session, entity_type, role_name)
    assert permission == 'READ'


@pytest.mark.integration
def test_give_role_entity_type_explicit(session, entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give --role {} write --entity-type {}'.format(role_name, entity_type))

    permission = get_role_entity_type_permission(session, entity_type, role_name)
    assert permission == 'WRITE'


@pytest.mark.integration
def test_give_permission_synonyms(session, entity_type, user):
    run_commander('give {} view {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(session, entity_type, user)
    assert permission == 'READ'


@pytest.mark.integration
def test_give_user_entity(session, rls_entity_type, user):
    run_commander('give {} write {} --entity {}'.format(user, rls_entity_type, 1))

    permission = get_user_entity_permission(session, rls_entity_type, 1, user)
    assert permission == 'WRITE'


@pytest.mark.integration
def test_give_role_entity(session, rls_entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give {} write {} --entity {}'.format(role_name, rls_entity_type, 1))

    permission = get_role_entity_permission(session, rls_entity_type, 1, role_name)
    assert permission == 'WRITE'


@pytest.mark.integration
def test_give_role_entity_explicit(session, rls_entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give --role {} write --entity-type {} --entity {}'.format(role_name, rls_entity_type, 1))

    permission = get_role_entity_permission(session, rls_entity_type, 1, role_name)
    assert permission == 'WRITE'


@pytest.mark.integration
def test_give_user_entity_overwrite(session, rls_entity_type, user):
    run_commander('give {} write {} --entity {}'.format(user, rls_entity_type, 1))
    run_commander('give {} read {} --entity {}'.format(user, rls_entity_type, 1))

    permission = get_user_entity_permission(session, rls_entity_type, 1, user)
    assert permission == 'READ'


@pytest.mark.integration
def test_give_user_entity_none(session, rls_entity_type, user):
    run_commander('give {} write {} --entity {}'.format(user, rls_entity_type, 1))
    run_commander('give {} none {} --entity {}'.format(user, rls_entity_type, 1))

    permission = get_user_entity_permission(session, rls_entity_type, 1, user)
    assert permission is None


@pytest.mark.integration
def test_give_user_entity_illegal_permission(session, rls_entity_type, user):
    run_commander_fail('give {} readmeta {} --entity {}'.format(user, rls_entity_type, 1))
