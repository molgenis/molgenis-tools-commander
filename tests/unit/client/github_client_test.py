import unittest

import pytest

from mcmd.github import client


@pytest.mark.unit
class GithubTest(unittest.TestCase):
    def test_get_attachments(self):
        body = """
        - Import [emx_tags-only.xlsx](https://github.com/molgenis/molgenis/files/626884/emx_tags-only.xlsx) or [emx_package-only.xlsx](https://github.com/molgenis/molgenis/files/626894/emx_package-only.xlsx) using the ```Upload``` plugin
        """

        ret = client._parse_attachment_urls(body)
        self.assertEqual(ret, ['https://github.com/molgenis/molgenis/files/626884/emx_tags-only.xlsx',
                               'https://github.com/molgenis/molgenis/files/626894/emx_package-only.xlsx'])
