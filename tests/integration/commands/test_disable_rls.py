from unittest.mock import patch

import pytest

from mcmd.molgenis.security.permissions_api import is_row_level_secured
from tests.integration.utils import run_commander


@pytest.mark.integration
@patch('mcmd.in_out.ask.confirm')
def test_disable_rls(are_you_sure, entity_type):
    are_you_sure.return_value = True
    run_commander('enable rls {}'.format(entity_type))
    run_commander('disable rls {}'.format(entity_type))

    assert not is_row_level_secured(entity_type)


@pytest.mark.integration
@patch('mcmd.in_out.ask.confirm')
def test_disable_rls_cancel(are_you_sure, entity_type):
    are_you_sure.return_value = False
    run_commander('enable rls {}'.format(entity_type))
    run_commander('disable rls {}'.format(entity_type))

    assert is_row_level_secured(entity_type)
