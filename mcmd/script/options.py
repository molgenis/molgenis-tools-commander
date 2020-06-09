from typing import NamedTuple


class ScriptOptions(NamedTuple):
    arguments: dict
    dry_run: bool
    start_at: int
    log_comments: bool
    exit_on_error: bool
