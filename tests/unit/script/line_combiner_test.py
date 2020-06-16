import unittest

import pytest

import mcmd.script.parser.line_combiner
from mcmd.script.model.lines import Line


@pytest.mark.unit
class LineCombinerTest(unittest.TestCase):

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
            ": 'default value'",
            "# last line \\"
        ]

        expected_lines = [
            Line(number=1, string='# add user henk'), 
            Line(number=2, string="$value name='henk'"), 
            Line(number=3, string=''), 
            Line(number=4, string='# multi-lined command'), 
            Line(number=5, string='add user {{name}} --is-superuser --is-active'), 
            Line(number=8, string=''), 
            Line(number=9, string='# multi-lined input statement'), 
            Line(number=10, string="$input text value : 'default value'"), 
            Line(number=12, string='# last line')
            ]

        lines = mcmd.script.parser.line_combiner.combine_multi_lines(
            script_lines)

        assert lines == expected_lines
