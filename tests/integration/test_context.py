import tempfile
from pathlib import Path
from typing import List

from mcmd.core.context import Context
from tests.integration.loader_mock import get_files_folder


class TestContext(Context):
    """Test context: uses temporary files and folders for writing, and the project's tests/files/ package for
    resources used in the tests."""

    def __init__(self):
        self._TEMP_HISTORY = None
        self._TEMP_ISSUES_FOLDER = None
        self._TEMP_BACKUP_FOLDER = None

    def _raise_exception(self, msg):
        raise NotImplementedError(msg)

    def get_history_file(self) -> Path:
        if not self._TEMP_HISTORY:
            self._TEMP_HISTORY = Path(tempfile.mkstemp()[1])
        return self._TEMP_HISTORY

    def get_issues_folder(self) -> Path:
        if not self._TEMP_ISSUES_FOLDER:
            self._TEMP_ISSUES_FOLDER = Path(tempfile.mkdtemp())
        return self._TEMP_ISSUES_FOLDER

    def get_scripts_folder(self) -> Path:
        return get_files_folder().joinpath('scripts')

    def get_properties_file(self):
        self._raise_exception("The properties file is not available from within tests")

    def get_backups_folder(self) -> Path:
        if not self._TEMP_BACKUP_FOLDER:
            self._TEMP_BACKUP_FOLDER = Path(tempfile.mkdtemp())
        return self._TEMP_BACKUP_FOLDER

    def get_dataset_folders(self) -> List[Path]:
        return [get_files_folder().joinpath('datasets')]

    def get_resource_folders(self) -> List[Path]:
        return [get_files_folder().joinpath('resources')]
