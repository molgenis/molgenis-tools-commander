from unittest import mock

import pytest

import mcmd.config.config as config
from tests.integration.conftest import run_commander


@pytest.mark.integration
def test_ping_online(capsys):
    exit_code = run_commander('ping')
    assert exit_code == 1

    captured = capsys.readouterr().out
    assert 'Online' in captured
    assert 'Version' in captured
    assert config.get('host', 'selected') in captured
    assert config.username() in captured


# noinspection PyUnusedLocal
@pytest.mark.integration
@mock.patch('mcmd.config.config.api', return_value='https://nonexisting.url')
def test_ping_offline(api_mock, capsys):
    exit_code = run_commander('ping')
    assert exit_code == 1

    captured = capsys.readouterr().out
    assert 'Offline' in captured
    assert 'Version' not in captured
    assert config.get('host', 'selected') in captured
    assert config.username() in captured
