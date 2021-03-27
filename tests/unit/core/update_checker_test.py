import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

import pytest
import responses
from packaging.version import Version

from mcmd.core import store
# noinspection PyProtectedMember
from mcmd.core.update_checker import _latest_version, check


@pytest.mark.unit
@patch('mcmd.core.store._persist', Mock())
class ErrorsTest(unittest.TestCase):

    @responses.activate
    def test_latest_version(self):
        responses.add(responses.GET, 'http://pypi.org/simple/molgenis-commander/', status=200, body=pypi_version_page)

        assert _latest_version() == Version('1.9.0')

    @responses.activate
    def test_latest_version_error(self):
        responses.add(responses.GET, 'http://pypi.org/simple/molgenis-commander/', status=500)

        assert _latest_version() is None

    @patch('mcmd.core.update_checker._show_update_message')
    def test_already_checked_today(self, message):
        now = datetime.now()
        store.set_last_version_check(now)
        store.set_update_available(None)

        check()

        assert store.get_last_version_check() == now
        assert store.get_update_available() is None
        assert not message.called

    @patch('mcmd.core.update_checker._latest_version')
    @patch('mcmd.core.update_checker._current_version')
    @patch('mcmd.core.update_checker._show_update_message')
    def test_update_available(self, message, current_version, latest_version):
        current_version.return_value = Version('1.8.0')
        latest_version.return_value = Version('1.9.0')
        two_days_ago = datetime.now() - timedelta(days=2)
        store.set_last_version_check(two_days_ago)
        store.set_update_available(None)

        check()

        assert store.get_last_version_check() > two_days_ago
        assert store.get_update_available() == Version('1.9.0')
        assert message.called

    @patch('mcmd.core.update_checker._latest_version')
    @patch('mcmd.core.update_checker._current_version')
    @patch('mcmd.core.update_checker._show_update_message')
    def test_no_update_available(self, message, current_version, latest_version):
        current_version.return_value = Version('1.8.0')
        latest_version.return_value = Version('1.8.0')
        two_days_ago = datetime.now() - timedelta(days=2)
        store.set_last_version_check(two_days_ago)
        store.set_update_available(None)

        check()

        assert store.get_last_version_check() > two_days_ago
        assert store.get_update_available() is None
        assert not message.called

    @patch('mcmd.core.update_checker._latest_version')
    @patch('mcmd.core.update_checker._current_version')
    @patch('mcmd.core.update_checker._show_update_message')
    def test_update_found_previously_and_already_checked_today(self, message, current_version, latest_version):
        current_version.return_value = Version('1.8.0')
        latest_version.return_value = Version('1.10.0')
        now = datetime.now()
        store.set_last_version_check(now)
        store.set_update_available(Version('1.9.0'))

        check()

        assert store.get_last_version_check() == now
        assert store.get_update_available() == Version('1.9.0')
        assert message.called

    @patch('mcmd.core.update_checker._latest_version')
    @patch('mcmd.core.update_checker._current_version')
    @patch('mcmd.core.update_checker._show_update_message')
    def test_update_found_previously(self, message, current_version, latest_version):
        current_version.return_value = Version('1.8.0')
        latest_version.return_value = Version('1.9.0')
        two_days_ago = datetime.now() - timedelta(days=2)
        store.set_last_version_check(two_days_ago)
        store.set_update_available(Version('1.9.0'))

        check()

        assert store.get_last_version_check() > two_days_ago
        assert store.get_update_available() == Version('1.9.0')
        assert message.called

    @patch('mcmd.core.update_checker._latest_version')
    @patch('mcmd.core.update_checker._current_version')
    @patch('mcmd.core.update_checker._show_update_message')
    def test_update_found_previously_and_update_available(self, message, current_version, latest_version):
        current_version.return_value = Version('1.8.0')
        latest_version.return_value = Version('1.10.0')
        two_days_ago = datetime.now() - timedelta(days=2)
        store.set_last_version_check(two_days_ago)
        store.set_update_available(Version('1.9.0'))

        check()

        assert store.get_last_version_check() > two_days_ago
        assert store.get_update_available() == Version('1.10.0')
        assert message.called


pypi_version_page = """
<!DOCTYPE html> <html> <head> <meta name="pypi:repository-version" content="1.0"> <title>Links for 
molgenis-commander</title> </head> <body> <h1>Links for molgenis-commander</h1> <a 
href="https://files.pythonhosted.org/packages/33/52/539b197c6723d0263c9446bc283ad11810fd7cbe588d16d3aa35b2b31bc9
/molgenis-commander-0.1.0.tar.gz#sha256=90c6563e0d65c1828f04ecaf9e4c142c5316716c16869846ac261d462ffe1a9d">molgenis
-commander-0.1.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/92/0a/3377457ba476fb70c353ba8102b7cb2806a2b9c3684588712b8acf24ad06
/molgenis_commander-0.1.0-py3-none-any.whl#sha256=08ba826285101a04b837e44c22a907071250f5b4be1d313d878bda62bfaa7a5c
">molgenis_commander-0.1.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/e8/cf/d7226688b0c0e6dfc5787bd11fc288f2367db372f7626263907f4c40158d
/molgenis-commander-0.1.1.tar.gz#sha256=11672b02215c5b6e27221192471fdb0494df1e82f018f2f49acc5d1932e1bb8c">molgenis
-commander-0.1.1.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/9e/66/906ba8c01b762036bbaeec9a6df24f1afe49a32f4c61e5480a5aaba66896
/molgenis_commander-0.1.1-py3-none-any.whl#sha256=e840e82f8f197fdf07a113e91aa9b2f1c8cb52725544156decc6e690eb225367
">molgenis_commander-0.1.1-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/ff/66/3eed22a290bd155c2cf6d96bc3e54ae6a86b2f86100329992e6b437fe433
/molgenis-commander-0.1.2.tar.gz#sha256=b75184ea7c0b1134156a17bc8cce12cd7fccc45e9398736575baf9c0412e7f73">molgenis
-commander-0.1.2.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/f9/06/c1a96cf87abca9c55e73210a94aa7b3175f0be60f10299847a36fd006983
/molgenis_commander-0.1.2-py3-none-any.whl#sha256=e8a6ea80bcfffc9bcde5c83834101c3b74eaf7eda67e1b67befe5cdc964d6c62
">molgenis_commander-0.1.2-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/d7/6e/7e29c4a01e27b4278b078da61ed786617d48bc89fb9a4315e07189530dbb
/molgenis-commander-1.0.0.tar.gz#sha256=29ae584e2e5056ef3e4b30df555fbaa434a0a345440a53b23347b941193747a5">molgenis
-commander-1.0.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/51/83/c659f3fc15a9d4447a7fcdc80bc81273f38b7514e4684ce0e945ca279541
/molgenis_commander-1.0.0-py3-none-any.whl#sha256=74574082ede8565e1b68dcebc23cd58c2fdbd2e118debdf8b90cf2aa82d48aec
">molgenis_commander-1.0.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/48/5a/fc187e0e277b33b532c6e8b95ecb679c91bff588178ed5832fe1f40387f4
/molgenis-commander-1.0.1.tar.gz#sha256=261deb8871cb996b620abe18dfb3c4f9a3525333cf4551b1368050d8f75af84d">molgenis
-commander-1.0.1.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/85/9e/7ab06472da61a74b935a8578b32c4f7ab3a8b66f613a248223f531ce4f7e
/molgenis_commander-1.0.1-py3-none-any.whl#sha256=766ad68ca83a0113e1409365853421c4e7152e1a03c2766e405e40de93a05756
">molgenis_commander-1.0.1-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/b1/00/9d5df98128e0d535147e84a6b5193c24d74d4b2c6550fbc5b9b1204f365c
/molgenis-commander-1.1.0.tar.gz#sha256=0b9225221ebfb7b0db71e7fff0d342e225e56032832b468a74d93ef7c586cda3" 
data-requires-python="&gt;3.7.0">molgenis-commander-1.1.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/00/9d/de57f717fd7f5f6f52be840f1b3b8987f60c13ac3a1f0511779189e0c49a
/molgenis_commander-1.1.0-py3-none-any.whl#sha256=64fcf264c4c33f3821db612c7a180382ea5c341c3858baadd7be496091d2542d" 
data-requires-python="&gt;3.7.0">molgenis_commander-1.1.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/57/ab/1b5f77eb5afcad08b4d13afdf712e91807c2c952afba2e3d1ac179858c6f
/molgenis-commander-1.1.1.tar.gz#sha256=5e24bf23d48c8360cf5c5eb6d708a6b35cb6d0751d6d5739027177ca5f764be3" 
data-requires-python="&gt;3.7.0">molgenis-commander-1.1.1.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/22/8d/5b80522421f87eb771d104b8dc75dfc75bf41d452e24d8480d551840ae82
/molgenis_commander-1.1.1-py3-none-any.whl#sha256=3d11100970eac8c8a668caf65607a87ac5c6b08b60864cf60453b447e16c3810" 
data-requires-python="&gt;3.7.0">molgenis_commander-1.1.1-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/0b/e3/1ecd045d9d4a3b2f57b4bbe6de1a1363671f9557afddc3d52a72f0018453
/molgenis-commander-1.1.3.tar.gz#sha256=fea57648606d1675b74a722b2cf1633e32534c892992bf65f34d1c5d8672c04f">molgenis
-commander-1.1.3.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/76/03/7f6a00f6d6b711c40938d3b8a9556790ea20ce60d3751f16c23c3cea3ac2
/molgenis_commander-1.1.3-py3-none-any.whl#sha256=bbc5eed063a3ec7f30fc04f28b9e95e6afab41fff0d19f53d1c24a8cb84a8c82
">molgenis_commander-1.1.3-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/ee/b5/9eec24ca4b9368edd2cff12b6422a8fc038e9fcdb2049d7389fa5fa5f11b
/molgenis-commander-1.2.0.tar.gz#sha256=61aaad044c547cb9b6f3b2e0a04e456847566b0d80f8ff21804bd47f25279f1b">molgenis
-commander-1.2.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/ba/f6/2bd22e684bad9af4f64c9acb6e233300e5e6184212aba38f1fcb277c2670
/molgenis_commander-1.2.0-py3-none-any.whl#sha256=a52267409949caea02a97462830298f7d92c871fc40e25abf2b3d5adc352e85a
">molgenis_commander-1.2.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/43/f9/7dcaf7c44b9a32ee47db32e5e33f80c101ea61e683d505f13547a172ebe1
/molgenis-commander-1.3.0.tar.gz#sha256=25ea9a286259a5f988bd092949fb7a6cc0a1fdfc4fb91410b735a82134f6841c">molgenis
-commander-1.3.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/82/c8/17484922b39537984bb57ec7d936e3641430074306d394bb90ba3b3a8da8
/molgenis_commander-1.3.0-py3-none-any.whl#sha256=70ebbfc97d9b58d6af55376bb525c429a100fc0c95a9f14649fe5f90b24e683c
">molgenis_commander-1.3.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/d1/58/1ae8b23094f971594700be30001df3fbbeff1324f3774529d36f6397050c
/molgenis-commander-1.3.1.tar.gz#sha256=3b88414177b1b678e6dbba96c376d0241b661fa08316d9d015b42dc6ece47fff">molgenis
-commander-1.3.1.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/a1/b9/daac8270d4154159de3aeab5160f0b31de6ec8693be0e723d94c4aef6a4c
/molgenis_commander-1.3.1-py3-none-any.whl#sha256=9d1c98e8a495cfae814135358eb09e088bbf14c64b5a85666592d6a2f8fd9179
">molgenis_commander-1.3.1-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/8d/de/f747c325eefab008e6376a994e2c4ed7f347ae8b5c23e88d1d39defcde8a
/molgenis-commander-1.4.0.tar.gz#sha256=b043c11f75bb03fd5684dc7f7b28d0c2a53fa0e972d2d08f008b724bb1ceea14">molgenis
-commander-1.4.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/14/83/acd7a99dcb14910ac10d6ba7a9a2b54532c51f7938247586d3654270f2e9
/molgenis_commander-1.4.0-py3-none-any.whl#sha256=cb2fffaf33da807ec608b52ddcd27d5703bcd69e751b84328bccca39a9a3686e
">molgenis_commander-1.4.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/82/36/13bc7101b95432f2e46cab8469eef3388eb08566a8991582fe8d7af1eb6f
/molgenis-commander-1.4.1.tar.gz#sha256=beba2c169ac9cc15515abd2626a49429b004f2d85145ec02fecdcb2eec051828">molgenis
-commander-1.4.1.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/b0/21/741a3a467b3698a6255a420de97ce716190329a68b350698beb61cc20b36
/molgenis_commander-1.4.1-py3-none-any.whl#sha256=970b860457a9cd406b175d243560719faa97f1b002cc5ba52a3d6aa460e5e77a
">molgenis_commander-1.4.1-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/c6/1c/7d4c7e9113c75758208afe508b75e8603954359b048bdb2b8a9f0757e930
/molgenis-commander-1.4.2.tar.gz#sha256=35c5550251187f5622c36d310e3bcd3c74e45b4130121b1a1516d33c78b7e02f">molgenis
-commander-1.4.2.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/99/db/c443a74cfd654d378e878965dd093935fc50e8b225df3fa8688d22a563ed
/molgenis_commander-1.4.2-py3-none-any.whl#sha256=13636c3c597abbb0fa8c8cf50c9a5965caf70d7c612478bd44d0faea1b7b60f2
">molgenis_commander-1.4.2-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/9e/76/21e33dfbe11cdd5ca9c3e825e2c49ba47a8c651149bd4f18c39b976e8145
/molgenis-commander-1.4.3.tar.gz#sha256=700440bbaf030654475dfd04d95f362fcd7cbbf5457e15e7916791e913025dec">molgenis
-commander-1.4.3.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/47/d8/843d92e72905f67caf280925e8616acdb3139e27e6dace854fe2c7019257
/molgenis_commander-1.4.3-py3-none-any.whl#sha256=70e7a7ed1d287b66cad8671a41bd90edfe7790d57358b0435349ebb87da85a3e
">molgenis_commander-1.4.3-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/2b/f5/5593063b20c88d01715a659a266d4ba06018cfd56209253f31f86446ef4a
/molgenis-commander-1.5.0.tar.gz#sha256=d941610572df7de71a8dfcfa9e455c62902792533efb0d098c46264c21303106">molgenis
-commander-1.5.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/57/73/379a57a46c17d8feb59e317f90d2dfc4d365df9ae24727f177f1e813d206
/molgenis_commander-1.5.0-py3-none-any.whl#sha256=8f072ab400b769b4025cac7e622c13660484348484c1520401d850d7a45101f1
">molgenis_commander-1.5.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/76/97/b1b787c4a5a79c71240b4e8d366e6721bc744dd9f937f69c7e6d1500c52d
/molgenis-commander-1.6.0.tar.gz#sha256=36feada77c955a1e3e7b5a35dfebd2feb4057093d2e2a2a22332d9ba2728062b">molgenis
-commander-1.6.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/3d/90/b99ca22a28a5478b7fd3dd3d8533355a884b7b4ddd0e0213fbac1ffbc669
/molgenis_commander-1.6.0-py3-none-any.whl#sha256=fc12f0a032b66093f9f8c62fb41906f3e1b89036143e84454a86503274c098e7
">molgenis_commander-1.6.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/01/63/9867b3ee4d81222d86e13af2ca9e0d5e811ab46cb1b4fb125b5ca1cfe0cc
/molgenis-commander-1.6.1.tar.gz#sha256=83bd29a2e689d5e22f880a4408562a7c213c016e0656f8d57b4a5e93df849088">molgenis
-commander-1.6.1.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/9e/6f/6b13bd9bc52fe1f83dd28031155fc4b8316344f0d7095b79f7c004f99860
/molgenis_commander-1.6.1-py3-none-any.whl#sha256=c08bb1bd69adcb8ee7a74d8f4da2ca431e7a24a8634253e23449f874287775e2
">molgenis_commander-1.6.1-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/6a/b5/86ee9202827ff7bdf776e7510052e66139e987305767adce8f1db1396d33
/molgenis-commander-1.7.0.tar.gz#sha256=96ce36ae2b5b5243df27a80f7b0289deda2d9ce384ea158c168275c332919c2b">molgenis
-commander-1.7.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/a6/e2/7c350f6538289a4d492f2df38661f99fd9003edb489c063553caa0342513
/molgenis_commander-1.7.0-py3-none-any.whl#sha256=a92675ada8984035e950bbbe25febf2844fa03a3caa5426cc6de2a682bf0e708
">molgenis_commander-1.7.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/c1/98/37cea23ab4cbfe1dab44b688154f0519e33c90c6a1e9b1e8a7f0a7fc03a4
/molgenis-commander-1.8.0.tar.gz#sha256=21c7a8894c7a3af80b7569e6993cc573011990e7dee1fc1dc59f70955f8fa9ce">molgenis
-commander-1.8.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/66/89/5873ddc3ddb2f73752d1bddaa6b04aa540540176909526037659c6f9ecff
/molgenis_commander-1.8.0-py3-none-any.whl#sha256=899ec35d121bbb512202a4949234e226b8c2a060b90b5db1da6ee65c0f9f23ce
">molgenis_commander-1.8.0-py3-none-any.whl</a><br/> <a 
href="https://files.pythonhosted.org/packages/c4/a5/f2d9550c67ab7924fe247899ebcd5477bc85348964b1aecdd96fe3eb02d3
/molgenis-commander-1.9.0.tar.gz#sha256=1376b22e6cd47e4bc841ee285e2d5c625e0d57229d5c5c3ca3fe8f3047b9e5cc">molgenis
-commander-1.9.0.tar.gz</a><br/> <a 
href="https://files.pythonhosted.org/packages/b3/f7/75f4a14bf2a29948bb70198cb6d3c434a15a7d13ed1aacfecb0dfdba2427
/molgenis_commander-1.9.0-py3-none-any.whl#sha256=dff51567376f105a86dc164074fcf08f3dfb00f4fbff2d05a6a87af06ddbd2c8
">molgenis_commander-1.9.0-py3-none-any.whl</a><br/> </body> </html> <!--SERIAL 8725982--> """
