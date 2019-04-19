import pytest
from mock import patch

from tests.integration.permission_client import entity_is_row_level_secured
from tests.integration.utils import run_commander


@pytest.mark.integration
@patch('mcmd.io.io.confirm')
def test_disable_rls(are_you_sure, session, entity_type):
    are_you_sure.return_value = True
    run_commander('enable rls {}'.format(entity_type))
    run_commander('disable rls {}'.format(entity_type))

    assert not entity_is_row_level_secured(session, entity_type)


@pytest.mark.integration
@patch('mcmd.io.io.confirm')
def test_disable_rls_cancel(are_you_sure, session, entity_type):
    are_you_sure.return_value = False
    run_commander('enable rls {}'.format(entity_type))
    run_commander('disable rls {}'.format(entity_type))

    assert entity_is_row_level_secured(session, entity_type)
