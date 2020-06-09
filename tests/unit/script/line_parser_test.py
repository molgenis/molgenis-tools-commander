import unittest

import pytest
from parsy import ParseError

# noinspection PyProtectedMember
from mcmd.script.parser.line_parser import _parse_line
from mcmd.script.model.statements import Value, Input, Wait, VisibleComment, Command, InvisibleComment, \
    Empty
from mcmd.script.model.types_ import InputType


@pytest.mark.unit
class LineParserTest(unittest.TestCase):

    @staticmethod
    def test_value_boolean():
        declaration = _parse_line("$value val = true")

        assert isinstance(declaration, Value)
        assert declaration.name == "val"
        assert declaration.value is True

    @staticmethod
    def test_value_boolean_false():
        declaration = _parse_line("$value myValue    =false")

        assert isinstance(declaration, Value)
        assert declaration.name == "myValue"
        assert declaration.value is False

    @staticmethod
    def test_value_text_single_quote():
        declaration = _parse_line(r"  $value my_value= 'text with escaped \'quotes\' in it'")

        assert isinstance(declaration, Value)
        assert declaration.name == "my_value"
        assert declaration.value.string == "text with escaped 'quotes' in it"

    @staticmethod
    def test_value_text_double_quote():
        declaration = _parse_line(r'$value val2="text with escaped \"quotes\" in it"')

        assert isinstance(declaration, Value)
        assert declaration.name == "val2"
        assert declaration.value.string == 'text with escaped "quotes" in it'

    @staticmethod
    def test_value_illegal_bool():
        with pytest.raises(ParseError) as e:
            _parse_line("$value myValue = tru")

        assert str(e.value) == "expected one of 'boolean', 'quoted text' at 0:17"

    @staticmethod
    def test_value_illegal_statement():
        with pytest.raises(ParseError) as e:
            _parse_line("$val myValue")

        assert str(e.value) == "expected one of 'input', 'value', 'wait' at 0:1"

    @staticmethod
    def test_value_illegal_text():
        with pytest.raises(ParseError) as e:
            _parse_line("$value text = '''")

        assert str(e.value) == "expected 'EOF' at 0:16"

    @staticmethod
    def test_value_illegal_assignment():
        with pytest.raises(ParseError) as e:
            _parse_line("$value text ! 'text'")

        assert str(e.value) == "expected '=' at 0:12"

    @staticmethod
    def test_input_text():
        input_ = _parse_line("$input text  input1  ")

        assert isinstance(input_, Input)
        assert input_.name == "input1"
        assert input_.type == InputType.TEXT
        assert input_.message is None

    @staticmethod
    def test_input_bool_with_message():
        input_ = _parse_line("$input bool yesno    :'would you like more'")

        assert isinstance(input_, Input)
        assert input_.name == 'yesno'
        assert input_.type == InputType.BOOL
        assert input_.message.string == 'would you like more'

    @staticmethod
    def test_input_illegal_type():
        with pytest.raises(ParseError) as e:
            _parse_line("$input circle val")

        assert str(e.value) == "expected one of 'bool', 'pass', 'text' at 0:7"

    @staticmethod
    def test_input_illegal_order():
        with pytest.raises(ParseError) as e:
            _parse_line("$input text val : 'message' = 'value'")

        assert str(e.value) == "expected 'EOF' at 0:27"

    @staticmethod
    def test_wait_no_message():
        wait = _parse_line("$wait")

        assert isinstance(wait, Wait)
        assert wait.message.string == ''

    @staticmethod
    def test_wait_message():
        wait = _parse_line(r"$wait :'This is \'the\' message' ")

        assert isinstance(wait, Wait)
        assert wait.message.string == "This is 'the' message"

    @staticmethod
    def test_wait_message_backward_compatible():
        wait = _parse_line(r"$wait This is 'the' message")

        assert isinstance(wait, Wait)
        assert wait.message.string == "This is 'the' message"

    @staticmethod
    def test_comment_visible():
        wait = _parse_line("  # this is a visible comment")

        assert isinstance(wait, VisibleComment)
        assert wait.text.string == "this is a visible comment"

    @staticmethod
    def test_comment_invisible():
        wait = _parse_line(" // this is an invisible comment ")

        assert isinstance(wait, InvisibleComment)
        assert wait.comment == "this is an invisible comment"

    @staticmethod
    def test_empty_line():
        empty = _parse_line("")

        assert isinstance(empty, Empty)

    @staticmethod
    def test_empty_line_whitespace():
        empty = _parse_line("    ")

        assert isinstance(empty, Empty)

    @staticmethod
    def test_command():
        command = _parse_line("mcmd add user {{name}}")

        print(command)
        assert isinstance(command, Command)
        assert command.command.string == "mcmd add user {{name}}"
