import os
import subprocess

from mcmd.config import config
from mcmd.core.errors import McmdError

_connection_options = ['--host', 'localhost',
                       '--port', '5432']


def dump(file_name):
    try:
        _set_env_var_user()
        _set_env_var_password()
        subprocess.check_output(
            ['pg_dump',
             config.get('local', 'database', 'name'),
             '-f', file_name] +
            _connection_options,
            stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise McmdError("pg_dump is not a recognized command")
    except subprocess.CalledProcessError as e:
        raise McmdError(e.output.decode('ascii').strip())


def drop():
    try:
        _set_env_var_password()
        subprocess.check_output(['psql',
                                 '-U', config.get('local', 'database', 'pg_user'),
                                 '-c', 'DROP DATABASE IF EXISTS {}'.format(config.get('local', 'database', 'name'))] +
                                _connection_options,
                                stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise McmdError("psql is not a recognized command")
    except subprocess.CalledProcessError as e:
        raise McmdError(e.output.decode('ascii').strip())


def create():
    try:
        _set_env_var_password()
        subprocess.check_output(['psql',
                                 '-U', config.get('local', 'database', 'pg_user'),
                                 '-c', 'CREATE DATABASE {}'.format(config.get('local', 'database', 'name'))] +
                                _connection_options,
                                stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise McmdError("psql is not a recognized command")
    except subprocess.CalledProcessError as e:
        raise McmdError(e.output.decode('ascii').strip())


def restore(dump_file):
    try:
        _set_env_var_password()
        subprocess.check_output(['psql',
                                 '-U', config.get('local', 'database', 'pg_user'),
                                 config.get('local', 'database', 'name'),
                                 '-f', dump_file] +
                                _connection_options,
                                stderr=subprocess.STDOUT)
    except FileNotFoundError:
        raise McmdError("psql is not a recognized command")
    except subprocess.CalledProcessError as e:
        raise McmdError(e.output.decode('ascii').strip())


def _set_env_var_user():
    os.environ['PGUSER'] = config.get('local', 'database', 'pg_user')


def _set_env_var_password():
    os.environ['PGPASSWORD'] = config.get('local', 'database', 'pg_password')
