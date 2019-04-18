from urllib.parse import urljoin

from mcmd.config import config
from mcmd.version.compatibility import version


def endpoint(func):
    def wrapper():
        return urljoin(config.get('host', 'selected'), func())

    return wrapper


@endpoint
def rest1():
    return 'api/v1/'


@endpoint
def rest2():
    return 'api/v2/'


@endpoint
def login():
    return 'api/v1/login/'


@endpoint
@version('7.0.0')
def group():
    return 'api/plugin/security/group/'


@endpoint
@version('8.0.0')
def group():
    return 'api/identities/v1/group/'


@endpoint
@version('7.0.0')
def member(group_name):
    return 'api/plugin/security/group/{}/member/'.format(group_name)


@endpoint
@version('8.0.0')
def member(group_name):
    return 'api/identities/v1/group/{}/member/'.format(group_name)


@endpoint
def import_():
    return 'plugin/importwizard/importFile/'


@endpoint
def import_by_url():
    return 'plugin/importwizard/importByUrl/'


@endpoint
def permissions():
    return 'menu/admin/permissionmanager/update/'


@endpoint
def rls():
    return 'menu/admin/permissionmanager/update/entityclass/rls'


@endpoint
def add_theme():
    return 'plugin/thememanager/add-bootstrap-theme'


@endpoint
def set_theme():
    return 'plugin/thememanager/set-bootstrap-theme'


@endpoint
def logo():
    return 'plugin/menumanager/upload-logo'
