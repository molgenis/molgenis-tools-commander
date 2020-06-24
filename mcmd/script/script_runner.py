import shlex
import sys
from typing import List

import attr

from mcmd.args import parser as arg_parser
from mcmd.args.errors import ArgumentSyntaxError
from mcmd.core.errors import McmdError, ScriptError
from mcmd.io import io, ask
from mcmd.io.io import bold, dim
from mcmd.io.logging import get_logger
from mcmd.script.model.lines import ScriptLine
from mcmd.script.model.script import Script
from mcmd.script.model.statements import Value, Input, Wait, VisibleComment, Command, InvisibleComment, \
    Empty
from mcmd.script.model.types_ import InputType, ValueType
from mcmd.script.options import ScriptOptions

log = get_logger()


@attr.s(auto_attribs=True)
class _ScriptExecutionState:
    script: Script
    options: ScriptOptions
    values: dict = attr.Factory(dict)


def run(script: Script, options: ScriptOptions):
    """
    Runs a Script by executing it line by line. Keeps track of the script's state in a _ScriptExecutionState.
    """
    state = _ScriptExecutionState(script=script, options=options, values=options.arguments)

    lines = script.get_lines_with_dependencies(from_line_number=options.start_at)
    _validate_required_args(lines, options.arguments)

    _process_lines(lines, state)


def _validate_required_args(lines: List[ScriptLine], args: dict):
    missing_args = list()
    for line in lines:
        statement = line.statement
        if isinstance(statement, Value) and statement.value is None and statement.name not in args:
            missing_args.append(statement.name)

    if len(missing_args) > 0:
        raise McmdError('Missing required argument(s): {}'.format(', '.join(missing_args)))


def _process_lines(lines: List[ScriptLine], state: _ScriptExecutionState):
    for line in lines:
        try:
            _process_line(line, state)
        except (McmdError, ArgumentSyntaxError) as error:
            _handle_error(error, line_number=line.number, state=state)


def _process_line(line: ScriptLine, state: _ScriptExecutionState):
    statement = line.statement

    if isinstance(statement, Value):
        __set_value(statement, state)
    elif isinstance(statement, Input):
        __ask_input(statement, state)
    elif isinstance(statement, Wait):
        _wait(statement, state)
    elif isinstance(statement, VisibleComment):
        _log_comment(statement, state)
    elif isinstance(statement, InvisibleComment):
        pass
    elif isinstance(statement, Empty):
        pass
    elif isinstance(statement, Command):
        _run_command(statement, state)


def _log_comment(comment: VisibleComment, state: _ScriptExecutionState):
    if state.options.log_comments:
        if len(comment.text.string) == 0:
            io.newline()
        else:
            log.info(comment.text.render(state.values))


def __set_value(assignment: Value, state: _ScriptExecutionState):
    if assignment.value is None or assignment.name in state.values:
        return

    if assignment.type == ValueType.TEMPLATE:
        state.values[assignment.name] = assignment.value.render(state.values)
    else:
        state.values[assignment.name] = assignment.value


def __ask_input(input_: Input, state: _ScriptExecutionState):
    if input_.name in state.values:
        return

    message = input_.message.render(state.values) if input_.message else input_.name

    if input_.type == InputType.TEXT:
        value = ask.input_(message, required=True)
    elif input_.type == InputType.BOOL:
        value = ask.confirm(message)
    elif input_.type == InputType.PASS:
        value = ask.password(message, required=True)
    else:
        raise ValueError('Invalid InputType: {}'.format(input_.type))

    state.values[input_.name] = value


def _wait(wait: Wait, state: _ScriptExecutionState):
    text = '{}: {} {}'.format(bold('Waiting for user'),
                              wait.message.render(state.values),
                              dim('(Press enter to continue)'))
    io.start(text)
    io.wait_for_enter()
    io.succeed()


def _handle_error(error: McmdError, line_number: int, state: _ScriptExecutionState):
    if state.options.exit_on_error and not state.options.dry_run:
        raise ScriptError.from_error(error, line_number)
    else:
        sys.stderr.write('Error on line {}: '.format(str(line_number)))
        io.error(error.message)
        if error.info:
            io.info(error.info)


def _run_command(command: Command, state: _ScriptExecutionState):
    cmd = command.command.render(state.values)
    try:
        sub_args = arg_parser.parse_args(shlex.split(cmd))
    except ArgumentSyntaxError as e:
        raise McmdError(message=str(e))

    _block_nested_scripts(sub_args.command)

    if state.options.dry_run:
        log.info(cmd)
    else:
        setattr(sub_args, 'arg_string', cmd)

        sub_args.func(sub_args, nested=True)


def _block_nested_scripts(command: str):
    if command == 'run':
        raise McmdError('Nesting scripts is not supported', info='If you think it should be, feel free to submit a '
                                                                 'feature request at '
                                                                 'https://github.com/molgenis/molgenis-tools'
                                                                 '-commander/issues!')
