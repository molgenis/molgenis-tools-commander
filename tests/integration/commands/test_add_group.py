import pytest

from tests.integration.utils import run_commander, random_name


def group_by_name_query(name):
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
    run_commander('add group {}'.format(name))

    result = session.get('sys_sec_Group', q=group_by_name_query(name.lower()))
    assert len(result) == 1
