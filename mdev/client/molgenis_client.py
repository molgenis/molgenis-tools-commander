import json
from enum import Enum

import requests

from mdev import io
from mdev.config.config import get_config
from mdev.logging import get_logger
from mdev.utils import MdevError

config = get_config()
log = get_logger()
token = ''


class ResourceType(Enum):
    ENTITY_TYPE = ('sys_md_EntityType', 'entityclass', 'Entity Type')
    PACKAGE = ('sys_md_Package', 'package', 'Package')
    PLUGIN = ('sys_Plugin', 'plugin', 'Plugin')

    def get_entity_id(self):
        return self.value[0]

    def get_resource_name(self):
        return self.value[1]

    def get_label(self):
        return self.value[2]

    @classmethod
    def of_label(cls, label):
        return ResourceType[label.replace(' ', '_').upper()]


class PrincipalType(Enum):
    USER = 'user'
    ROLE = 'role'


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

    io.debug('Logging in as user %s' % username)

    response = post(login_url,
                    data={"username": username, "password": password})
    token = response.json()['token']


def get(url):
    return _handle_request(lambda: requests.get(url,
                                                headers=_get_default_headers()))


def grant(principal_type, principal_name, resource_type, identifier, permission):
    data = {'radio-' + identifier: permission}

    if principal_type == PrincipalType.USER:
        data['username'] = principal_name
    elif principal_type == PrincipalType.ROLE:
        data['rolename'] = principal_name.upper()
    else:
        raise MdevError('Unknown principal type: %s' % principal_type)

    url = config.get('api', 'perm') + resource_type.get_resource_name() + '/' + principal_type.value
    return _handle_request(lambda: requests.post(url,
                                                 headers={
                                                     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                                                     'x-molgenis-token': token},
                                                 data=data))


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
            response_json = response.json()
            if 'errors' in response_json:
                for error in response_json['errors']:
                    # TODO capture multiple error messages
                    raise MdevError(error['message'])
            elif 'errorMessage' in response_json:
                raise MdevError(response_json['errorMessage'])
        raise MdevError(str(e))
    except requests.RequestException as e:
        raise MdevError(str(e))


def resource_exists(resource_id, resource_type):
    log.debug('Checking if %s %s exists' % (resource_type.get_label(), resource_id))
    response = get(config.get('api', 'rest2') + resource_type.get_entity_id() + '?q=id==' + resource_id)
    return int(response.json()['total']) > 0


def principal_exists(principal_name, principal_type):
    if principal_type == PrincipalType.USER:
        return user_exists(principal_name)
    elif principal_type == PrincipalType.ROLE:
        return role_exists(principal_name)
    else:
        raise MdevError('Unknown principal type: %s' % principal_type)


def user_exists(username):
    log.debug('Checking if user %s exists' % username)
    response = get(config.get('api', 'rest2') + 'sys_sec_User?q=username==' + username)
    return int(response.json()['total']) > 0


def role_exists(rolename):
    log.debug('Checking if role %s exists' % rolename)
    response = get(config.get('api', 'rest2') + 'sys_sec_Role?q=name==' + rolename.upper())
    return int(response.json()['total']) > 0
