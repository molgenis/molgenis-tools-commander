import tempfile
from pathlib import Path

_TEMP_FILE = None


def _raise_exception(msg):
    raise NotImplementedError(msg)


def get_history_file():
    global _TEMP_FILE
    if not _TEMP_FILE:
        _TEMP_FILE = Path(tempfile.mkstemp()[1])
    return _TEMP_FILE


def get_issues_folder():
    return _raise_exception("")


def get_scripts_folder():
    return _raise_exception("")


def get_properties_file():
    _raise_exception(
        "The properties file is not available from within tests")


def get_mcmd_home():
    return _raise_exception("")


def get_datasets_folder():
    return _raise_exception("")


def get_backups_folder():
    return _raise_exception("")
