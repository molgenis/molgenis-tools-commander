"""
These tests test the commands that interact with the backend resources of MOLGENIS (database, filestore and MinIO). They
don't require a running MOLGENIS application
"""

import tarfile
import tempfile
from pathlib import Path

import pytest
from mock import patch

from mcmd.backend.database import Database
from mcmd.backend.files import Filestore, MinIO
from tests.integration.home_mock import get_backups_folder
from tests.integration.loader_mock import get_files_folder
from tests.integration.utils import run_commander


def setup_module():
    print("SETUP BEFORE MODULE: backing up current database/filestore/minio")
    run_commander('backup --all --name backup_original')
    print("SETUP DONE")


def teardown_module():
    print("\nTEARDOWN AFTER MODULE: restoring original database/filestore/minio")
    run_commander('drop --all --force')
    run_commander('restore backup_original')
    print("TEARDOWN DONE")


def setup_function():
    print("\nSETUP BEFORE TEST: reset test database/filestore/minio")
    run_commander('drop --all --force')
    run_commander('restore --from-path {}'.format(get_files_folder().joinpath('test_backup.tar.gz')))
    print("SETUP DONE")


@pytest.mark.local
@patch('mcmd.io.io.input_')
def test_backup_database(which_name):
    which_name.return_value = 'backup_db'
    run_commander('backup --database')

    backup = get_backups_folder().joinpath('backup_db.tar.gz')
    assert backup.exists()
    with tarfile.open(backup) as archive:
        _assert_correct_database(archive)
        assert not _archive_has_member(archive, 'filestore')
        assert not _archive_has_member(archive, 'minio')


@pytest.mark.local
def test_backup_filestore():
    path = get_backups_folder()
    run_commander('backup --filestore --name backup_filestore --to-path {}'.format(path))

    backup = get_backups_folder().joinpath('backup_filestore.tar.gz')
    assert backup.exists()
    with tarfile.open(backup) as archive:
        _assert_correct_filestore(archive)
        assert not _archive_has_member(archive, 'database/dump.sql')
        assert not _archive_has_member(archive, 'minio')


@pytest.mark.local
def test_backup_minio():
    run_commander('backup --minio --name backup_minio')

    backup = get_backups_folder().joinpath('backup_minio.tar.gz')
    assert backup.exists()
    with tarfile.open(backup) as archive:
        _assert_correct_minio(archive)
        assert not _archive_has_member(archive, 'filestore')
        assert not _archive_has_member(archive, 'database/dump.sql')


@pytest.mark.local
def test_restore():
    # backup MOLGENIS
    run_commander('backup --all --name backup_all')

    # confirm the backup contains the correct data
    backup = get_backups_folder().joinpath('backup_all.tar.gz')
    assert backup.exists()
    with tarfile.open(backup) as archive:
        _assert_correct_database(archive)
        _assert_correct_filestore(archive)
        _assert_correct_minio(archive)

    # drop the backend
    run_commander('drop --all --force')

    # restore the backup
    run_commander('restore backup_all')

    # confirm the restore was succesful by backing up again and inspecting the contents
    run_commander('backup --all --name check_backup')
    backup = get_backups_folder().joinpath('check_backup.tar.gz')
    assert backup.exists()
    with tarfile.open(backup) as archive:
        _assert_correct_database(archive)
        _assert_correct_filestore(archive)
        _assert_correct_minio(archive)


@pytest.mark.local
@patch('mcmd.io.io.confirm')
def test_drop_filestore(are_you_sure):
    are_you_sure.return_value = True
    run_commander('drop --filestore')

    assert Filestore.instance().is_empty()


@pytest.mark.local
@patch('mcmd.io.io.confirm')
def test_drop_cancel(are_you_sure):
    are_you_sure.return_value = False
    run_commander('drop --filestore')

    assert not Filestore.instance().is_empty()


@pytest.mark.local
def test_drop_minio():
    run_commander('drop --minio --force')

    assert MinIO.instance().is_empty()


@pytest.mark.local
def test_drop_database():
    run_commander('drop --database --force')

    temp_file = Path(tempfile.mkstemp()[1])
    Database.instance().dump(temp_file)
    assert temp_file.stat().st_size < 500


def _archive_has_member(archive, member):
    try:
        archive.getmember(member)
    except KeyError:
        return False
    else:
        return True


def _assert_correct_database(archive):
    file = archive.extractfile(archive.getmember('database/dump.sql'))
    assert 'it_emx_autoid_testAutoId' in str(file.read())


def _assert_correct_filestore(archive):
    assert _archive_has_member(archive, 'filestore/it_emx_autoid.xlsx')


def _assert_correct_minio(archive):
    file = archive.extractfile(archive.getmember('minio/molgenis/aaaac3fyiq74lzw2vuwyxoyaae'))
    assert file.read() == b'minio test file'
