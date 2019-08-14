import os
import tarfile
import tempfile
import textwrap
from datetime import datetime
from pathlib import Path

from mcmd.backend import database
from mcmd.commands._registry import arguments
from mcmd.config import config
from mcmd.core.command import command
from mcmd.core.errors import McmdError
from mcmd.core.home import get_backups_folder
from mcmd.io import io
from mcmd.io.io import highlight

# =========
# Arguments
# =========

# Store a reference to the parser so that we can show an error message for the custom validation rule
_parser = None


@arguments('backup')
def arguments(subparsers):
    global _parser
    _parser = subparsers.add_parser('backup',
                                    help='create a backup of a locally installed MOLGENIS')
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
        config.raise_if_empty('local', 'molgenis_home')
    if args.minio or args.all:
        config.raise_if_empty('local', 'minio_data')
    if args.database or args.all:
        config.raise_if_empty('local', 'database', 'pg_user')
        config.raise_if_empty('local', 'database', 'pg_password')
        config.raise_if_empty('local', 'database', 'name')


def _determine_file_name(args):
    location = Path(args.to_path) if args.to_path else get_backups_folder()
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
    except McmdError as error:
        Path(file_name).unlink()
        raise error
    io.info('Backup saved at: {}'.format(highlight(file_name)))


def _backup_database(archive):
    io.start('Backing up database')
    with tempfile.NamedTemporaryFile(delete=False) as dump_file:
        try:
            database.dump(dump_file.name)
            archive.add(dump_file.name, arcname='database/dump.sql')
        except OSError as e:
            raise McmdError("Error writing to backup zip: {}".format(e))
        finally:
            try:
                dump_file.close()
                os.unlink(dump_file.name)
            except OSError as e:
                raise McmdError('Error removing temporary file: {}'.format(e))
    io.succeed()


def _backup_filestore(archive):
    io.start('Backing up filestore')
    filestore = Path(config.get('local', 'molgenis_home')).joinpath('data').joinpath('filestore')
    archive.add(filestore, arcname='filestore', recursive=True)
    io.succeed()


def _backup_minio(archive):
    io.start('Backing up MinIO data')
    archive.add(config.get('local', 'minio_data'), arcname='minio', recursive=True)
    io.succeed()


def _create_backup_name(args, location):
    if args.name and args.timestamp:
        return args.name + _timestamp()
    elif args.name:
        if location.joinpath(args.name + '.tar.gz').exists():
            raise McmdError('File {} already exists'.format(args.name + '.tar.gz'))
        return args.name
    else:
        return _input_backup_name(args, location)


def _timestamp() -> str:
    return datetime.now().strftime('-%Y%m%dT%H%M%S')


def _input_backup_name(args, location):
    file_name = ''
    while not file_name:
        name = io.input_('Please supply the name of this backup:')
        if args.timestamp:
            name += _timestamp()

        if location.joinpath(name + '.tar.gz').exists():
            overwrite = io.confirm('{} already exists. Overwrite?'.format(location.joinpath(name + '.tar.gz')))
            if overwrite:
                file_name = name
        else:
            file_name = name

    return file_name
