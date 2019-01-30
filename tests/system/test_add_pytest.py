import pytest

# noinspection PyUnresolvedReferences
import tests.system.fake_home
# noinspection PyUnresolvedReferences
import tests.system.fake_loader
from mcmd.__main__ import start


@pytest.mark.system
class Test:

    def test_it(self):
        exit_code = start(["mcmd", "add", "user", "henk"])
        assert exit_code == 1

    def test_it2(self):
        exit_code = start(["mcmd", "give", "henk", "write", "it_emx"])
        assert exit_code == 1
