import textwrap
from argparse import RawDescriptionHelpFormatter

from mcmd.backend import database, files
from mcmd.backend.database import Database
from mcmd.backend.files import Filestore, MinIO
from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.io import io, ask

# =========
# Arguments
# =========

# Store a reference to the parser so that we can show an error message for the custom validation rule
_parser = None


@arguments('drop')
def arguments(subparsers):
    global _parser
    _parser = subparsers.add_parser('drop',
                                    help='Drop backend resources',
                                    formatter_class=RawDescriptionHelpFormatter,
                                    description=textwrap.dedent(
                                        """
                                        This command drops backend resources. The filestore and MinIO data folders are 
                                        emptied. The database is dropped and a new one gets created.

                                        Requirements:
                                        - Correctly configured 'local' properties (in ~/.mcmd/mcmd.yaml)
                                        - 'psql' must be installed (when dropping the database) 

                                        For safe use, make sure MOLGENIS and the MinIO server are not running.
                                        """)
                                    )
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
                         help='drop everything (same as using -dfm)')
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

    if not args.force and not ask.confirm(
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
    Database.instance().drop()
    Database.instance().create()
    io.succeed()


def _drop_filestore():
    io.start('Dropping filestore')
    Filestore.instance().drop()
    Filestore.instance().create()
    io.succeed()


def _drop_minio():
    io.start('Dropping MinIO')
    MinIO.instance().drop()
    MinIO.instance().create()
    io.succeed()


def _validate_args(args):
    if not (args.database or args.filestore or args.minio or args.all):
        _parser.error('choose at least one thing to drop')
    if args.filestore or args.all:
        files.raise_if_filestore_unconfigured()
    if args.minio or args.all:
        files.raise_if_minio_unconfigured()
    if args.database or args.all:
        database.raise_if_unconfigured()
