import unittest
from unittest.mock import patch

import pytest
from testfixtures import log_capture

from mcmd.script import script_runner
from mcmd.script.options import ScriptOptions
from mcmd.script.parser import script_parser


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

        script = script_parser.parse(script_lines)

        options = ScriptOptions(arguments={"arg1": "arg1",
                                           "arg2": "arg2",
                                           "in1": "in1"},
                                dry_run=True,
                                start_at=0,
                                exit_on_error=True,
                                log_comments=True)

        script_runner.run(script, options)

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
    def test_line_dependencies(input_surname, capture):
        input_surname.return_value = 'achternaam'
        script_lines = ["$value name = 'henk'",
                        "$input text surname : 'achternaam'",
                        "",
                        "# don't execute this line",
                        "",
                        "$value fullname = '{{name}} {{surname}}'",
                        "",
                        "# {{fullname}}"
                        ]

        script = script_parser.parse(script_lines)

        options = ScriptOptions(arguments=dict(),
                                dry_run=True,
                                start_at=7,  # start at a later point in the script
                                exit_on_error=True,
                                log_comments=True)

        script_runner.run(script, options)

        capture.check(
            ('console', 'INFO', 'henk achternaam')
        )

    @staticmethod
    @log_capture()
    def test_not_log_comments(capture):
        script_lines = ["# don't log this",
                        "// and this",
                        "add user test"
                        ]

        script = script_parser.parse(script_lines)

        options = ScriptOptions(arguments=dict(),
                                dry_run=True,
                                start_at=1,  # start at a later point in the script
                                exit_on_error=True,
                                log_comments=False)

        script_runner.run(script, options)

        capture.check(
            ('console', 'INFO', 'add user test')
        )
