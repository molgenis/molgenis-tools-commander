import unittest

import pytest

# noinspection PyProtectedMember
from mcmd.args._raising_parser import RaisingArgumentParser
from mcmd.args.actions import ParseKeyValue
from mcmd.args.errors import ArgumentSyntaxError


@pytest.mark.unit
class ActionsTest(unittest.TestCase):
    parser = RaisingArgumentParser(prog='test')
    parser.add_argument('-a',
                        nargs='+',
                        default=dict(),
                        action=ParseKeyValue)

    def test_invalid_key_value_pair(self):
        with pytest.raises(ArgumentSyntaxError) as e:
            self.parser.parse_args(['-a', 'key'])

        assert str(e.value) == "Not a valid key/value pair: key"

    def test_one_pair(self):
        args = self.parser.parse_args(['-a', 'key=value'])
        assert args.a == {'key': 'value'}

    def test_two_pairs(self):
        args = self.parser.parse_args(['-a', 'key=value', 'key2=value2'])
        assert args.a == {'key': 'value', 'key2': 'value2'}

    def test_bool(self):
        args = self.parser.parse_args(['-a', 'key=true', 'key2=false'])
        assert args.a == {'key': True, 'key2': False}
