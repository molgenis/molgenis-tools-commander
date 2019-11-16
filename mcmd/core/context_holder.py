from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


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
    def get_dataset_folders(self) -> List[Path]:
        pass

    @abstractmethod
    def get_resource_folders(self) -> List[Path]:
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
