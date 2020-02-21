import pytest

from mcmd.core.home import get_scripts_folder
from tests.integration.utils import run_commander, entity_type_exists, package_exists


@pytest.mark.integration
def test_run(session):
    run_commander('run test_script')

    try:
        assert entity_type_exists(session, 'scripttest_testAutoId')
        assert package_exists(session, 'otherpackage')
    finally:
        session.delete('sys_md_Package', 'scripttest')
        session.delete('sys_md_Package', 'otherpackage')


@pytest.mark.integration
def test_run_from_path(session):
    run_commander('run --from-path {}'.format(get_scripts_folder().joinpath('test_script')))

    try:
        assert entity_type_exists(session, 'scripttest_testAutoId')
        assert package_exists(session, 'otherpackage')
    finally:
        session.delete('sys_md_Package', 'scripttest')
        session.delete('sys_md_Package', 'otherpackage')


@pytest.mark.integration
def test_run_from_line(session):
    run_commander('run test_script --from-line 3')

    try:
        assert not package_exists(session, 'scripttest')
        assert package_exists(session, 'otherpackage')
    finally:
        session.delete('sys_md_Package', 'otherpackage')


@pytest.mark.integration
def test_run_error(session):
    with pytest.raises(SystemExit):
        run_commander('run test_script_error')

    try:
        assert package_exists(session, 'scripttest')
        assert not package_exists(session, 'package_after_error')
    finally:
        session.delete('sys_md_Package', 'scripttest')


@pytest.mark.integration
def test_run_ignore_error(session):
    run_commander('run test_script_error --ignore-errors')

    try:
        assert package_exists(session, 'scripttest')
        assert package_exists(session, 'package_after_error')
    finally:
        session.delete('sys_md_Package', 'scripttest')
        session.delete('sys_md_Package', 'package_after_error')


@pytest.mark.integration
def test_run_nested_fails(session):
    with pytest.raises(SystemExit):
        run_commander('run test_script_nested')

    assert not package_exists(session, 'scripttest')
    assert not package_exists(session, 'package_after_error')


@pytest.mark.integration
def test_run_quotes(session):
    run_commander('run test_script_quotes')

    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'value between quotes'


@pytest.mark.integration
def test_run_comments(session, caplog):
    run_commander('run test_script_comments')

    settings = session.get('sys_set_app')[0]
    assert settings['title'] == 'test'

    expected_messages = [
        "Let's change the app title",
        '',
        '',
        'Finished'
    ]

    assert caplog.messages == expected_messages
