import unittest

import pytest

# noinspection PyProtectedMember
from mcmd.args._raising_parser import RaisingArgumentParser
from mcmd.args.errors import ArgumentSyntaxError


@pytest.mark.unit
class RaisingParserTest(unittest.TestCase):
    parser = RaisingArgumentParser(prog='test')
    parser.add_argument('-a')

    def test_raises_error(self):
        with pytest.raises(ArgumentSyntaxError) as e:
            self.parser.parse_args(['-a'])

        assert str(e.value) == "test: argument -a: expected one argument"
        assert e.value.usage == "usage: test [-h] [-a A]\n"
