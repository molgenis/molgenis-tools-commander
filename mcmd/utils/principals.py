from enum import Enum

from mcmd.client.molgenis_client import get
from mcmd.config import config
from mcmd.io import multi_choice
from mcmd.logging import get_logger
from mcmd.utils.errors import McmdError

log = get_logger()


class PrincipalType(Enum):
    USER = 'user'
    ROLE = 'role'


def ensure_principal_exists(principal_name, principal_type):
    if not principal_exists(principal_name, principal_type):
        raise McmdError('No {} found with id {}'.format(principal_type.value, principal_name))


def principal_exists(principal_name, principal_type):
    if principal_type == PrincipalType.USER:
        return user_exists(principal_name)
    elif principal_type == PrincipalType.ROLE:
        return role_exists(principal_name)
    else:
        raise McmdError('Unknown principal type: %s' % principal_type)


def user_exists(username):
    log.debug('Checking if user %s exists' % username)
    response = get(config.api('rest2') + 'sys_sec_User?q=username==' + username)
    return int(response.json()['total']) > 0


def role_exists(rolename):
    log.debug('Checking if role %s exists' % rolename)
    response = get(config.api('rest2') + 'sys_sec_Role?q=name==' + rolename.upper())
    return int(response.json()['total']) > 0


def detect_principal_type(principal_name):
    results = dict()
    for principal_type in PrincipalType:
        if principal_exists(principal_name, principal_type):
            results[principal_type.value] = principal_name

    if len(results) == 0:
        raise McmdError('No principals found with name %s' % principal_name)
    elif len(results) > 1:
        choices = results.keys()
        answer = multi_choice('Multiple principals found with name %s. Choose one:' % principal_name, choices)
        return PrincipalType[answer.upper()]
    else:
        return PrincipalType[list(results)[0].upper()]
