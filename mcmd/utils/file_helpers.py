from collections.__init__ import defaultdict
from os import path
from pathlib import Path

import mcmd.io.ask
from mcmd.io import io
from mcmd.core.errors import McmdError


def get_file_name_from_path(file_path):
    """
    get_file_name returns a file name from a path to the file
    :param file_path: path to the file (i.e. /Users/henk/Desktop/example.xlsx)
    :return: filename (i.e. example.xlsx)
    """
    return path.basename(file_path)


def scan_folders_for_files(folders):
    """
    scan_folders_for_files loops through specified folders to look for their files
    :param folders: a list of paths to folders
    :return: files: a dictionary with as key a file and as value a list of the paths that lead to the file
    """
    files = defaultdict(list)
    for folder in folders:
        if not folder.is_dir():
            io.warn("Folder %s doesn't exist" % folder)

        for file in list(folder.glob('*.*')):
            files[file.stem].append(file)
    return files


def select_path(file_map, file_name):
    """
    select_path selects the path to a file from a dictionary of files with paths
    :param file_map: a dictionary with file as key and as value a list of paths l
    :param file_name: the name of the file to get the path of
    :return: the selected path

    :exception McmdError if selected file was not found
    """
    if file_name in file_map:
        paths = file_map[file_name]
        if len(paths) > 1:
            file_path = _choose_file(paths, file_name)
        else:
            file_path = paths[0]
    else:
        raise McmdError('No file found for %s' % file_name)
    return file_path


def _choose_file(paths, name):
    """
    _choose_file asks the user to choose a file out of the possible file paths
    :param paths: the list of paths to the file
    :param name: the filename
    :return: the selected path
    """
    choices = [str(file_path) for file_path in paths]
    answer = mcmd.io.ask.multi_choice('Multiple files found for %s. Pick one:' % name, choices)
    return Path(answer)
