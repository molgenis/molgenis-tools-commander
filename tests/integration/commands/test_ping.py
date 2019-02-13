from unittest import mock

import pytest

import mcmd.config.config as config
from tests.integration.utils import run_commander


@pytest.mark.integration
def test_ping_online(capsys):
    run_commander('ping')

    captured = capsys.readouterr().out
    assert 'Online' in captured
    assert 'Version' in captured
    assert config.get('host', 'selected') in captured
    assert config.username() in captured


@pytest.mark.integration
@mock.patch('mcmd.config.config.api')
def test_ping_offline(api_mock, capsys):
    api_mock.return_value = 'https://nonexisting.url'
    run_commander('ping')

    captured = capsys.readouterr().out
    assert 'Offline' in captured
    assert 'Version' not in captured
    assert config.get('host', 'selected') in captured
    assert config.username() in captured
