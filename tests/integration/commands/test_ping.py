from unittest import mock

import pytest

from mcmd.utils.errors import McmdError
from tests.integration.loader_mock import get_host
from tests.integration.utils import run_commander


@pytest.mark.integration
def test_ping_online(capsys):
    run_commander('ping')

    captured = capsys.readouterr().out
    assert 'Online' in captured
    assert 'Version' in captured
    assert get_host()['url'] in captured
    assert get_host()['username'] in captured


@pytest.mark.integration
@mock.patch('mcmd.version.molgenis_version.get_version')
def test_ping_offline(get_version_mock, capsys):
    get_version_mock.side_effect = McmdError('')
    run_commander('ping')

    captured = capsys.readouterr().out
    assert 'Offline' in captured
    assert 'Version' not in captured
    assert get_host()['url'] in captured
    assert get_host()['username'] in captured
