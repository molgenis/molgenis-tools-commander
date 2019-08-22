import os
import subprocess

from mcmd.config import config
from mcmd.core.errors import McmdError
from mcmd.utils.utils import Singleton


def _handle_subprocess(program):
    def handler(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError:
                raise McmdError("{} is not a recognized command".format(program))
            except subprocess.CalledProcessError as e:
                raise McmdError(e.output.decode('ascii').strip())

        return wrapper

    return handler


@Singleton
class Database:
    _CONNECTION_OPTIONS = ('--host', 'localhost',
                           '--port', '5432')

    def __init__(self):
        os.environ['PGUSER'] = config.get('local', 'database', 'pg_user')
        os.environ['PGPASSWORD'] = config.get('local', 'database', 'pg_password')
        self.database_name = config.get('local', 'database', 'name')

    @_handle_subprocess('pg_dump')
    def dump(self, file_name):
        subprocess.check_output(
            ['pg_dump',
             config.get('local', 'database', 'name'),
             '-f', file_name] +
            list(self._CONNECTION_OPTIONS),
            stderr=subprocess.STDOUT)

    @_handle_subprocess('psql')
    def create(self):
        subprocess.check_output(['psql',
                                 '-c', 'CREATE DATABASE {}'.format(self.database_name)] +
                                list(self._CONNECTION_OPTIONS),
                                stderr=subprocess.STDOUT)

    @_handle_subprocess('psql')
    def drop(self):
        subprocess.check_output(['psql',
                                 '-c', 'DROP DATABASE IF EXISTS {}'.format(self.database_name)] +
                                list(self._CONNECTION_OPTIONS),
                                stderr=subprocess.STDOUT)

    @_handle_subprocess('psql')
    def restore(self, dump_file):
        subprocess.check_output(['psql',
                                 self.database_name,
                                 '-f', dump_file] +
                                list(self._CONNECTION_OPTIONS),
                                stderr=subprocess.STDOUT)
