import json

import requests

from mdev.configuration import get_config
from mdev.logging import get_logger
from mdev.utils import lower_kebab

log = get_logger()
config = get_config()
token = ''


def import_(args):
    log.info('Importing %s', args.file)


def make(args):
    _login()
    group_name = _find_group(args.role)

    log.info('Making user %s a member of role %s', args.user, args.role.upper())
    url = config.get('api', 'member') % group_name
    _post(url, {'username': args.user, 'roleName': args.role.upper()})


def _find_group(role):
    log.debug('Fetching groups')
    groups = _get(config.get('api', 'rest2') + 'sys_sec_Group?attrs=name')

    matches = dict()
    for group in groups.json()['items']:
        group_name = group['name']
        if lower_kebab(role).startswith(group_name):
            matches[len(group_name)] = group_name
    if not matches:
        log.error('No group found for role %s', role.upper())
        exit(1)

    return matches[max(matches, key=int)]


def add(args):
    _login()

    if args.type == 'user':
        _add_user(args.value)
    elif args.type == 'group':
        _add_group(args.value)
    else:
        raise ValueError('invalid choice for add: %s', args.type)


def _add_user(username):
    log.info('Adding user %s', username)
    _post(config.get('api', 'rest1') + 'sys_sec_User',
          {'username': username,
           'password_': username,
           'Email': username + "@molgenis.org",
           'active': True})


def _add_group(name):
    log.info('Adding group %s', name)
    _post(config.get('api', 'group'), {'name': name, 'label': name})


def run(args):
    print("run", args)


def _login():
    global token

    login_url = config.get('api', 'login')
    username = config.get('auth', 'username')
    password = config.get('auth', 'password')

    log.debug('Logging in as user %s', username)
    try:
        response = requests.post(login_url,
                                 data=json.dumps({"username": username, "password": password}),
                                 headers={"Content-Type": "application/json"})
        response.raise_for_status()
        token = response.json()['token']
    except requests.RequestException as e:
        log.error(e)
        exit(1)


def _get(url):
    response = str()
    try:
        response = requests.get(url,
                                headers={'Content-Type': 'application/json',
                                         'x-molgenis-token': token})
        response.raise_for_status()
        return response
    except requests.HTTPError:
        for error in response.json()['errors']:
            log.error(error['message'])
        exit(1)
    except requests.RequestException as e:
        log.error(e)
        exit(1)


def _post(url, data):
    response = str()
    try:
        response = requests.post(url,
                                 headers={'Content-Type': 'application/json',
                                          'x-molgenis-token': token},
                                 data=json.dumps(data))
        response.raise_for_status()
    except requests.HTTPError as e:
        if 'application/json' in response.headers.get('Content-Type'):
            if 'errors' in response.json():
                for error in response.json()['errors']:
                    log.error(error['message'])
                exit(1)
        log.error(e)
        exit(1)
    except requests.RequestException as e:
        log.error(e)
        exit(1)
