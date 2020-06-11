import unittest

import pytest

import mcmd.script.parser.script_parser

from mcmd.script.parser import script_parser
from mcmd.script.parser._parse_state import _ParseState
from mcmd.script.model.lines import ParsedLine, Line
from mcmd.script.model.statements import VisibleComment, InvisibleComment, Value, Command, Input, Empty, Wait
from mcmd.script.model.templates import Template
from mcmd.script.model.types_ import InputType, ValueType


@pytest.mark.unit
class ScriptParserTest(unittest.TestCase):

    @staticmethod
    def test_parse_lines():
        state = _ParseState()

        state.combined_lines = [
            Line(1, "# add user henk"),
            Line(2, "// adding user henk"),
            Line(3, "$value name='henk'"),
            Line(4, "add user {{name}} --is-superuser --is-active"),
            Line(5, "$input text value: 'default value'"),
            Line(6, "$wait Wait and relax"),
            Line(7, "")
        ]

        expected_lines = [
            ParsedLine("# add user henk", 1, VisibleComment(Template("add user henk"))),
            ParsedLine("// adding user henk", 2, InvisibleComment(
                "adding user henk")),
            ParsedLine("$value name='henk'", 3,
                       Value("name", Template("henk"))),
            ParsedLine("add user {{name}} --is-superuser --is-active",
                       4, Command(Template('add user {{name}} --is-superuser --is-active'))),
            ParsedLine("$input text value: 'default value'", 5,
                       Input("value", InputType.TEXT, Template('default value'))),
            ParsedLine("$wait Wait and relax", 6,
                       Wait(Template("Wait and relax"))),
            ParsedLine("", 7, Empty())
        ]

        mcmd.script.parser.script_parser._parse_lines(state)

        assert state.lines == expected_lines
