from os import path
from pathlib import Path
from typing import List

import mcmd.io.ask
from mcmd.core.errors import McmdError
from mcmd.io import io


def get_file_name_from_path(file_path: str) -> str:
    """
    get_file_name returns a file name from a path to the file
    :param file_path: path to the file (i.e. /Users/henk/Desktop/example.xlsx)
    :return: filename (i.e. example.xlsx)
    """
    return path.basename(file_path)


def get_files(folders: List[Path]) -> List[Path]:
    """
    loops through specified folders and appends their files to a list
    :param folders: a list of paths to folders
    :return: files: a dictionary with as key a file and as value a list of the paths that lead to the file
    """
    files = list()
    for folder in folders:
        if not folder.is_dir():
            io.warn("Folder %s doesn't exist" % folder)

        for file in list(folder.glob('*.*')):
            files.append(file)
    return files


def read_file(file: Path) -> str:
    """
    read_file reads the file data into a string
    :param file: file to read from
    :return: file contents
    """
    try:
        with file.open() as file_handle:
            content = file_handle.read()
    except OSError as e:
        raise McmdError('Error reading file: {}'.format(str(e)))
    return content


def read_file_lines(file: Path) -> List[str]:
    """
    read_file reads the file data into a list of strings
    :param file: file to read from
    :return: list of lines
    """
    try:
        with file.open() as file_handle:
            content = file_handle.readlines()
    except OSError as e:
        raise McmdError('Error reading file: {}'.format(str(e)))
    return content


def select_file_from_folders(folders: List[Path], file_name: str) -> Path:
    """
    Selects a file from a list of folders. File name can be supplied with or without extension. When there are multiple
    matches, the user will be asked to choose one.
    :param folders: a list of folders
    :param file_name: the name of the file to get the path of, with or without extension
    :return: the selected path

    :exception McmdError if selected file was not found
    """
    files = get_files(folders)
    return select_path(files, file_name)


def select_path(files: List[Path], file_name: str) -> Path:
    """
    select_path selects the path from a list of paths, asks user's input when result is ambiguous
    :param files: a list of files
    :param file_name: the name of the file to get the path of, with or withou extension
    :return: the selected path

    :exception McmdError if selected file was not found
    """

    matches = list()
    for file in files:
        if file_name == file.stem or file_name == file.name:
            matches.append(file)

    if len(matches) > 0:
        if len(matches) > 1:
            file_path = _choose_file(matches, file_name)
        else:
            file_path = matches[0]
    else:
        raise McmdError('No file found for {}'.format(file_name))
    return file_path


def _choose_file(paths: List[Path], name: str):
    """
    _choose_file asks the user to choose a file out of the possible file paths
    :param paths: the list of paths to the file
    :param name: the filename
    :return: the selected path
    """
    choices = [str(file_path) for file_path in paths]
    answer = mcmd.io.ask.multi_choice('Multiple files found for %s. Pick one:' % name, choices)
    return Path(answer)
