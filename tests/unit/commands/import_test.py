import unittest

import pytest
from mock import patch

from mcmd.client.github_client import Attachment
from mcmd.commands import import_


@pytest.mark.unit
class ImportMethodsTest(unittest.TestCase):
    @patch('mcmd.io.multi_choice')
    def test_choose_attachments(self, multi_choice):
        multi_choice.return_value = 'other_file.xlsx'
        a1 = Attachment('url/1234/file.xlsx')
        a2 = Attachment('url/4567/other_file.xlsx')
        ret = import_._choose_attachment([a1, a2])
        self.assertEqual(ret, a2)

    @patch('mcmd.io.multi_choice')
    def test_choose_attachments_with_duplicates(self, multi_choice):
        multi_choice.return_value = '1234/file.xlsx'
        a1 = Attachment('url/1234/file.xlsx')
        a2 = Attachment('url/4567/file.xlsx')
        ret = import_._choose_attachment([a1, a2])
        self.assertEqual(ret, a1)

    def test_create_attachment_map(self):
        a1 = Attachment('url/1234/file.xlsx')
        a2 = Attachment('url/4567/file.xlsx')
        a3 = Attachment('url/1234/other_file.xlsx')
        ret = import_._create_attachment_map([a1, a2, a3])
        self.assertEqual(ret, {'1234/file.xlsx': a1, '4567/file.xlsx': a2, 'other_file.xlsx': a3})
