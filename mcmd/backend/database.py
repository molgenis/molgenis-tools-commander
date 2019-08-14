import os
import subprocess

from mcmd.config import config
from mcmd.core.errors import McmdError


def dump(file_name):
    try:
        os.environ['PGUSER'] = config.get('local', 'database', 'pg_user')
        os.environ['PGPASSWORD'] = config.get('local', 'database', 'pg_password')
        subprocess.check_output(
            ['pg_dump',
             '-h', 'localhost',
             '-p', '5432',
             config.get('local', 'database', 'name'),
             '-f', file_name],
            stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise McmdError("pg_dump is not a recognized command")
    except subprocess.CalledProcessError as e:
        raise McmdError(e.output.decode('ascii').strip())


def drop():
    os.environ['PGPASSWORD'] = config.get('local', 'database', 'pg_password')
    try:
        subprocess.check_output(['psql',
                                 '-U', config.get('local', 'database', 'pg_user'),
                                 '-h', 'localhost',
                                 '-p', '5432',
                                 '-c', 'DROP DATABASE IF EXISTS {}'.format(config.get('local', 'database', 'name'))],
                                stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise McmdError("psql is not a recognized command")
    except subprocess.CalledProcessError as e:
        raise McmdError(e.output.decode('ascii').strip())


def create():
    os.environ['PGPASSWORD'] = config.get('local', 'database', 'pg_password')
    try:
        subprocess.check_output(['psql',
                                 '-U', config.get('local', 'database', 'pg_user'),
                                 '-h', 'localhost',
                                 '-p', '5432',
                                 '-c', 'CREATE DATABASE {}'.format(config.get('local', 'database', 'name'))],
                                stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise McmdError("psql is not a recognized command")
    except subprocess.CalledProcessError as e:
        raise McmdError(e.output.decode('ascii').strip())


def restore(dump_file):
    os.environ['PGPASSWORD'] = config.get('local', 'database', 'pg_password')
    try:
        subprocess.check_output(['psql',
                                 '-U', config.get('local', 'database', 'pg_user'),
                                 '-h', 'localhost',
                                 '-p', '5432',
                                 'molgenis',
                                 '-f', dump_file],
                                stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise McmdError("psql is not a recognized command")
    except subprocess.CalledProcessError as e:
        raise McmdError(e.output.decode('ascii').strip())
