from pathlib import Path
from urllib.parse import urljoin

import polling
from halo import Halo

from mdev.configuration import get_config
from mdev.logging import get_logger
from mdev.requests import login, get, post, post_file
from mdev.utils import lower_kebab, config_string_to_paths

log = get_logger()
config = get_config()


def import_(args):
    login()

    target_path = Path(args.file)

    if target_path.is_file():
        # TODO importing from an absolute path
        log.warn('Importing from an absolute path')
        exit(1)
    elif Path.cwd().joinpath(target_path).is_file():
        # TODO importing from current directory
        log.warn('Importing from the current directory')
        exit(1)
    else:
        files = _scan_folders_for_files(_get_molgenis_folders() + _get_quick_folders())

        if target_path.stem in files:
            file = files[target_path.stem]
            spinner = Halo(text='Importing %s' % file.name, spinner='dots')
            spinner.start()
            response = post_file(config.get('api', 'import'), file, {'action': config.get('set', 'import_action')})
            import_run_url = urljoin(config.get('api', 'host'), response.text)
            status, message = _poll_for_completion(import_run_url)
            if status == 'FAILED':
                spinner.fail()
                log.error(message)
            else:
                spinner.succeed()
        else:
            log.error('No file found for %s', target_path.stem)
            exit(1)


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
        log.warn('Molgenis git paths not configured. Edit the mdev.ini file to include the test data.')
        return list()
    else:
        return config_string_to_paths(config.get('data', 'git_paths'))


def _get_quick_folders():
    if not config.has_option('data', 'quick_folders'):
        return list()
    else:
        return config_string_to_paths(config.get('data', 'quick_folders'))


def make(args):
    login()
    group_name = _find_group(args.role)

    log.info('Making user %s a member of role %s', args.user, args.role.upper())
    url = config.get('api', 'member') % group_name
    post(url, {'username': args.user, 'roleName': args.role.upper()})


def _find_group(role):
    log.debug('Fetching groups')
    groups = get(config.get('api', 'rest2') + 'sys_sec_Group?attrs=name')
    role = lower_kebab(role)

    matches = {len(group['name']): group['name'] for group in groups.json()['items'] if role.startswith(group['name'])}

    if not matches:
        log.error('No group found for role %s', role.upper())
        exit(1)

    return matches[max(matches, key=int)]


def add(args):
    login()

    if args.type == 'user':
        _add_user(args.value)
    elif args.type == 'group':
        _add_group(args.value)
    else:
        raise ValueError('invalid choice for add: %s', args.type)


def _add_user(username):
    log.info('Adding user %s', username)

    post(config.get('api', 'rest1') + 'sys_sec_User',
         {'username': username,
          'password_': username,
          'Email': username + "@molgenis.org",
          'active': True})


def _add_group(name):
    log.info('Adding group %s', name)
    post(config.get('api', 'group'), {'name': name, 'label': name})


def run(args):
    print("run", args)
