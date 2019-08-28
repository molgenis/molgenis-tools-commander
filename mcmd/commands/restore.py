import shutil
import tarfile
import textwrap
from argparse import RawDescriptionHelpFormatter
from distutils.errors import DistutilsFileError
from pathlib import Path
from tempfile import TemporaryDirectory

from mcmd.backend.database import Database
from mcmd.backend.files import Filestore, MinIO
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
    _parser = subparsers.add_parser('restore',
                                    help='Restore a backup',
                                    formatter_class=RawDescriptionHelpFormatter,
                                    description=textwrap.dedent(
                                        """
                                        This command restores a previously made backup. 
                                        
                                        Requirements:
                                        - Correctly configured 'local' properties (in ~/.mcmd/mcmd.yaml)
                                        - 'psql' must be installed (when restoring a backup of a database)
                                        - The database, filestore and MinIO should be empty before restoring (use the
                                          'drop' command if they aren't) 
                                        
                                        For safe use, make sure MOLGENIS and the MinIO server are not running.
                                        """)
                                    )

    _parser.set_defaults(func=restore,
                         write_to_history=True)
    _parser.add_argument('name',
                         help='the backup to restore (or path to the backup when using --from-path)')
    _parser.add_argument('--from-path', '-p',
                         action='store_true',
                         help='get a backup from a path instead of the MCMD backup folder')

    return _parser


# =======
# Methods
# =======

@command
def restore(args):
    backup = _get_backup(args)
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
    restore_database = False
    restore_filestore = False
    restore_minio = False
    with tarfile.open(backup) as archive:
        if _archive_has_member(archive, 'database/dump.sql'):
            _validate_restore_database()
            restore_database = True

        if _archive_has_member(archive, 'filestore'):
            _validate_restore_filestore()
            restore_filestore = True

        if _archive_has_member(archive, 'minio'):
            _validate_restore_minio()
            restore_minio = True

        if restore_database:
            _restore_database(archive)
        if restore_filestore:
            _restore_filestore(archive)
        if restore_minio:
            _restore_minio(archive)


def _validate_restore_database():
    config.raise_if_empty('local', 'database', 'pg_user')
    config.raise_if_empty('local', 'database', 'pg_password')
    config.raise_if_empty('local', 'database', 'name')


def _validate_restore_filestore():
    config.raise_if_empty('local', 'molgenis_home')
    if not Filestore.instance().is_empty():
        raise McmdError(
            'The filestore ({}) is not empty - drop it before restoring'.format(Filestore.instance().get_path()))


def _validate_restore_minio():
    config.raise_if_empty('local', 'minio_data')
    if not MinIO.instance().is_empty():
        raise McmdError(
            'The MinIO data folder ({}) is not empty - drop it before restoring'.format(MinIO.instance().get_path()))


def _archive_has_member(archive, member):
    try:
        archive.getmember(member)
    except KeyError:
        return False
    else:
        return True


def _restore_database(archive):
    io.start('Restoring database')

    with TemporaryDirectory() as tempdir:
        archive.extractall(path=tempdir, members=[archive.getmember('database/dump.sql')])
        dumpfile = tempdir + '/database/dump.sql'

        Database.instance().restore(dumpfile)

    io.succeed()


def _restore_filestore(archive):
    io.start('Restoring filestore')
    _extract_files(archive, Filestore.instance().get_path().parent, "filestore")
    io.succeed()


def _restore_minio(archive):
    io.start('Restoring MinIO data')
    # the minio folder can have any name so we need to extract the folder to a temporary location first
    with TemporaryDirectory() as tempdir:
        _extract_files(archive, tempdir, "minio")
        minio = MinIO.instance()
        minio.drop()
        _copy_minio_files(tempdir + '/minio', minio.get_path())
    io.succeed()


def _copy_minio_files(backup_location, location):
    try:
        shutil.copytree(str(backup_location), str(location))
    except (DistutilsFileError, OSError) as e:
        raise McmdError("Error restoring MinIO data: {}".format(e))


def _extract_files(archive, location, name):
    try:
        archive.extractall(path=location, members=[m for m in archive.members if m.name.startswith(name + '/')])
    except (tarfile.ExtractError, OSError) as e:
        raise McmdError("Error restoring {}: {}".format(name, e))
