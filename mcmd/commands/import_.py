from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin

import polling
import requests

from mcmd import io
from mcmd.client import github_client as github
from mcmd.client.molgenis_client import login, post_file, get, import_by_url
from mcmd.config.config import config
from mcmd.config.home import get_issues_folder
from mcmd.io import highlight
from mcmd.utils import McmdError, config_string_to_paths


# =========
# Arguments
# =========

def arguments(subparsers):
    p_import = subparsers.add_parser('import',
                                     help='Import a file')
    p_import.set_defaults(func=import_,
                          write_to_history=True)
    p_import.add_argument('file',
                          nargs='?',
                          help='The file to upload')
    p_import_source = p_import.add_mutually_exclusive_group()
    p_import_source.add_argument('--from-path', '-p',
                                 action='store_true',
                                 help='Import a file the old school way (by path)')
    p_import_source.add_argument('--from-issue', '-i',
                                 metavar='ISSUE_NUMBER',
                                 help='Import a file from a GitHub issue')
    p_import_source.add_argument('--from-url',
                                 metavar='URL',
                                 help='Import a file from a URL. Uses the importByUrl endpoint of the MOLGENIS '
                                      'importer.')
    p_import.add_argument('--in',
                          dest='to_package',
                          type=str,
                          metavar='PACKAGE_ID',
                          help='The package to import to')
    return p_import


# =======
# Methods
# =======

@login
def import_(args):
    if args.from_path:
        _import_from_path(args)
    elif args.from_url:
        _import_from_url(args)
    elif args.from_issue:
        _import_from_issue(args)
    else:
        _import_from_quick_folders(args)


def _import_from_url(args):
    file_url = args.from_url
    file_name = file_url.split("/")[-1]
    io.start('Importing from URL %s' % highlight(file_url))

    params = {'action': _get_import_action(file_name),
              'metadataAction': 'upsert'}

    if args.to_package:
        params['packageId'] = args.to_package

    params['url'] = file_url

    response = import_by_url(params)
    import_run_url = urljoin(config().get('api', 'host'), response.text)
    status, message = _poll_for_completion(import_run_url)
    if status == 'FAILED':
        raise McmdError(message)


def _import_from_quick_folders(args):
    file_name = args.file
    file_map = _scan_folders_for_files(_get_molgenis_folders() + _get_quick_folders())
    path = _select_path(file_map, file_name)
    _do_import(path, args.to_package)


def _import_from_issue(args):
    issue_num = args.from_issue
    attachment = _select_attachment(issue_num, args.file)
    file_path = _download_attachment(attachment, issue_num)
    _do_import(file_path, args.to_package)


def _import_from_path(args):
    io.start('Importing from path %s' % highlight(args.file))
    file = Path(args.file)
    if not file.is_file():
        raise McmdError("File %s doesn't exist" % str(file.resolve()))
    _do_import(file, args.to_package)


def _select_path(file_map, file_name):
    if file_name in file_map:
        paths = file_map[file_name]
        if len(paths) > 1:
            path = _choose_file(paths, file_name)
        else:
            path = paths[0]
    else:
        raise McmdError('No file found for %s' % file_name)
    return path


def _select_attachment(issue_num, wanted_attachment):
    """Gets attachments from a GitHub issue. If wanted_attachment is specified it will try to select that attachment."""
    attachments = github.get_attachments(issue_num)
    if len(attachments) == 0:
        raise McmdError("Issue #%s doesn't contain any files" % issue_num)

    if wanted_attachment:
        selected = [a for a in attachments if a.name == wanted_attachment]
        if len(selected) == 0:
            raise McmdError('There are no attachments named %s.' % wanted_attachment)
        if len(selected) > 1:
            raise McmdError('Multiple attachments with name %s found.' % wanted_attachment)
        return selected[0]
    else:
        if len(attachments) > 1:
            return _choose_attachment(attachments)
        else:
            return attachments[0]


def _create_attachment_map(attachments):
    """"Creates a dict of name/attachment pairs. If the name isn't unique, uses the identifier as key. Example:
            1234/example.xls
            4567/example.xls
            other_example.xls
    """
    names = [a.name for a in attachments]

    attachment_map = dict()
    for a in attachments:
        if names.count(a.name) > 1:
            attachment_map[a.id] = a
        else:
            attachment_map[a.name] = a

    return attachment_map


def _choose_attachment(attachments):
    """Let user choose from multiple attachments. Attachments with duplicate names will display their id."""
    attachment_map = _create_attachment_map(attachments)
    choices = list(attachment_map.keys())

    answer = io.multi_choice('Multiple attachments found. Choose which one to import:', choices)
    return attachment_map[answer]


def _choose_file(paths, name):
    choices = [str(path) for path in paths]
    answer = io.multi_choice('Multiple files found for %s. Pick one:' % name, choices)
    return Path(answer)


def _download_attachment(attachment, issue_num):
    issue_folder = get_issues_folder().joinpath(issue_num)
    issue_folder.mkdir(parents=True, exist_ok=True)
    file_path = issue_folder.joinpath(attachment.name)

    if file_path.exists():
        overwrite = io.confirm('File %s already exists. Re-download?' % file_path.name)
        if not overwrite:
            return file_path

    io.start('Downloading %s from GitHub issue %s' % (highlight(attachment.name), highlight('#' + issue_num)))
    try:
        r = requests.get(attachment.url)
        r.raise_for_status()
        with file_path.open('wb') as f:
            f.write(r.content)
    except (OSError, requests.RequestException, requests.HTTPError) as e:
        raise McmdError('Error downloading GitHub attachment: %s' % str(e))
    io.succeed()
    return file_path


def _do_import(file_path, package):
    io.start('Importing %s' % (highlight(file_path.name)))

    params = {'action': _get_import_action(file_path.name),
              'metadataAction': 'upsert'}

    if package:
        params['packageId'] = package

    response = post_file(config().get('api', 'import'), file_path.resolve(), params)
    import_run_url = urljoin(config().get('api', 'host'), response.text)
    status, message = _poll_for_completion(import_run_url)
    if status == 'FAILED':
        raise McmdError(message)


def _get_import_action(file_name):
    if '.owl' in file_name or '.obo' in file_name:
        return 'add'
    else:
        return config().get('set', 'import_action')


def _poll_for_completion(url):
    polling.poll(lambda: get(url).json()['status'] != 'RUNNING',
                 step=0.1,
                 poll_forever=True)
    import_run = get(url).json()
    return import_run['status'], import_run['message']


def _scan_folders_for_files(folders):
    files = defaultdict(list)
    for folder in folders:
        if not folder.is_dir():
            io.warn("Folder %s doesn't exist" % folder)

        for file in list(folder.glob('*.*')):
            files[file.stem].append(file)
    return files


def _get_molgenis_folders():
    if not config().has_option('data', 'git_root') or not config().has_option('data', 'git_paths'):
        return list()
    else:
        return config_string_to_paths(config().get('data', 'git_paths'))


def _get_quick_folders():
    if not config().has_option('data', 'quick_folders'):
        return list()
    else:
        return config_string_to_paths(config().get('data', 'quick_folders'))
