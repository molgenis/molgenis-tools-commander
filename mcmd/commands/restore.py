import os
import shutil
import subprocess
import tarfile
from distutils.dir_util import copy_tree
from distutils.errors import DistutilsFileError
from pathlib import Path
from tempfile import TemporaryDirectory

from mcmd.commands._registry import arguments
from mcmd.config import config
from mcmd.core.command import command
from mcmd.core.errors import McmdError
from mcmd.core.home import get_backups_folder
from mcmd.io import io


# =========
# Arguments
# =========

@arguments('restore')
def arguments(subparsers):
    p_restore = subparsers.add_parser('restore',
                                      help='Restores a backup')

    p_restore.set_defaults(func=restore,
                           write_to_history=True)
    p_restore.add_argument('name',
                           help='the backup to restore (or path to the backup when using --from-path)')
    p_restore.add_argument('--force', '-f',
                           action='store_true',
                           help='forces the restore without asking for confirmation')
    p_restore.add_argument('--from-path', '-p',
                           action='store_true',
                           help='get a backup from a path instead of the MCMD backup folder')

    return p_restore


# =======
# Methods
# =======

@command
def restore(args):
    backup = _get_backup(args)

    if not args.force and not io.confirm(
            'Are you sure you want to restore this backup? This will overwrite your current database and/or files'):
        return

    _restore_backup(backup)


def _get_backup(args):
    if args.from_path:
        backup = Path(args.name)
    else:
        backup = get_backups_folder().joinpath(args.name + '.tar.gz')
    if not backup.exists():
        raise McmdError("{} doesn't exist".format(backup))
    return backup


def _restore_backup(backup):
    with tarfile.open(backup) as archive:
        try:
            archive.getmember('database/dump.sql')
            _restore_database(archive)
        except KeyError:
            pass

        try:
            archive.getmember('filestore')
            _restore_filestore(archive)
        except KeyError:
            pass

        try:
            archive.getmember('minio')
            _restore_minio(archive)
        except KeyError:
            pass


def _restore_database(archive):
    io.start('Restoring database')

    with TemporaryDirectory() as tempdir:
        archive.extractall(path=tempdir, members=[archive.getmember('database/dump.sql')])
        dumpfile = tempdir + '/database/dump.sql'

        user = config.get('local', 'pg_user')
        os.environ['PGPASSWORD'] = config.get('local', 'pg_password')

        try:
            subprocess.check_output(['psql',
                                     '-U', user,
                                     '-c', 'DROP DATABASE IF EXISTS {}'.format(config.get('local', 'database_name'))],
                                    stderr=subprocess.STDOUT)
            subprocess.check_output(['psql',
                                     '-U', user,
                                     '-c', 'CREATE DATABASE {}'.format(config.get('local', 'database_name'))],
                                    stderr=subprocess.STDOUT)
            subprocess.check_output(['psql',
                                     '-U', user,
                                     'molgenis',
                                     '-f', dumpfile],
                                    stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise McmdError(e.output.decode('ascii').strip())

    io.succeed()


def _restore_filestore(archive):
    io.start('Restoring filestore')
    filestore = Path(config.get('local', 'molgenis_home')).joinpath('data').joinpath('filestore')
    _drop(filestore, "filestore")
    _extract_files(archive, filestore.parent, "filestore")
    io.succeed()


def _restore_minio(archive):
    io.start('Restoring MinIO data')
    minio = Path(config.get('local', 'minio_data'))
    _drop(minio, "MinIO")

    # the minio folder can have any name so we need to extract the folder to a temporary location first
    with TemporaryDirectory() as tempdir:
        _extract_files(archive, tempdir, "minio")
        _copy_files(tempdir + '/minio', minio, 'minio')
    io.succeed()


def _copy_files(backup_location, location, name):
    try:
        copy_tree(str(backup_location), str(location))
    except (DistutilsFileError, OSError) as e:
        raise McmdError("Error restoring {}: {}".format(name, e))


def _drop(location, name):
    try:
        if location.exists():
            shutil.rmtree(location)
    except Exception as e:
        raise McmdError("Error dropping {}: {}".format(name, e))


def _extract_files(archive, location, name):
    try:
        archive.extractall(path=location, members=[m for m in archive.members if m.name.startswith(name + '/')])
    except (tarfile.ExtractError, OSError) as e:
        raise McmdError("Error restoring {}: {}".format(name, e))
