"""
A line parser for MCMD scripts. For a full overview of the specs, see the script_spec file in the script package.
"""
from jinja2 import TemplateSyntaxError
from parsy import regex, string, seq, whitespace, from_enum, generate, ParseError

from mcmd.script.model.lines import Line
from mcmd.script.model.statements import Statement, Value, Input, Wait, VisibleComment, Command, \
    InvisibleComment, Empty
from mcmd.script.model.templates import Template
from mcmd.script.model.types_ import InputType
from mcmd.script.parser.errors import ScriptSyntaxError

# subparsers
_double_quoted_string = regex(r'"[^"\\]*(?:\\[\S\s][^"\\]*)*"').map(lambda s: s[1:-1].replace(r'\"', '"'))
_single_quoted_string = regex(r"'[^'\\]*(?:\\[\S\s][^'\\]*)*'").map(lambda s: s[1:-1].replace(r"\'", "'"))
_text = _single_quoted_string.map(Template) | _double_quoted_string.map(Template)
_boolean = string('true').result(True) | string('false').result(False)
_padding = whitespace.optional()
_equals = _padding >> string('=') >> _padding
_bool_assignment = _equals >> _boolean.desc('boolean')
_text_assignment = _equals >> _text.desc('quoted text')
_assignment = _bool_assignment | _text_assignment
_message = _padding >> string(':') >> _padding >> _text
_value_name = regex(r'[a-zA-Z0-9_]+').desc('value name consisting of letters, numbers and/or underscores')
_input_type = from_enum(InputType)
_wait_message = _message | regex('.*').map(lambda s: s.strip()).map(Template)


# $value name [= "text"]
@generate
def _value_declaration():
    yield string('value')
    yield whitespace
    name = yield _value_name
    value = yield _assignment.optional()
    return Value.from_untyped_value(name=name, value=value)


# $input type name [: "message"]
@generate
def _input_declaration():
    yield string('input')
    yield whitespace
    type_ = yield _input_type
    yield whitespace
    name = yield _value_name

    message = yield _message.optional()

    return Input(name=name,
                 type=type_,
                 message=message)


@generate
def _command():
    command_str = yield regex(r'^[^#/\$].*')
    return Command(command=Template(command_str))


# comments (# and //)
@generate
def _visible_comment():
    yield string('#')
    yield _padding
    text = yield regex('.*')
    return VisibleComment(text=Template(text))


_invisible_comment = seq(__start=string('//'),
                         __pad=_padding,
                         comment=regex('.*')).combine_dict(InvisibleComment)

# $wait [: "message"]
# $wait [message]    (backward compatibility)
_wait_declaration = seq(__keyword=string("wait"),
                        message=_wait_message).combine_dict(Wait)

# define declaration parser
_declaration = string('$') >> (_value_declaration | _input_declaration | _wait_declaration)

# define comment parser
_comment = _visible_comment | _invisible_comment

# empty line or line with only whitespace
_empty_line = regex(r'^\s*$').result(Empty())

# top-level parser - the command parser is a fallback parser and will match "everything else"
_statement = _declaration | _comment | _empty_line | _command


def _parse_line(line: str) -> Statement:
    return _statement.parse(line.strip())


def parse(line: Line) -> Statement:
    try:
        return _parse_line(line.string)
    except ParseError as e:
        column = int(str(e).rsplit(':', 1)[-1])
        raise ScriptSyntaxError(str(e), line=line, column=column)
    except TemplateSyntaxError as e:
        raise ScriptSyntaxError(str(e), line=line)
