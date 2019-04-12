from urllib.parse import urljoin

from mcmd.config import config
from mcmd.utils.compatibility import version


def to_url(endpoint):
    url_ = config.get('host', 'selected')
    return urljoin(url_, endpoint)


def rest1():
    return to_url('api/v1/')


def rest2():
    return to_url('api/v2/')


def login():
    return to_url('api/v1/login/')


@version('7.0.0')
def group():
    return to_url('api/plugin/security/group/')


@version('8.0.0')
def group():
    return to_url('api/identities/v1/group/')


@version('7.0.0')
def member():
    return to_url('api/plugin/security/group/{}/member/')


@version('8.0.0')
def member():
    return to_url('api/identities/v1/group/{}/member/')


def import_():
    return to_url('plugin/importwizard/importFile/')


def import_url():
    return to_url('plugin/importwizard/importByUrl/')


def permissions():
    return to_url('menu/admin/permissionmanager/update/')


def rls():
    return to_url('menu/admin/permissionmanager/update/entityclass/rls')


def add_theme():
    return to_url('plugin/thememanager/add-bootstrap-theme')


def set_theme():
    return to_url('plugin/thememanager/set-bootstrap-theme')


def logo():
    return to_url('plugin/menumanager/upload-logo')
