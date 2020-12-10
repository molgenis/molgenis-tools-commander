import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from mcmd.core.errors import McmdError
from mcmd.utils import files


@pytest.mark.unit
class FileUtilsTest(unittest.TestCase):

    @staticmethod
    def test_get_file_name_from_path():
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir).joinpath('tempfile.txt')
            path.open('w')

            name = files.get_file_name_from_path(str(path))

            assert name == 'tempfile.txt'

    @staticmethod
    def test_get_files():
        with TemporaryDirectory() as temp_dir:
            path1 = Path(temp_dir).joinpath('tempfile1.txt')
            path2 = Path(temp_dir).joinpath('tempfile2.txt')
            path3 = Path(temp_dir).joinpath('dir/')
            path1.open('w')
            path2.open('w')
            path3.open('w')

            paths = files.get_files([Path(temp_dir)])

            assert set(paths) == {path1, path2}

    @staticmethod
    def test_read_file():
        with TemporaryDirectory() as temp_dir:
            path1 = Path(temp_dir).joinpath('tempfile1.txt')
            path1.open('w').write('line1\nline2')

            content = files.read_file(path1)

            assert content == 'line1\nline2'

    @staticmethod
    def test_read_file_lines():
        with TemporaryDirectory() as temp_dir:
            path1 = Path(temp_dir).joinpath('tempfile1.txt')
            path1.open('w').write('line1\nline2')

            lines = files.read_file_lines(path1)

            assert lines == ['line1', 'line2']

    @staticmethod
    def test_select_path_without_extension():
        with TemporaryDirectory() as temp_dir:
            path1 = Path(temp_dir).joinpath('tempfile1.txt')
            path2 = Path(temp_dir).joinpath('tempfile2.txt')
            path1.open('w')
            path2.open('w')

            selected_file = files.select_file([path1, path2], 'tempfile1')

            assert selected_file == path1

    @staticmethod
    def test_select_path_with_extension():
        with TemporaryDirectory() as temp_dir:
            path1 = Path(temp_dir).joinpath('tempfile1.txt')
            path2 = Path(temp_dir).joinpath('tempfile2.txt')
            path1.open('w')
            path2.open('w')

            selected_file = files.select_file([path1, path2], 'tempfile1.txt')

            assert selected_file == path1

    @patch('mcmd.io.ask.multi_choice')
    def test_select_path_clash(self, multi_choice):
        with TemporaryDirectory() as temp_dir:
            path1 = Path(temp_dir).joinpath('tempfile.txt')
            path2 = Path(temp_dir).joinpath('tempfile.csv')
            path1.open('w')
            path2.open('w')
            multi_choice.return_value = str(path1)

            selected_file = files.select_file([path1, path2], 'tempfile')

            assert selected_file == path1

    @staticmethod
    def test_select_path_unknown():
        with TemporaryDirectory() as temp_dir:
            with pytest.raises(McmdError):
                path1 = Path(temp_dir).joinpath('tempfile1.txt')
                path1.open('w')

                files.select_file([path1], 'tempfile1.csv')

    @staticmethod
    def test_select_path_from_folders():
        with TemporaryDirectory() as temp_dir1:
            with TemporaryDirectory() as temp_dir2:
                path1 = Path(temp_dir1).joinpath('tempfile1.txt')
                path2 = Path(temp_dir2).joinpath('tempfile2.txt')
                path1.open('w')
                path2.open('w')

                selected_file = files.select_file_from_folders([Path(temp_dir1), Path(temp_dir2)],
                                                               'tempfile1.txt')

                assert selected_file == path1
