import json

import requests

from mdev.configuration import get_config
from mdev.logging import get_logger
from mdev.utils import MdevError

config = get_config()
log = get_logger()
token = ''


def login(args):
    global token

    if args.as_user is None:
        username = config.get('auth', 'username')
    else:
        username = args.as_user[0]

    if args.with_password is None:
        if args.as_user is None:
            password = config.get('auth', 'password')
        else:
            password = args.as_user[0]
    else:
        password = args.with_password[0]

    login_url = config.get('api', 'login')

    log.debug('Logging in as user %s', username)

    response = post(login_url,
                    data={"username": username, "password": password})
    token = response.json()['token']


def get(url):
    return _handle_request(lambda: requests.get(url,
                                                headers=_get_default_headers()))


def post(url, data):
    return _handle_request(lambda: requests.post(url,
                                                 headers=_get_default_headers(),
                                                 data=json.dumps(data)))


def post_file(url, file_path, params):
    return _handle_request(lambda: requests.post(url,
                                                 headers={'x-molgenis-token': token},
                                                 files={'file': open(file_path, 'rb')},
                                                 params=params))


def _get_default_headers():
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['x-molgenis-token'] = token
    return headers


def _handle_request(request):
    response = str()
    try:
        response = request()
        response.raise_for_status()
        return response
    except requests.HTTPError as e:
        if 'application/json' in response.headers.get('Content-Type'):
            if 'errors' in response.json():
                for error in response.json()['errors']:
                    # TODO capture multiple error messages
                    raise MdevError(error['message'])
        raise MdevError(str(e))
    except requests.RequestException as e:
        raise MdevError(str(e))
