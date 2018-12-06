# =========
# Arguments
# =========
import subprocess
import tempfile
from pathlib import Path

from mdev import io
from mdev.config.home import get_backups_folder
from mdev.io import confirm


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
    # prompt for backup name
    file_name = _input_backup_name()

    with tempfile.TemporaryDirectory() as tempdir:
        pg_dump_handle = Path(tempdir).joinpath('dump.sql').open('w')
        subprocess.run(['pg_dump', '--username', 'postgres'], stdout=pg_dump_handle)


    # check not exists
    # create temp dir
    # dump postgresql to temp dir
    # dump elasticsearch to temp dir
    # copy filestore to temp dir
    # zip contents of temp dir
    # move zip to /backups folder
    # always remove temp dir

    pass


def _input_backup_name():
    file_name = ''
    while not file_name:
        name = io.input_('Supply the name of your backup:')
        if get_backups_folder().joinpath(name + '.zip').exists():
            overwrite = confirm('%s.zip already exists. Overwrite?' % name)
            if overwrite:
                file_name = name
        else:
            file_name = name

    return file_name
