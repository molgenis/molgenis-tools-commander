import tempfile
from pathlib import Path

from tests.integration.loader_mock import get_files_folder

_TEMP_HISTORY = None
_TEMP_ISSUES_FOLDER = None
_TEMP_BACKUP_FOLDER = None


def _raise_exception(msg):
    raise NotImplementedError(msg)


def get_history_file():
    global _TEMP_HISTORY
    if not _TEMP_HISTORY:
        _TEMP_HISTORY = Path(tempfile.mkstemp()[1])
    return _TEMP_HISTORY


def get_issues_folder():
    global _TEMP_ISSUES_FOLDER
    if not _TEMP_ISSUES_FOLDER:
        _TEMP_ISSUES_FOLDER = Path(tempfile.mkdtemp())
    return _TEMP_ISSUES_FOLDER


def get_scripts_folder():
    return get_files_folder().joinpath('scripts')


def get_properties_file():
    _raise_exception(
        "The properties file is not available from within tests")


def get_mcmd_home():
    return _raise_exception("")


def get_backups_folder():
    global _TEMP_BACKUP_FOLDER
    if not _TEMP_BACKUP_FOLDER:
        _TEMP_BACKUP_FOLDER = Path(tempfile.mkdtemp())
    return _TEMP_BACKUP_FOLDER
