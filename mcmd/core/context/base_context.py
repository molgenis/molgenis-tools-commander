from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class Context(ABC):
    """
    Abstract context class that provides the interface of a Context.

    A context defines all the different locations where content can be requested during the execution of MOLGENIS
    Commander.

    Also functions as a context manager so an instance of this class can be set as the current context using the 'with'
    syntax:

    >>> context = Context() # an implementation of a context
    >>> with context:
    >>>     # do something
    """

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
    def get_git_folders(self) -> List[Path]:
        pass

    @abstractmethod
    def get_properties_file(self) -> Path:
        pass

    @abstractmethod
    def get_storage_file(self) -> Path:
        pass

    def __enter__(self):
        """Replace the previous context (if any) with this context."""
        self.previous_context = context_holder.get_context()
        context_holder.set_context(self)

    def __exit__(self, type_, value, traceback):
        """When exiting this context, replace the previous one (if any)."""
        context_holder.set_context(self.previous_context)


# delay import of _context_holder to prevent circular import errors
import mcmd.core.context._context_holder as context_holder
