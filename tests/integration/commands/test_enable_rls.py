import pytest

from tests.integration.permission_client import entity_is_row_level_secured
from tests.integration.utils import run_commander


@pytest.mark.integration
def test_enable_rls(session, entity_type):
    run_commander('enable rls {}'.format(entity_type))

    assert entity_is_row_level_secured(session, entity_type)
