from typing import List, Dict, Set

import attr

from mcmd.script.model.lines import ScriptLine, Line
from mcmd.script.parser.errors import ScriptValidationError


@attr.s
class _ParseState:
    lines: List[ScriptLine] = attr.ib(default=attr.Factory(list))
    raw_lines: List[str] = attr.ib(default=attr.Factory(list))
    combined_lines: List[Line] = attr.ib(default=attr.Factory(list))
    errors: List[ScriptValidationError] = attr.ib(default=attr.Factory(list))
    dependencies: Dict[ScriptLine, Set[ScriptLine]] = attr.ib(default=attr.Factory(dict))
