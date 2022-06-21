from pathlib import Path
from typing import List

from mcmd.__main__ import start_detached
from mcmd.config import config
from mcmd.core.context import Context

from mcmd.core.errors import ApiError


class EmptyContext(Context):
    def get_scripts_folder(self) -> Path:
        self._raise()

    def get_backups_folder(self) -> Path:
        self._raise()

    def get_issues_folder(self) -> Path:
        self._raise()

    def get_history_file(self) -> Path:
        return None

    def get_dataset_folders(self) -> List[Path]:
        self._raise()

    def get_resource_folders(self) -> List[Path]:
        self._raise()

    def get_git_folders(self) -> List[Path]:
        self._raise()

    def get_properties_file(self) -> Path:
        self._raise()

    def get_storage_file(self) -> Path:
        self._raise()

    def _raise(self):
        raise ApiError("Can't access context paths using the API.")


class Commander:

    # TODO pass token, or better: a molgenis.client.Session
    def __init__(self):
        config.set_config(
            {
                "host":
                    {
                        "selected": "http://localhost",
                        "auth": [
                            {
                                "url": "http://localhost",
                                "username": "xxx",
                                "password": "xxx",
                                "token": "xxx"
                            }
                        ]
                    },
                "settings":
                    {
                        "import_action": "add_update_existing",
                        "non_interactive":  True
                    }
            },
            None)
        pass

    @staticmethod
    def execute(arg_string):
        exit_code = start_detached(['mcmd'] + arg_string.split(' '), EmptyContext())
        assert exit_code == 0


commander = Commander()
commander.execute("import --from-path it_emx_autoid")
