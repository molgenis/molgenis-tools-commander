"""Module containing the structure and paths of the .mdev folder. Creates folders if they don't exist.

.mdev/
    scripts/
        ...
    datasets/
        ...
    issues/
        <issue1>/
            ...
        <issue2>/
            ...
        ...
    history.log
    mdev.properties
"""

from pathlib import Path

_MDEV_FOLDER = '.mdev'
_SCRIPT_FOLDER = 'scripts'
_DATASET_FOLDER = 'datasets'
_BACKUP_FOLDER = 'backups'
_ISSUE_FOLDER = 'issues'
_PROPERTIES_FILE = 'mdev.properties'
_HISTORY_FILE = 'history.log'


def get_mdev_home():
    mdev_home = Path().home().joinpath(_MDEV_FOLDER)
    return _mkdir_if_not_exists(mdev_home)


def get_scripts_folder():
    scripts_folder = get_mdev_home().joinpath(_SCRIPT_FOLDER)
    return _mkdir_if_not_exists(scripts_folder)


def get_datasets_folder():
    datasets_folder = get_mdev_home().joinpath(_DATASET_FOLDER)
    return _mkdir_if_not_exists(datasets_folder)


def get_backups_folder():
    backups_folder = get_mdev_home().joinpath(_BACKUP_FOLDER)
    return _mkdir_if_not_exists(backups_folder)


def get_issues_folder():
    issues_folder = get_mdev_home().joinpath(_ISSUE_FOLDER)
    return _mkdir_if_not_exists(issues_folder)


def get_history_file():
    return get_mdev_home().joinpath(_HISTORY_FILE)


def get_properties_file():
    return get_mdev_home().joinpath(_PROPERTIES_FILE)


def _mkdir_if_not_exists(path):
    path.mkdir(exist_ok=True)
    return path
