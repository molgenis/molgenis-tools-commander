import unittest

import pytest

import mcmd.script.parser.line_combiner
from mcmd.script.model.lines import Line


@pytest.mark.unit
class ScriptParserTest(unittest.TestCase):

    @staticmethod
    def test_combine_multi_lines():
        script_lines = [
            "# add user henk",
            "$value name='henk'",
            "",
            "# multi-lined command",
            "add user {{name}} \\",
            "--is-superuser \\",
            "--is-active",
            "",
            "# multi-lined input statement",
            "$input text value\t\\",
            "= 'default value'",
            "# last line \\"
        ]

        expected_lines = [
            Line(1, "# add user henk"),
            Line(2, "$value name='henk'"),
            Line(3, ""),
            Line(4, "# multi-lined command"),
            Line(5, "add user {{name}} --is-superuser --is-active"),
            Line(8, ""),
            Line(9, "# multi-lined input statement"),
            Line(10, "$input text value = 'default value'"),
            Line(12, "# last line")

        ]

        lines = mcmd.script.parser.line_combiner.combine_multi_lines(script_lines)

        assert lines == expected_lines
