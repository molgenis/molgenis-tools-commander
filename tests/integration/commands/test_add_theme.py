import pytest
from requests import HTTPError

from tests.integration.utils import run_commander
from tests.integration.loader_mock import get_test_resource_folder


def _style_exists(session, id_):
    try:
        session.get_by_id('sys_set_StyleSheet', id_)
    except HTTPError:
        return False
    return True


@pytest.mark.integration
def test_add_theme(session):
    run_commander('add theme --bootstrap3 test3')

    try:
        theme = session.get_by_id('sys_set_StyleSheet',
                                  'test3.css',
                                  expand=['bootstrap3Theme', 'bootstrap4Theme'])

        assert theme['bootstrap3Theme']['filename'] == 'test3.css'
        assert 'bootstrap4Theme' not in theme
    finally:
        session.delete('sys_set_StyleSheet', 'test3.css')


@pytest.mark.integration
def test_add_theme_with_bootstrap4(session):
    run_commander('add theme --bootstrap3 test3 --bootstrap4 test4')

    try:
        theme = session.get_by_id('sys_set_StyleSheet',
                                  'test3.css',
                                  expand=['bootstrap3Theme', 'bootstrap4Theme'])

        assert theme['bootstrap3Theme']['filename'] == 'test3.css'
        assert theme['bootstrap4Theme']['filename'] == 'test4.css'
    finally:
        session.delete('sys_set_StyleSheet', 'test3.css')


@pytest.mark.integration
def test_add_theme_without_bootstrap3(session):
    with(pytest.raises(SystemExit)):
        run_commander('add theme --bootstrap4 test4')

    assert not _style_exists(session, 'test4.css')


@pytest.mark.integration
def test_add_theme_from_path(session):
    file_bs3 = str(get_test_resource_folder().joinpath('test3.css'))
    file_bs4 = str(get_test_resource_folder().joinpath('test4.css'))
    run_commander('add theme --from-path --bootstrap3 {} --bootstrap4 {}'.format(file_bs3, file_bs4))

    try:
        theme = session.get_by_id('sys_set_StyleSheet',
                                  'test3.css',
                                  expand=['bootstrap3Theme', 'bootstrap4Theme'])

        assert theme['bootstrap3Theme']['filename'] == 'test3.css'
        assert theme['bootstrap4Theme']['filename'] == 'test4.css'
    finally:
        session.delete('sys_set_StyleSheet', 'test3.css')
