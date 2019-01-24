import sys

import pytest

from mcmd.__main__ import main


# @pytest.fixture
# def run():
#     def do_run(*args):
#         sys.argv = ["mcmd"] + list(args)
#         return main()
#
#     return do_run

@pytest.mark.system
class Test:
    def test_it(self):
        sys.argv = ["mcmd", "give", "henk", "write", "it_emx"]
        result = main()
        assert result == 0

    def test_it2(self):
        sys.argv = ["mcmd", "give", "henk", "write", "it_emx"]
        result = main()
        assert result == 0
