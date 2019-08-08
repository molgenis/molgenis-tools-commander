import pytest
from mock import patch

from tests.integration.utils import run_commander


# @pytest.mark.local
# @patch('mcmd.io.io.input_')
# def test_backup(which_name):
#     which_name.return_value = 'test'
#     run_commander('backup --database')


@pytest.mark.local
@patch('mcmd.io.io.input_')
def test_backup_filestore(which_name):
    which_name.return_value = 'test'
    run_commander('backup --filestore')


@pytest.mark.local
@patch('mcmd.io.io.input_')
def test_backup_minio(which_name):
    which_name.return_value = 'test'
    run_commander('backup --minio')
