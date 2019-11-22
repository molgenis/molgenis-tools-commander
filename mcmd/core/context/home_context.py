from pathlib import Path
from typing import List

from mcmd.config import config
from mcmd.core.context import Context


class HomeContext(Context):
    """Default context: stores locations to files/folders in the usere's home directory: ~/.mcmd"""

    _MCMD_FOLDER = '.mcmd'
    _SCRIPT_FOLDER = 'scripts'
    _BACKUP_FOLDER = 'backups'
    _ISSUE_FOLDER = 'issues'
    _PROPERTIES_FILE = 'mcmd.yaml'
    _HISTORY_FILE = 'history.log'

    def _get_mcmd_home(self) -> Path:
        mcmd_home = Path().home().joinpath(self._MCMD_FOLDER)
        return self._mkdir_if_not_exists(mcmd_home)

    def get_scripts_folder(self) -> Path:
        scripts_folder = self._get_mcmd_home().joinpath(self._SCRIPT_FOLDER)
        return self._mkdir_if_not_exists(scripts_folder)

    def get_backups_folder(self) -> Path:
        backups_folder = self._get_mcmd_home().joinpath(self._BACKUP_FOLDER)
        return self._mkdir_if_not_exists(backups_folder)

    def get_issues_folder(self) -> Path:
        issues_folder = self._get_mcmd_home().joinpath(self._ISSUE_FOLDER)
        return self._mkdir_if_not_exists(issues_folder)

    def get_history_file(self) -> Path:
        return self._get_mcmd_home().joinpath(self._HISTORY_FILE)

    def get_dataset_folders(self) -> List[Path]:
        return [Path(folder) for folder in config.get('resources', 'dataset_folders')]

    def get_resource_folders(self) -> List[Path]:
        return [Path(folder) for folder in config.get('resources', 'resource_folders')]

    def get_git_folders(self) -> List[Path]:
        return config.git_paths()

    def get_properties_file(self) -> Path:
        return self._get_mcmd_home().joinpath(self._PROPERTIES_FILE)

    @staticmethod
    def _mkdir_if_not_exists(path) -> Path:
        path.mkdir(exist_ok=True)
        return path
