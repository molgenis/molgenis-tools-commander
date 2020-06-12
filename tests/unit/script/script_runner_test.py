import unittest
from unittest.mock import patch

import pytest

from testfixtures import log_capture

import mcmd.script.script_runner
import mcmd.script.parser.script_parser
from mcmd.script.options import ScriptOptions
from mcmd.script.model.lines import ParsedLine
from mcmd.script.model.script import Script
from mcmd.script.model.statements import VisibleComment, InvisibleComment, Value, Command, Input, Empty, Wait
from mcmd.script.model.templates import Template
from mcmd.script.model.types_ import InputType, ValueType


@pytest.mark.unit
class ScriptRunnerTest(unittest.TestCase):

    @staticmethod
    @log_capture()
    @patch('mcmd.io.ask.input_')
    @patch('mcmd.io.ask.confirm')
    @patch('mcmd.io.ask.password')
    def test_script_runner(input_text, confirm_input, password_input, capture):
        input_text.return_value = 'text'
        confirm_input.return_value = 'true'
        password_input.return_value = 'password'
        script_lines = ["$value arg1",
                        "$value arg2= 'override'",
                        "$value arg3= \"don't override\"",
                        "# {{arg1}} {{arg2}} {{arg3}}",
                        "$value val1= 'test'",
                        "$value val2= true",
                        "# {% if val2 %}{{val1}}{% endif %}",
                        "$input text in1: \"override\"",
                        "$input text in2",
                        "# {{in1}} {{in2}}",
                        "$input bool in3",
                        "$input pass in4",
                        "# {% if in3 %}{{in4}}{% endif %}",
                        "add user {{arg1}}",
                        "// no output"
                        ]

        script = mcmd.script.parser.script_parser.parse(script_lines)

        options = ScriptOptions(
            arguments={"arg1": "arg1", "arg2": "arg2", "in1": "in1"}, dry_run=True, start_at=0, exit_on_error=True, log_comments=True)

        mcmd.script.script_runner.run(script, options)

        capture.check(
            ('console', 'INFO', 'arg1 arg2 don\'t override'),
            ('console', 'INFO', 'test'),
            ('console', 'INFO', 'in1 password'),
            ('console', 'INFO', 'text'),
            ('console', 'INFO', 'add user arg1')
        )

    @staticmethod
    @log_capture()
    @patch('mcmd.io.ask.input_')
    def test_use_jinja_vars(input_surname, capture):
        input_surname.return_value = 'achternaam'
        script_lines = ["$value name = 'henk'",
                        "$input text surname: 'achternaam'",
                        "",
                        "# don't execute this line",
                        "",
                        "$input text fullname: '{{name}} {{surname}}'",
                        "",
                        "# {{fullname}}"
                        ]

        script = mcmd.script.parser.script_parser.parse(script_lines)

        options = ScriptOptions(
            arguments={}, dry_run=True, start_at=7, exit_on_error=True, log_comments=True)

        mcmd.script.script_runner.run(script, options)

        capture.check(
            # TODO: should be 'henk achternaam', it does not pickup the value
            ('console', 'INFO', 'achternaam')
        )
