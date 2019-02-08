import pytest

from tests.integration.conftest import run_commander, random_name


def _group_by_name_query(name):
    return [{
        "field": "name",
        "operator": "EQUALS",
        "value": name
    }]


def _random_group_name():
    return '{}-{}'.format(random_name(), random_name())


@pytest.mark.integration
def test_add_group(session):
    name = _random_group_name()
    exit_code = run_commander('add group {}'.format(name))
    assert exit_code == 1

    result = session.get('sys_sec_Group', q=_group_by_name_query(name.lower()))
    assert len(result) == 1
