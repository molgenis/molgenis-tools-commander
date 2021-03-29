import attr


@attr.s(frozen=True, auto_attribs=True)
class ScriptOptions:
    arguments: dict = attr.Factory(dict)
    dry_run: bool = False
    start_at: int = 1
    log_comments: bool = True
    exit_on_error: bool = True
