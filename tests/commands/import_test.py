import unittest

from mock import patch

from mdev.client.github_client import Attachment
from mdev.commands import import_


class ImportMethodsTest(unittest.TestCase):
    @patch('mdev.io.multi_choice')
    def test_choose_attachments(self, multi_choice):
        multi_choice.return_value = 'other_file.xlsx'
        a1 = Attachment('url/1234/file.xlsx')
        a2 = Attachment('url/4567/other_file.xlsx')
        ret = import_._choose_attachments([a1, a2])
        self.assertEqual(ret, [a2])

    @patch('mdev.io.multi_choice')
    def test_choose_attachments_all(self, multi_choice):
        multi_choice.return_value = 'All'
        a1 = Attachment('url/1234/file.xlsx')
        a2 = Attachment('url/4567/other_file.xlsx')
        a3 = Attachment('url/4567/file.xlsx')
        ret = import_._choose_attachments([a1, a2, a3])
        self.assertEqual(ret, [a1, a2, a3])

    @patch('mdev.io.multi_choice')
    def test_choose_attachments_with_duplicates(self, multi_choice):
        multi_choice.return_value = '1234/file.xlsx'
        a1 = Attachment('url/1234/file.xlsx')
        a2 = Attachment('url/4567/file.xlsx')
        ret = import_._choose_attachments([a1, a2])
        self.assertEqual(ret, [a1])

    @patch('mdev.io.multi_choice')
    def test_choose_attachments_all_with_duplicates(self, multi_choice):
        multi_choice.return_value = 'All'
        a1 = Attachment('url/1234/file.xlsx')
        a2 = Attachment('url/4567/file.xlsx')
        a3 = Attachment('url/1234/other_file.xlsx')
        ret = import_._choose_attachments([a1, a2, a3])
        self.assertEqual(ret, [a1, a2, a3])

    def test_create_attachment_map(self):
        a1 = Attachment('url/1234/file.xlsx')
        a2 = Attachment('url/4567/file.xlsx')
        a3 = Attachment('url/1234/other_file.xlsx')
        ret = import_._create_attachment_map([a1, a2, a3])
        self.assertEqual(ret, {'1234/file.xlsx': a1, '4567/file.xlsx': a2, 'other_file.xlsx': a3})
