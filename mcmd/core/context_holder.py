"""Module containing the structure and paths of the .mcmd folder. Creates folders if they don't exist.

.mcmd/
    scripts/
        ...
    issues/
        <issue1>/
            ...
        <issue2>/
            ...
        ...
    history.log
    mcmd.yaml
"""
from abc import ABC, abstractmethod
from pathlib import Path


class Context(ABC):
    @abstractmethod
    def get_mcmd_home(self) -> Path:
        pass

    @abstractmethod
    def get_scripts_folder(self) -> Path:
        pass

    @abstractmethod
    def get_backups_folder(self) -> Path:
        pass

    @abstractmethod
    def get_issues_folder(self) -> Path:
        pass

    @abstractmethod
    def get_history_file(self) -> Path:
        pass

    @abstractmethod
    def get_properties_file(self) -> Path:
        pass


_context = None


def set_context(new_context: Context):
    global _context
    _context = new_context


def get_context():
    return _context


class HomeContext(Context):
    """Default context: stores locations to files/folders in ~/.mcmd"""

    _MCMD_FOLDER = '.mcmd'
    _SCRIPT_FOLDER = 'scripts'
    _BACKUP_FOLDER = 'backups'
    _ISSUE_FOLDER = 'issues'
    _PROPERTIES_FILE = 'mcmd.yaml'
    _HISTORY_FILE = 'history.log'

    def get_mcmd_home(self) -> Path:
        mcmd_home = Path().home().joinpath(self._MCMD_FOLDER)
        return self._mkdir_if_not_exists(mcmd_home)

    def get_scripts_folder(self) -> Path:
        scripts_folder = self.get_mcmd_home().joinpath(self._SCRIPT_FOLDER)
        return self._mkdir_if_not_exists(scripts_folder)

    def get_backups_folder(self) -> Path:
        backups_folder = self.get_mcmd_home().joinpath(self._BACKUP_FOLDER)
        return self._mkdir_if_not_exists(backups_folder)

    def get_issues_folder(self) -> Path:
        issues_folder = self.get_mcmd_home().joinpath(self._ISSUE_FOLDER)
        return self._mkdir_if_not_exists(issues_folder)

    def get_history_file(self) -> Path:
        return self.get_mcmd_home().joinpath(self._HISTORY_FILE)

    def get_properties_file(self) -> Path:
        return self.get_mcmd_home().joinpath(self._PROPERTIES_FILE)

    @staticmethod
    def _mkdir_if_not_exists(path) -> Path:
        path.mkdir(exist_ok=True)
        return path
