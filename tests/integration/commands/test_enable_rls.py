import pytest

from mcmd.molgenis.security.permissions_api import is_row_level_secured
from tests.integration.utils import run_commander


@pytest.mark.integration
def test_enable_rls(entity_type):
    run_commander('enable rls {}'.format(entity_type))

    assert is_row_level_secured(entity_type)
