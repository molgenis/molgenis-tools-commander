import pytest

from tests.integration.utils import run_commander


@pytest.mark.integration
def test_set(session):
    run_commander('set app title MyApp')

    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'MyApp'


@pytest.mark.integration
def test_set_entity_name(session):
    run_commander('set sys_set_app title MyAppFullName')

    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'MyAppFullName'


@pytest.mark.integration
def test_set_not_setting_fail():
    with pytest.raises(SystemExit):
        run_commander('set sys_Language code nl')


@pytest.mark.integration
def test_set_not_setting(session):
    run_commander('set sys_Language active true --for fr')
    lang = session.get_by_id('sys_Language', 'fr')
    assert lang['active']
