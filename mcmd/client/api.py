from urllib.parse import urljoin, quote

from mcmd.config import config


def endpoint(func):
    def wrapper(*args, **kwargs):
        return urljoin(config.get('host', 'selected'), quote(func(*args, **kwargs)))

    return wrapper


@endpoint
def rest1(path: str):
    return urljoin('api/v1/', path)


@endpoint
def rest2(path: str):
    return urljoin('api/v2/', path)


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
