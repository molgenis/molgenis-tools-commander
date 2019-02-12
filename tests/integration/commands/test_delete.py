import pytest
from mock import patch
from requests import HTTPError

from tests.integration.conftest import run_commander, random_name


def _setup_entity():
    package_name = random_name()
    run_commander('add package {}'.format(package_name))
    run_commander('import testAutoId_unpackaged --in {}'.format(package_name))
    return '{}_testAutoId'.format(package_name)


def _entity_type_exists(session, id_):
    try:
        session.get_entity_meta_data(id_)
    except HTTPError:
        return False
    return True


def _entity_is_empty(session, id_):
    return len(session.get(id_)) == 0


@pytest.mark.integration
@patch('mcmd.io.confirm')
def test_delete_entity(are_you_sure, session):
    are_you_sure.return_value = True
    entity_id = _setup_entity()
    run_commander('delete entity {}'.format(entity_id))

    assert not _entity_type_exists(session, entity_id)


@pytest.mark.integration
@patch('mcmd.io.confirm')
def test_delete_entity_cancel(are_you_sure, session):
    are_you_sure.return_value = False
    entity_id = _setup_entity()
    run_commander('delete entity {}'.format(entity_id))

    assert _entity_type_exists(session, entity_id)


@pytest.mark.integration
def test_delete_entity_force(session):
    entity_id = _setup_entity()
    run_commander('delete --force entity {}'.format(entity_id))

    assert not _entity_type_exists(session, entity_id)


@pytest.mark.integration
@patch('mcmd.io.confirm')
def test_delete_data(are_you_sure, session):
    are_you_sure.return_value = True
    entity_id = _setup_entity()
    run_commander('delete data {}'.format(entity_id))

    assert _entity_is_empty(session, entity_id)


@pytest.mark.integration
@patch('mcmd.io.confirm')
def test_delete_data_cancel(are_you_sure, session):
    are_you_sure.return_value = False
    entity_id = _setup_entity()
    run_commander('delete data {}'.format(entity_id))

    assert not _entity_is_empty(session, entity_id)


@pytest.mark.integration
def test_delete_data_force(session):
    entity_id = _setup_entity()
    run_commander('delete --force data {}'.format(entity_id))

    assert _entity_is_empty(session, entity_id)
