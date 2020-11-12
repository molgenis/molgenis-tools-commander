import pytest

from mcmd.molgenis.security.permission import Permission
from mcmd.molgenis.security.permissions_api import get_user_plugin_permission, get_user_entity_type_permission, \
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
def test_give_user_plugin(user):
    run_commander('give {} read mappingservice'.format(user))

    permission = get_user_plugin_permission('mappingservice', user)
    assert permission == Permission.READ


@pytest.mark.integration
def test_give_user_plugin_explicit(user):
    run_commander('give --user {} read --plugin dataexplorer'.format(user))

    permission = get_user_plugin_permission('dataexplorer', user)
    assert permission == Permission.READ


@pytest.mark.integration
def test_give_user_entity_type(entity_type, user):
    run_commander('give {} write {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(entity_type, user)
    assert permission == Permission.WRITE


@pytest.mark.integration
def test_give_user_entity_type_overwrite(entity_type, user):
    run_commander('give {} write {}'.format(user, entity_type))
    run_commander('give {} read {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(entity_type, user)
    assert permission == Permission.READ


@pytest.mark.integration
def test_give_user_entity_type_none(entity_type, user):
    run_commander('give {} write {}'.format(user, entity_type))
    run_commander('give {} none {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(entity_type, user)
    assert permission is Permission.NONE


@pytest.mark.integration
def test_give_user_entity_type_explicit(entity_type, user):
    run_commander('give --user {} count --entity-type {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(entity_type, user)
    assert permission == Permission.COUNT


@pytest.mark.integration
def test_give_user_package(user, package):
    run_commander('give {} writemeta {}'.format(user, package))

    permission = get_user_package_permission(package, user)
    assert permission == Permission.WRITEMETA


@pytest.mark.integration
def test_give_user_package_explicit(user, package):
    run_commander('give --user {} writemeta --package {}'.format(user, package))

    permission = get_user_package_permission(package, user)
    assert permission == Permission.WRITEMETA


@pytest.mark.integration
def test_give_role_entity_type_explicit(entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give {} read {}'.format(role_name, entity_type))

    permission = get_role_entity_type_permission(entity_type, role_name)
    assert permission == Permission.READ


@pytest.mark.integration
def test_give_role_entity_type_explicit(entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give --role {} write --entity-type {}'.format(role_name, entity_type))

    permission = get_role_entity_type_permission(entity_type, role_name)
    assert permission == Permission.WRITE


@pytest.mark.integration
def test_give_permission_synonyms(entity_type, user):
    run_commander('give {} view {}'.format(user, entity_type))

    permission = get_user_entity_type_permission(entity_type, user)
    assert permission == Permission.READ


@pytest.mark.integration
def test_give_user_entity(rls_entity_type, user):
    run_commander('give {} write {} --entity {}'.format(user, rls_entity_type, 1))

    permission = get_user_entity_permission(rls_entity_type, 1, user)
    assert permission == Permission.WRITE


@pytest.mark.integration
def test_give_role_entity(rls_entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give {} write {} --entity {}'.format(role_name, rls_entity_type, 1))

    permission = get_role_entity_permission(rls_entity_type, 1, role_name)
    assert permission == Permission.WRITE


@pytest.mark.integration
def test_give_role_entity_explicit(rls_entity_type, group):
    role_name = group + '_EDITOR'
    run_commander('give --role {} write --entity-type {} --entity {}'.format(role_name, rls_entity_type, 1))

    permission = get_role_entity_permission(rls_entity_type, 1, role_name)
    assert permission == Permission.WRITE


@pytest.mark.integration
def test_give_user_entity_overwrite(rls_entity_type, user):
    run_commander('give {} write {} --entity {}'.format(user, rls_entity_type, 1))
    run_commander('give {} read {} --entity {}'.format(user, rls_entity_type, 1))

    permission = get_user_entity_permission(rls_entity_type, 1, user)
    assert permission == Permission.READ


@pytest.mark.integration
def test_give_user_entity_none(rls_entity_type, user):
    run_commander('give {} write {} --entity {}'.format(user, rls_entity_type, 1))
    run_commander('give {} none {} --entity {}'.format(user, rls_entity_type, 1))

    permission = get_user_entity_permission(rls_entity_type, 1, user)
    assert permission is Permission.NONE


@pytest.mark.integration
def test_give_user_entity_illegal_permission(rls_entity_type, user):
    run_commander_fail('give {} readmeta {} --entity {}'.format(user, rls_entity_type, 1))
