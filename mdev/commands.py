import re
from pathlib import Path
from urllib.parse import urljoin

import polling
import requests
from github import Github, UnknownObjectException
from halo import Halo

from mdev.client import login, get, post, post_file
from mdev.configuration import get_config
from mdev.logging import get_logger, highlight
from mdev.utils import lower_kebab, config_string_to_paths, MdevError, upper_snake

log = get_logger()
config = get_config()
spinner = None


def execute(args, exit_on_error):
    global spinner

    try:
        spinner = Halo(spinner='dots')
        spinner.start()
        args.func(args)
    except MdevError as e:
        spinner.fail()
        log.error('  ' + str(e).strip('\"\''))
        if exit_on_error:
            exit(1)
    else:
        spinner.succeed()


def import_(args):
    if args.from_path:
        spinner.text = 'Importing from path %s' % highlight(args.file)
        login(args)
        file = Path(args.file)
        if not file.is_file():
            raise MdevError("File %s doesn't exist" % str(file.resolve()))

        _do_import(args.file)
    elif args.from_issue:
        spinner.text = 'Importing from GitHub issue %s' % highlight('#' + args.file)
        try:
            issue_num = int(args.file)
            issue = Github().get_organization('molgenis').get_repo('molgenis').get_issue(issue_num)
        except ValueError:
            raise MdevError('Not a valid issue number: %s' % args.file)
        except UnknownObjectException:
            raise MdevError("Issue #%s doesn't exist" % args.file)

        # GitHub has no API for downloading attachments yet so we get them from the issue description
        file_links = re.findall('\(https://github.com/molgenis/molgenis/files/.*\)', issue.body)
        if len(file_links) == 0:
            raise MdevError("Issue #%s doesn't contain any files" % issue_num)
        file_links = list(map(lambda s: s.strip('()'), file_links))

        for link in file_links:
            name = link.rsplit('/', 1)[-1]
            r = requests.get(file_links[0])
            open(name, 'wb').write(r.content)

        exit(1)

    else:
        file_name = args.file
        spinner.text = 'Importing %s' % highlight(file_name)
        login(args)

        files = _scan_folders_for_files(_get_molgenis_folders() + _get_quick_folders())

        if file_name in files:
            file = files[file_name]
            _do_import(file)
        else:
            raise MdevError('No file found for %s' % file_name)


def _do_import(file_path):
    response = post_file(config.get('api', 'import'), file_path, {'action': config.get('set', 'import_action')})
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
            log.warn('Folder %s is not a valid folder, skipping it...', folder)

        for file in list(folder.glob('*.xlsx')):
            files[file.stem] = file
    return files


def _get_molgenis_folders():
    if not config.has_option('data', 'git_root') or not config.has_option('data', 'git_paths'):
        spinner.warn()
        log.warn('  Molgenis git paths not configured. Edit the mdev.ini file to include the test data.')
        spinner.start()
        return list()
    else:
        return config_string_to_paths(config.get('data', 'git_paths'))


def _get_quick_folders():
    if not config.has_option('data', 'quick_folders'):
        return list()
    else:
        return config_string_to_paths(config.get('data', 'quick_folders'))


def make(args):
    login(args)
    spinner.text = 'Making user %s a member of role %s' % (highlight(args.user), highlight(args.role.upper()))

    group_name = _find_group(args.role)

    url = config.get('api', 'member') % group_name
    post(url, {'username': args.user, 'roleName': args.role.upper()})


def _find_group(role):
    log.debug('Fetching groups')
    groups = get(config.get('api', 'rest2') + 'sys_sec_Group?attrs=name')
    role = lower_kebab(role)

    matches = {len(group['name']): group['name'] for group in groups.json()['items'] if role.startswith(group['name'])}

    if not matches:
        raise MdevError('No group found for role %s' % upper_snake(role))

    return matches[max(matches, key=int)]


def add(args):
    login(args)

    if args.type == 'user':
        spinner.text = 'Adding user %s' % highlight(args.value)
        _add_user(args.value)
    elif args.type == 'group':
        spinner.text = 'Adding group %s' % highlight(args.value)
        _add_group(args.value)


def _add_user(username):
    post(config.get('api', 'rest1') + 'sys_sec_User',
         {'username': username,
          'password_': username,
          'Email': username + "@molgenis.org",
          'active': True})


def _add_group(name):
    post(config.get('api', 'group'), {'name': name, 'label': name})


def give(args):
    pass
