from typing import List

from mcmd.script.model.lines import ParsedLine
from mcmd.script.model.script import Script
from mcmd.script.parser import dependency_resolver, line_parser, line_combiner
from mcmd.script.parser._parse_state import _ParseState
from mcmd.script.parser.errors import ScriptSyntaxError, InvalidScriptError


def parse(str_lines: List[str]) -> Script:
    """
    Parses a script and returns a Script object containing ParsedLines.
    """

    state = _ParseState()

    # first pass: strip lines
    state.raw_lines = [line.strip() for line in str_lines]

    # second pass: combine multi-line statements
    state.combined_lines = line_combiner.combine_multi_lines(state.raw_lines)

    # third pass: interpret the lines
    _parse_lines(state)

    # fourth pass: resolve dependencies
    dependency_resolver.resolve(state)

    if len(state.errors) > 0:
        raise InvalidScriptError(state.errors)
    else:
        return Script(lines=state.lines, dependencies=state.dependencies)


def _parse_lines(state: _ParseState):
    for line in state.combined_lines:
        try:
            statement = line_parser.parse(line)
        except ScriptSyntaxError as e:
            state.errors.append(e)
        else:
            state.lines.append(ParsedLine(raw=line.string, number=line.number, statement=statement))
