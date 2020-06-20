import unittest

import pytest

from mcmd.script.model.lines import ScriptLine, Line
from mcmd.script.model.statements import VisibleComment, InvisibleComment, Value, Command, Input, Empty, Wait
from mcmd.script.model.templates import Template
from mcmd.script.model.types_ import InputType
from mcmd.script.parser import script_parser
# noinspection PyProtectedMember
from mcmd.script.parser._parse_state import _ParseState
from mcmd.script.parser.errors import InvalidScriptError


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
            ScriptLine("# add user henk", 1, VisibleComment(Template("add user henk"))),
            ScriptLine("// adding user henk", 2, InvisibleComment("adding user henk")),
            ScriptLine("$value name='henk'", 3, Value.from_untyped_value("name", Template("henk"))),
            ScriptLine("add user {{name}} --is-superuser --is-active", 4,
                       Command(Template('add user {{name}} --is-superuser --is-active'))),
            ScriptLine("$input text value: 'default value'", 5,
                       Input("value", InputType.TEXT, Template('default value'))),
            ScriptLine("$wait Wait and relax", 6, Wait(Template("Wait and relax"))),
            ScriptLine("", 7, Empty())
        ]

        script_parser._parse_lines(state)

        assert state.lines == expected_lines

    def test_error_handling(self):
        script_lines = ["$input bool test =",
                        "$input text test2 = true",
                        "",
                        "# {{name}}",
                        "",
                        "$input text name = '{{name}}'",
                        "$value name",
                        "",
                        "# {{blaat}}",
                        "",
                        "$valu x = 'hoi'",
                        "",
                        "$input enum type : 'input something!'",
                        "",
                        "# {{x}}",
                        "",
                        "# {{name}",
                        "",
                        "$input bool question = 'string'"
                        ]

        with self.assertRaises(InvalidScriptError) as context:
            script_parser.parse(script_lines)

        for num, exception in enumerate(context.exception.errors, start=1):
            if num == 0:
                assert str(
                    exception.message) == "Line 2: $input text test2 = true\n" \
                                          "                          ^\n" \
                                          "  - Expected ':' at 0:18"
            if num == 1:
                assert str(
                    exception.message) == "Line 1: $input bool test =\n" \
                                          "                         ^\n" \
                                          "  - Expected ':' at 0:17"
            if num == 2:
                assert str(
                    exception.message) == "Line 2: $input text test2 = true\n" \
                                          "                          ^\n" \
                                          "  - Expected ':' at 0:18"
            if num == 3:
                assert str(
                    exception.message) == "Line 6: $input text name = '{{name}}'\n" \
                                          "                         ^\n" \
                                          "  - Expected ':' at 0:17"
            if num == 4:
                assert str(
                    exception.message) == "Line 11: $valu x = 'hoi'\n" \
                                          "          ^\n" \
                                          "  - Expected one of 'input', 'value', 'wait' at 0:1"
            if num == 5:
                assert str(
                    exception.message) == "Line 13: $input enum type : 'input something!'\n" \
                                          "                ^\n" \
                                          "  - Expected one of 'bool', 'pass', 'text' at 0:7"
            if num == 6:
                assert str(
                    exception.message) == "Line 17: # {{name}\n" \
                                          "  - Unexpected '}'"
            if num == 7:
                assert str(
                    exception.message) == "Line 19: $input bool question = 'string'\n" \
                                          "                              ^\n" \
                                          "  - Expected ':' at 0:21"
            if num == 8:
                assert str(
                    exception.message) == "Line 4: # {{name}}\n" \
                                          "  - Value 'name' referenced before assignment: 'name' is assigned at line 7"
            if num == 9:
                assert str(
                    exception.message) == "Line 9: # {{blaat}}\n" \
                                          "  - Unknown value 'blaat'"
