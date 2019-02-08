import pytest

from tests.integration.conftest import random_name, run_commander


@pytest.mark.integration
def test_add_package(session):
    name = random_name()
    exit_code = run_commander('add package {}'.format(name))
    assert exit_code == 1

    package = session.get_by_id('sys_md_Package', name)
    assert 'parent' not in package


@pytest.mark.integration
def test_add_package_in_package(session):
    name1 = random_name()
    name2 = random_name()
    exit_code1 = run_commander('add package {}'.format(name1))
    exit_code2 = run_commander('add package {} --in {}'.format(name2, name1))
    assert exit_code1 == 1
    assert exit_code2 == 1

    package = session.get_by_id('sys_md_Package', name2, expand=['parent'])
    assert package['parent']['id'] == name1
