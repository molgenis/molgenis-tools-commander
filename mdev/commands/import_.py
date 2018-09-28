import re
from pathlib import Path
from urllib.parse import urljoin

import polling
import requests
from github import Github, UnknownObjectException

from mdev import io
from mdev.client import login, post_file, get
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError, config_string_to_paths

config = get_config()


def import_(args):
    login(args)
    to_package = None
    if args.to_package:
        to_package = args.to_package

    if args.from_path:
        io.start('Importing from path %s' % highlight(args.file))
        file = Path(args.file)
        if not file.is_file():
            raise MdevError("File %s doesn't exist" % str(file.resolve()))

        _do_import(args.file, to_package)
    elif args.from_issue:
        issue_num = args.file

        issue_folder = Path.home().joinpath('.mdev', 'issues', issue_num)
        if not issue_folder.exists():
            file_path = _download_github_file(issue_num)
        else:
            file_path = list(_scan_folders_for_files([issue_folder]))[0]

        io.start('Importing %s' % file_path)
        _do_import(file_path, to_package)

    else:
        file_name = args.file
        io.start('Importing %s' % highlight(file_name))

        files = _scan_folders_for_files(_get_molgenis_folders() + _get_quick_folders())

        if file_name in files:
            file = files[file_name]
            _do_import(file, to_package)
        else:
            raise MdevError('No file found for %s' % file_name)


def _download_github_file(issue_num):
    try:
        issue = Github().get_organization('molgenis').get_repo('molgenis').get_issue(int(issue_num))
    except ValueError:
        raise MdevError('Not a valid issue number: %s' % issue_num)
    except UnknownObjectException:
        raise MdevError("Issue #%s doesn't exist" % issue_num)

    # GitHub has no API for downloading attachments yet so we get them from the issue description
    file_links = re.findall('\(https://github.com/molgenis/molgenis/files/.*\)', issue.body)
    if len(file_links) == 0:
        raise MdevError("Issue #%s doesn't contain any files" % issue_num)
    file_links = list(map(lambda s: s.strip('()'), file_links))

    files = {'/'.join(link.rsplit('/', 2)[-2:]): link for link in file_links}

    if len(files) > 1:
        # TODO implement downloading of multiple files
        raise MdevError('Issue contains more than one file. (Not supported yet).')

    issue_folder = Path().home().joinpath('.mdev', 'issues', issue_num)
    issue_folder.mkdir(parents=True, exist_ok=True)

    link = file_links[0]
    name = link.rsplit('/', 1)[-1]
    io.start('Downloading %s from GitHub issue %s' % (highlight(name), highlight('#' + issue_num)))
    file_path = issue_folder.joinpath(name)
    r = requests.get(file_links[0])
    with file_path.open('wb') as fp:
        fp.write(r.content)
    io.succeed()
    return file_path


def _do_import(file_path, to_package):
    data = {'action': config.get('set', 'import_action')}
    if to_package:
        data['packageId'] = to_package
    response = post_file(config.get('api', 'import'), file_path, data)
    import_run_url = urljoin(config.get('api', 'host'), response.text)
    status, message = _poll_for_completion(import_run_url)
    if status == 'FAILED':
        raise MdevError(message)


def _poll_for_completion(url):
    polling.poll(lambda: get(url).json()['status'] != 'RUNNING',
                 step=0.1,
                 poll_forever=True)
    import_run = get(url).json()
    return import_run['status'], import_run['message']


def _scan_folders_for_files(folders):
    files = dict()
    for folder in folders:
        if not folder.is_dir():
            io.warn('Folder %s is not a valid folder, skipping it...' % folder)

        for file in list(folder.glob('*.xlsx')):
            files[file.stem] = file
    return files


def _get_molgenis_folders():
    if not config.has_option('data', 'git_root') or not config.has_option('data', 'git_paths'):
        io.info('Molgenis git paths not configured. Edit the mdev.ini file to include the test data.')
        return list()
    else:
        return config_string_to_paths(config.get('data', 'git_paths'))


def _get_quick_folders():
    if not config.has_option('data', 'quick_folders'):
        return list()
    else:
        return config_string_to_paths(config.get('data', 'quick_folders'))
