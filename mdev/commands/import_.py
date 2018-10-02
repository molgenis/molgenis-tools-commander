from pathlib import Path
from urllib.parse import urljoin

import polling
import requests

from mdev import io
from mdev.client import github_client as github
from mdev.client.molgenis_client import login, post_file, get
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError, config_string_to_paths

config = get_config()


def import_(args):
    login(args)

    if args.from_path:
        io.start('Importing from path %s' % highlight(args.file))
        file = Path(args.file)
        if not file.is_file():
            raise MdevError("File %s doesn't exist" % str(file.resolve()))

        _do_import(file, args.to_package)
    elif args.from_issue:
        issue_num = args.from_issue
        attachment = _select_attachment(issue_num, args.file)
        file_path = _download_attachment(attachment, issue_num)
        _do_import(file_path, args.to_package)
    else:
        file_name = args.file
        files = _scan_folders_for_files(_get_molgenis_folders() + _get_quick_folders())

        if file_name in files:
            file = files[file_name]
            _do_import(file, args.to_package)
        else:
            raise MdevError('No file found for %s' % file_name)


def _select_attachment(issue_num, wanted_attachment):
    """Gets attachments from a GitHub issue. If wanted_attachment is specified it will try to select that attachment."""
    attachments = github.get_attachments(issue_num)
    if len(attachments) == 0:
        raise MdevError("Issue #%s doesn't contain any files" % issue_num)

    if wanted_attachment:
        selected = [a for a in attachments if a.name == wanted_attachment]
        if len(selected) == 0:
            raise MdevError('There are no attachments named %s.' % wanted_attachment)
        if len(selected) > 1:
            raise MdevError('Multiple attachments with name %s found.' % wanted_attachment)
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


def _download_attachment(attachment, issue_num):
    issue_folder = Path().home().joinpath('.mdev', 'issues', issue_num)
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
        raise MdevError('Error downloading GitHub attachment: %s' % str(e))
    io.succeed()
    return file_path


def _do_import(file_path, package):
    io.start('Importing %s' % (highlight(file_path.name)))
    data = {'action': _get_import_action(file_path)}

    if package:
        data['packageId'] = package

    response = post_file(config.get('api', 'import'), file_path.resolve(), data)
    import_run_url = urljoin(config.get('api', 'host'), response.text)
    status, message = _poll_for_completion(import_run_url)
    if status == 'FAILED':
        raise MdevError(message)


def _get_import_action(file):
    if '.owl' in file.name:
        return 'add'
    else:
        config.get('set', 'import_action')


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

        for file in list(folder.glob('*.*')):
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
