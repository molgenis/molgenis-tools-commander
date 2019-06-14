import pytest

from tests.integration.utils import run_commander


@pytest.mark.integration
def test_enable_language(session):
    session.update_one('sys_Language', 'nl', 'active', True)

    run_commander('disable language nl')
    assert session.get_by_id('sys_Language', 'nl')['active'] is False
