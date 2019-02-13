import pytest

from tests.integration.utils import run_commander


@pytest.mark.integration
def test_enable_theme(session):
    run_commander('enable theme lumen')
    settings = session.get('sys_set_app')[0]

    assert settings['bootstrap_theme'] == 'bootstrap-lumen.min.css'


@pytest.mark.integration
def test_enable_theme_full_name(session):
    run_commander('enable theme bootstrap-darkly.min.css')
    settings = session.get('sys_set_app')[0]

    assert settings['bootstrap_theme'] == 'bootstrap-darkly.min.css'


@pytest.mark.integration
def test_enable_uploaded_theme(session):
    run_commander('add theme --bootstrap3 test3')
    run_commander('enable theme test3')

    settings = session.get('sys_set_app')[0]
    assert settings['bootstrap_theme'] == 'test3.css'

    # cleanup
    run_commander('enable theme molgenis')
    session.delete('sys_set_StyleSheet', 'test3.css')
