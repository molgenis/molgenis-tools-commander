import unittest

import pytest

from testfixtures import log_capture, LogCapture

import mcmd.script.script_runner
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
    def test_script_runner(capture):

        parsed_lines = [
            ParsedLine("# add user henk", 1, VisibleComment(
                Template("add user henk"))),
            ParsedLine("// adding user henk", 2, InvisibleComment(
                "adding user henk")),
            #ParsedLine("$value name='henk'", 3,
            #           Value("name", Template("henk"))),
            # ParsedLine("add user {{name}} --is-superuser --is-active",
            #           4, Command(Template('add user {{name}} --is-superuser --is-active'))),
            # ParsedLine("$input text value: 'default value'", 5,
            #           Input("value", InputType.TEXT, Template('default value'))),
            ParsedLine("$wait Wait and relax", 6,
                       Wait(message = Template("Wait and relax"))),
            ParsedLine("", 7, Empty())
        ]

        script = Script(parsed_lines)

        options = ScriptOptions(
            arguments={"-v"}, dry_run=True, start_at=0, exit_on_error=True, log_comments=True)

        mcmd.script.script_runner.run(script, options)

        capture.check(
            ('console', 'INFO', 'add user henk'),
        )
