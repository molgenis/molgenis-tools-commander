import os
import shutil
from abc import ABC
from pathlib import Path

from mcmd.config import config
from mcmd.core.errors import McmdError
from mcmd.utils.utils import Singleton


class AbstractFilesFolder(ABC):
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        super().__init__()

    def get_path(self):
        return self.path

    def exists(self):
        try:
            return self.path.exists()
        except OSError as e:
            raise McmdError('Error reading {}: {}'.format(self.name, e))

    def is_empty(self):
        try:
            if not self.path.exists() or len(os.listdir(str(self.path))) == 0:
                return True
            else:
                return False
        except OSError as e:
            raise McmdError('Error reading {}: {}'.format(self.name, e))

    def drop(self):
        try:
            if self.path.exists():
                shutil.rmtree(self.path)
        except Exception as e:
            raise McmdError('Error dropping {}: {}'.format(self.name, e))

    def create(self):
        try:
            self.path.mkdir()
        except OSError as e:
            raise McmdError('Error creating {}: {}'.format(self.name, e))


@Singleton
class Filestore(AbstractFilesFolder):
    def __init__(self):
        super().__init__('filestore',
                         Path(config.get('local', 'molgenis_home')).joinpath('data').joinpath('filestore'))


@Singleton
class MinIO(AbstractFilesFolder):
    def __init__(self):
        super().__init__('MinIO data folder',
                         Path(config.get('local', 'minio_data')))


def raise_if_filestore_unconfigured():
    config.raise_if_empty('local', 'molgenis_home')


def raise_if_minio_unconfigured():
    config.raise_if_empty('local', 'minio_data')
