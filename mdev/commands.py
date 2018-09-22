import re
from pathlib import Path
from urllib.parse import urljoin

import polling
import requests
# PyGithub's package is called github which throws off PyCharm
# noinspection PyPackageRequirements
from github import Github, UnknownObjectException

from mdev import history as hist
from mdev import io
from mdev.client import login, get, post, post_file
from mdev.configuration import get_config
from mdev.logging import get_logger
from mdev.io import highlight
from mdev.utils import lower_kebab, config_string_to_paths, MdevError, upper_snake

log = get_logger()
config = get_config()


def import_(args):
    if args.from_path:
        io.start('Importing from path %s' % highlight(args.file))
        login(args)
        file = Path(args.file)
        if not file.is_file():
            raise MdevError("File %s doesn't exist" % str(file.resolve()))

        _do_import(args.file)
    elif args.from_issue:
        io.start('Importing from GitHub issue %s' % highlight('#' + args.file))
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

        files = {'/'.join(link.rsplit('/', 2)[-2:]): link for link in file_links}

        if len(files) > 1:
            io.multi_choice(question='Issue #%s contains multiple files. Pick one:' % issue_num,
                            choices=files.keys())

        for link in file_links:
            name = link.rsplit('/', 2)[-2]
            r = requests.get(file_links[0])
            open(name, 'wb').write(r.content)

        exit(1)

    else:
        file_name = args.file
        io.start('Importing %s' % highlight(file_name))
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
        io.info('Molgenis git paths not configured. Edit the mdev.ini file to include the test data.')
        return list()
    else:
        return config_string_to_paths(config.get('data', 'git_paths'))


def _get_quick_folders():
    if not config.has_option('data', 'quick_folders'):
        return list()
    else:
        return config_string_to_paths(config.get('data', 'quick_folders'))


def make(args):
    io.start('Making user %s a member of role %s' % (highlight(args.user), highlight(args.role.upper())))
    login(args)

    group_name = _find_group(args.role)

    url = config.get('api', 'member') % group_name
    post(url, {'username': args.user, 'roleName': args.role.upper()})


def _find_group(role):
    io.debug('Fetching groups')
    groups = get(config.get('api', 'rest2') + 'sys_sec_Group?attrs=name')
    role = lower_kebab(role)

    matches = {len(group['name']): group['name'] for group in groups.json()['items'] if role.startswith(group['name'])}

    if not matches:
        raise MdevError('No group found for role %s' % upper_snake(role))

    return matches[max(matches, key=int)]


def add(args):
    if args.type == 'user':
        io.start('Adding user %s' % highlight(args.value))
        login(args)
        _add_user(args.value)
    elif args.type == 'group':
        io.start('Adding group %s' % highlight(args.value))
        login(args)
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
    io.start('Giving %s permission to %s on %s' % (highlight(args.receiver),
                                                   highlight(args.permission),
                                                   highlight(args.resource)))

    if args.entity_type:
        io.warn('entity type')
    elif args.package:
        io.warn('package')
    elif args.plugin:
        io.warn('plugin')
    else:
        login(args)
        entity_type = get(config.get('api', 'rest2') + 'sys_md_EntityType?q=id==%s' % args.resource).json()[
                          'total'] == 1
        package = get(config.get('api', 'rest2') + 'sys_md_Package?q=id==%s' % args.resource).json()['total'] == 1
        plugin = get(config.get('api', 'rest2') + 'sys_Plugin?q=id==%s' % args.resource).json()['total'] == 1


def history(args):
    if args.clear:
        io.start('Clearing history')
        hist.clear()
    else:
        lines = hist.read(args.number)
        if len(lines) == 0:
            log.warn('History is empty.')
        for line in lines:
            log.info(line)
