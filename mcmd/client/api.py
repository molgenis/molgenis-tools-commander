from urllib.parse import urljoin

from mcmd.config import config


def endpoint(func):
    def wrapper(*args, **kwargs):
        return urljoin(config.get('host', 'selected'), func(*args, **kwargs))

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
def group():
    return 'api/plugin/security/group/'


@endpoint
def member(group_name):
    return 'api/plugin/security/group/{}/member/'.format(group_name)


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
