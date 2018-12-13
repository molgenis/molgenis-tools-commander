"""Module containing the structure and paths of the .mcmd folder. Creates folders if they don't exist.

.mcmd/
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
    mcmd.properties
"""

from pathlib import Path

_MCMD_FOLDER = '.mcmd'
_SCRIPT_FOLDER = 'scripts'
_DATASET_FOLDER = 'datasets'
_BACKUP_FOLDER = 'backups'
_ISSUE_FOLDER = 'issues'
_PROPERTIES_FILE = 'mcmd.properties'
_HISTORY_FILE = 'history.log'


def get_mcmd_home():
    mcmd_home = Path().home().joinpath(_MCMD_FOLDER)
    return _mkdir_if_not_exists(mcmd_home)


def get_scripts_folder():
    scripts_folder = get_mcmd_home().joinpath(_SCRIPT_FOLDER)
    return _mkdir_if_not_exists(scripts_folder)


def get_datasets_folder():
    datasets_folder = get_mcmd_home().joinpath(_DATASET_FOLDER)
    return _mkdir_if_not_exists(datasets_folder)


def get_backups_folder():
    backups_folder = get_mcmd_home().joinpath(_BACKUP_FOLDER)
    return _mkdir_if_not_exists(backups_folder)


def get_issues_folder():
    issues_folder = get_mcmd_home().joinpath(_ISSUE_FOLDER)
    return _mkdir_if_not_exists(issues_folder)


def get_history_file():
    return get_mcmd_home().joinpath(_HISTORY_FILE)


def get_properties_file():
    return get_mcmd_home().joinpath(_PROPERTIES_FILE)


def _mkdir_if_not_exists(path):
    path.mkdir(exist_ok=True)
    return path
