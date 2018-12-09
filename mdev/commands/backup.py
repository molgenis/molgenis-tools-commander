import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

from mdev import io
from mdev.config.config import config
from mdev.config.home import get_backups_folder
from mdev.io import confirm
from mdev.utils import MdevError


# =========
# Arguments
# =========

def arguments(subparsers):
    p_backup = subparsers.add_parser('backup',
                                     help='Create a backup of the current local MOLGENIS')
    p_backup.set_defaults(func=backup,
                          write_to_history=True)
    return p_backup


# =======
# Methods
# =======

def backup(args):
    file_name = _input_backup_name()

    backup_name = str(get_backups_folder().joinpath(file_name + '.zip'))

    try:
        with zipfile.ZipFile(backup_name, 'w') as backup_zip:
            _backup_database(backup_zip)
            _backup_filestore(backup_zip)
    except MdevError as error:
        Path(backup_name).unlink()
        raise error


# TODO wrap stderr in MdevErrors
def _backup_database(backup_zip):
    io.start('Backing up database')
    with tempfile.NamedTemporaryFile(delete=False) as pg_dump:
        try:
            os.environ['PGUSER'] = config().get('auth', 'pg_user')
            os.environ['PGPASSWORD'] = config().get('auth', 'pg_password')
            subprocess.run(['pg_dump', 'molgenis'], stdout=pg_dump)
            backup_zip.write(pg_dump.name, arcname='dump.sql')
        except FileNotFoundError:
            raise MdevError("pg_dump is not a recognized command.")
        except OSError:
            raise MdevError("Error writing to backup zip")
        finally:
            try:
                pg_dump.close()
                os.unlink(pg_dump.name)
            except OSError as e:
                raise MdevError('Error removing temporary file: %s' % e)
    io.succeed()


def _backup_filestore(backup_zip):
    io.start('Backing up filestore')
    filestore = config().get('data', 'molgenis_home').joinpath('data').joinpath('filestore')
    try:
        for root, dirs, files in os.walk(str(filestore)):
            for file in files:
                backup_zip.write(os.path.join(root, file), arcname='filestore/' + file)
    except OSError as e:
        raise MdevError("Error writing to backup zip: %s" % e)
    io.succeed()


def _input_backup_name():
    file_name = ''
    while not file_name:
        name = io.input_('Please supply the name of this backup:')
        if get_backups_folder().joinpath(name + '.zip').exists():
            overwrite = confirm('%s.zip already exists. Overwrite?' % name)
            if overwrite:
                file_name = name
        else:
            file_name = name

    return file_name
