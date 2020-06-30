from typing import List, Dict, Set

import attr

from mcmd.script.model.lines import ParsedLine, Line
from mcmd.script.parser.errors import ScriptValidationError


@attr.s(auto_attribs=True)
class _ParseState:
    lines: List[ParsedLine] = attr.Factory(list)
    raw_lines: List[str] = attr.Factory(list)
    combined_lines: List[Line] = attr.Factory(list)
    errors: List[ScriptValidationError] = attr.Factory(list)
    dependencies: Dict[ParsedLine, Set[ParsedLine]] = attr.Factory(dict)
