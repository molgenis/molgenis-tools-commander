from mcmd.backend import database, filestore, minio
from mcmd.commands._registry import arguments
from mcmd.config import config
from mcmd.core.command import command
from mcmd.io import io

# =========
# Arguments
# =========

# Store a reference to the parser so that we can show an error message for the custom validation rule
_parser = None


@arguments('drop')
def arguments(subparsers):
    global _parser
    _parser = subparsers.add_parser('drop',
                                    help='drop backend resources')
    _parser.set_defaults(func=drop,
                         write_to_history=True)

    _parser.add_argument('--database', '-d',
                         action='store_true',
                         help='drop the database')
    _parser.add_argument('--filestore', '-f',
                         action='store_true',
                         help='drop the filestore')
    _parser.add_argument('--minio', '-m',
                         action='store_true',
                         help='drop the MinIO data folder')
    _parser.add_argument('--all', '-a',
                         action='store_true',
                         help='drop everything (same as using -dfme)')
    _parser.add_argument('--force', '-F',
                         action='store_true',
                         help='forces the drops without asking for confirmation')

    return _parser


# =======
# Methods
# =======

@command
def drop(args):
    _validate_args(args)

    if not args.force and not io.confirm(
            'Are you sure you want to drop these resources? This will completely remove them'):
        return

    if args.database or args.all:
        _drop_database()
    if args.filestore or args.all:
        _drop_filestore()
    if args.minio or args.all:
        _drop_minio()


def _drop_database():
    io.start('Dropping database')
    database.drop()
    database.create()
    io.succeed()


def _drop_filestore():
    io.start('Dropping filestore')
    filestore.drop()
    filestore.create()
    io.succeed()


def _drop_minio():
    io.start('Dropping minio')
    minio.drop()
    minio.create()
    io.succeed()


def _validate_args(args):
    if not (args.database or args.filestore or args.minio or args.all):
        _parser.error('choose at least one thing to drop')
    if args.filestore or args.all:
        config.raise_if_empty('local', 'molgenis_home')
    if args.minio or args.all:
        config.raise_if_empty('local', 'minio_data')
    if args.database or args.all:
        config.raise_if_empty('local', 'database', 'pg_user')
        config.raise_if_empty('local', 'database', 'pg_password')
        config.raise_if_empty('local', 'database', 'name')
