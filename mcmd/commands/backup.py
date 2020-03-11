import tarfile
import tempfile
import textwrap
from argparse import RawDescriptionHelpFormatter
from pathlib import Path

from mcmd.backend import database, files
from mcmd.backend.database import Database
from mcmd.backend.files import Filestore, MinIO
from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.context import context
from mcmd.core.errors import McmdError
from mcmd.io import io, ask
from mcmd.io.io import highlight
from mcmd.utils.utils import timestamp

# =========
# Arguments
# =========

# Store a reference to the parser so that we can show an error message for the custom validation rule
_parser = None


@arguments('backup')
def arguments(subparsers):
    global _parser
    _parser = subparsers.add_parser('backup',
                                    help='Create a backup of backend resources',
                                    formatter_class=RawDescriptionHelpFormatter,
                                    description=textwrap.dedent(
                                        """
                                        This command creates a backup archive of MOLGENIS backend resoures. Resources 
                                        that can be included are: the database, the filestore and MinIO data.
                                        
                                        The filestore and MinIO data are backed up by copying their folders. 
                                        The database is backed up with 'pg_dump'.
                                        
                                        Requirements:
                                        - Correctly configured 'local' properties (in ~/.mcmd/mcmd.yaml)
                                        - 'pg_dump' must be installed (only when backing up the database)
                                        
                                        For safe use, make sure MOLGENIS and the MinIO server are not running.
                                        """))
    _parser.set_defaults(func=backup,
                         write_to_history=True)

    _parser.add_argument('--database', '-d',
                         action='store_true',
                         help='include a backup of the database (does a PSQL dump)')
    _parser.add_argument('--filestore', '-f',
                         action='store_true',
                         help='include a backup of the filestore')
    _parser.add_argument('--minio', '-m',
                         action='store_true',
                         help='include a backup of the MinIO data folder')
    _parser.add_argument('--all', '-a',
                         action='store_true',
                         help='back up everything (same as using -dfm)')
    _parser.add_argument('--timestamp', '-t',
                         action='store_true',
                         help='add a timestamp to the file name')
    _parser.add_argument('--name', '-n',
                         help='the name of the backup (will be prompted if absent)')
    _parser.add_argument('--to-path', '-p',
                         metavar='PATH',
                         help='store the backup at a custom location (default: ~/.mcmd/backups)')

    return _parser


# =======
# Methods
# =======

@command
def backup(args):
    _validate_args(args)
    file_name = _determine_file_name(args)
    _do_backup(args, file_name)


def _validate_args(args):
    if not (args.database or args.filestore or args.minio or args.all):
        _parser.error('choose at least one thing to back up')
    if args.to_path and not Path(args.to_path).exists():
        raise McmdError("Folder {} doesn't exist".format(args.to_path))
    if args.filestore or args.all:
        if not Filestore.instance().exists():
            raise McmdError("Filestore ({}) doesn't exist".format(Filestore.instance().get_path()))
        files.raise_if_filestore_unconfigured()
    if args.minio or args.all:
        if not MinIO.instance().exists():
            raise McmdError("MinIO data folder ({}) doesn't exist".format(MinIO.instance().get_path()))
        files.raise_if_minio_unconfigured()
    if args.database or args.all:
        database.raise_if_unconfigured()


def _determine_file_name(args):
    location = Path(args.to_path) if args.to_path else context().get_backups_folder()
    backup_name = _create_backup_name(args, location)
    return str(location.joinpath(backup_name)) + '.tar.gz'


def _do_backup(args, file_name):
    try:
        with tarfile.open(file_name, mode='w:gz') as archive:
            if args.database or args.all:
                _backup_database(archive)

            if args.filestore or args.all:
                _backup_filestore(archive)

            if args.minio or args.all:
                _backup_minio(archive)

        io.info('Backup saved at: {}'.format(highlight(file_name)))
    except McmdError as error:
        # Remove the incomplete archive if something went wrong
        Path(file_name).unlink()
        raise error


def _backup_database(archive):
    io.start('Backing up database')
    with tempfile.NamedTemporaryFile() as dump_file:
        try:
            Database.instance().dump(dump_file.name)
            archive.add(dump_file.name, arcname='database/dump.sql')
        except OSError as e:
            raise McmdError("Error writing to backup zip: {}".format(e))
    io.succeed()


def _backup_filestore(archive):
    io.start('Backing up filestore')
    archive.add(Filestore.instance().get_path(), arcname='filestore', recursive=True)
    io.succeed()


def _backup_minio(archive):
    io.start('Backing up MinIO data')
    archive.add(MinIO.instance().get_path(), arcname='minio', recursive=True)
    io.succeed()


def _create_backup_name(args, location):
    if args.name and args.timestamp:
        return args.name + '-' + timestamp()
    elif args.name:
        if location.joinpath(args.name + '.tar.gz').exists():
            raise McmdError('File {} already exists'.format(args.name + '.tar.gz'))
        return args.name
    elif args.timestamp:
        return ask.input_file_name(location, extension='.tar.gz', suffix='-' + timestamp())
    else:
        return ask.input_file_name(location, extension='.tar.gz')
