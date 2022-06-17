from unittest.mock import patch

import pytest

from tests.integration.utils import run_commander, entity_type_exists, entity_is_empty, package_exists, random_name


@pytest.mark.integration
@patch('mcmd.in_out.ask.confirm')
def test_delete_entity(are_you_sure, session, entity_type):
    are_you_sure.return_value = True
    run_commander('delete --entity-type {}'.format(entity_type))

    assert not entity_type_exists(session, entity_type)


@pytest.mark.integration
@patch('mcmd.in_out.ask.confirm')
def test_delete_entity_cancel(are_you_sure, session, entity_type):
    are_you_sure.return_value = False
    run_commander('delete --entity-type {}'.format(entity_type))

    assert entity_type_exists(session, entity_type)


@pytest.mark.integration
@patch('mcmd.in_out.ask.confirm')
def test_delete_force(are_you_sure, session, package):
    run_commander('delete --force --package {}'.format(package))

    assert not are_you_sure.called
    assert not package_exists(session, package)


@pytest.mark.integration
def test_delete_entity_data(session, entity_type):
    run_commander('delete --force --entity-type --data {}'.format(entity_type))

    assert entity_is_empty(session, entity_type)


@pytest.mark.integration
@patch('mcmd.in_out.ask.confirm')
def test_delete_entity_attribute(are_you_sure, session, entity_type):
    are_you_sure.return_value = True
    run_commander('delete --entity-type {} --attribute firstName'.format(entity_type))

    assert len(session.get_entity_meta_data(entity_type)['attributes']) == 2


@pytest.mark.integration
def test_delete_package_contents(session, entity_type):
    package = entity_type.split('_')[0]
    child_package = random_name()
    run_commander('add package {} --in {}'.format(child_package, package))

    run_commander('delete --force --package --contents {}'.format(package))

    assert not entity_type_exists(session, entity_type)
    assert not package_exists(session, child_package)
    assert package_exists(session, package)


@pytest.mark.integration
def test_delete_group(session, group):
    run_commander('delete --force --group {}'.format(group))

    groups = session.get('sys_sec_Group', q='name=={}'.format(group))
    assert len(groups) == 0


@pytest.mark.integration
def test_delete_guess_resource(session, entity_type):
    run_commander('delete --force {}'.format(entity_type))

    assert not package_exists(session, entity_type)
