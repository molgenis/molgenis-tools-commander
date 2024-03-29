import os
from unittest import mock
from unittest.mock import patch, mock_open

import pytest

from tests.integration.loader_mock import get_files_folder
from tests.integration.utils import run_commander, get_test_context

_expected_list_messages = [file for file in os.listdir(get_files_folder().joinpath('scripts'))]
_expected_read_messages = ['add package scripttest', 'import testAutoId_unpackaged --in scripttest',
                           'add package otherpackage']
_history_lines = [
    'add user henk',
    'add group test',
    'make henk test_viewer'
]


@pytest.mark.integration
def test_script_list(caplog):
    run_commander('script --list')
    assert caplog.messages == _expected_list_messages


@pytest.mark.integration
def test_script_read(caplog):
    run_commander('script --read test_script')
    assert caplog.messages == _expected_read_messages


@pytest.mark.integration
@patch('mcmd.in_out.ask.input_')
@patch('mcmd.in_out.ask.checkbox')
@patch('mcmd.core.history.read')
def test_script_create(history, which_lines, what_filename):
    history.return_value = _history_lines
    which_lines.return_value = ['add user henk', 'add group test']
    what_filename.return_value = 'test'

    with patch("builtins.open", mock_open()) as mock_file:
        run_commander('script')
        mock_file.assert_called_with(str(get_test_context().get_scripts_folder().joinpath('test')), 'w')
        mock_file().write.assert_has_calls([
            mock.call('add user henk\n'),
            mock.call('add group test\n')
        ])
