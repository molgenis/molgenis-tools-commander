from mcmd.script.model.lines import ScriptLine
from mcmd.script.model.statements import Templatable, Assignment
from mcmd.script.parser._parse_state import _ParseState
from mcmd.script.parser.errors import ReassignmentError, ForwardReferenceError, UnknownReferenceError, \
    RecursiveReferenceError


def resolve(state: _ParseState):
    """
    Resolves the dependencies of each ParsedLine and adds them to that ParsedLine. Attaches any errors encountered
    along the way to the parse state.
    """

    declarations_by_name = dict()
    for line in state.lines:
        statement = line.statement
        if isinstance(statement, Assignment):
            if statement.name in declarations_by_name:
                state.errors.append(ReassignmentError(statement.name, line, declarations_by_name[statement.name]))
            else:
                declarations_by_name[statement.name] = line

    for line in state.lines:
        statement = line.statement
        if isinstance(statement, Templatable):
            _set_dependencies(declarations_by_name, line, statement.variables, state)


def _set_dependencies(declarations_by_name: dict, line: ScriptLine, variables: frozenset, state: _ParseState):
    for var in variables:
        if var not in declarations_by_name:
            state.errors.append(UnknownReferenceError(line, var))
        else:
            dependency = declarations_by_name[var]

            if dependency.number == line.number:
                state.errors.append(RecursiveReferenceError(line, var))
            elif dependency.number >= line.number:
                state.errors.append(ForwardReferenceError(var, line, dependency))
            else:
                if line not in state.dependencies:
                    state.dependencies[line] = {declarations_by_name[var]}
                else:
                    state.dependencies[line].add(declarations_by_name[var])
