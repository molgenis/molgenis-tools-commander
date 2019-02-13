import pytest
from mock import patch

from tests.integration.utils import run_commander, entity_type_exists, entity_is_empty


@pytest.mark.integration
@patch('mcmd.io.confirm')
def test_delete_entity(are_you_sure, session, entity_type):
    are_you_sure.return_value = True
    run_commander('delete entity {}'.format(entity_type))

    assert not entity_type_exists(session, entity_type)


@pytest.mark.integration
@patch('mcmd.io.confirm')
def test_delete_entity_cancel(are_you_sure, session, entity_type):
    are_you_sure.return_value = False
    run_commander('delete entity {}'.format(entity_type))

    assert entity_type_exists(session, entity_type)


@pytest.mark.integration
def test_delete_entity_force(session, entity_type):
    run_commander('delete --force entity {}'.format(entity_type))

    assert not entity_type_exists(session, entity_type)


@pytest.mark.integration
@patch('mcmd.io.confirm')
def test_delete_data(are_you_sure, session, entity_type):
    are_you_sure.return_value = True
    run_commander('delete data {}'.format(entity_type))

    assert entity_is_empty(session, entity_type)


@pytest.mark.integration
@patch('mcmd.io.confirm')
def test_delete_data_cancel(are_you_sure, session, entity_type):
    are_you_sure.return_value = False
    run_commander('delete data {}'.format(entity_type))

    assert not entity_is_empty(session, entity_type)


@pytest.mark.integration
def test_delete_data_force(session, entity_type):
    run_commander('delete --force data {}'.format(entity_type))

    assert entity_is_empty(session, entity_type)
