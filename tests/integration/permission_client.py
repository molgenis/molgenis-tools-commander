import json
from urllib.parse import urljoin

import molgenis.client
import requests

from tests.integration.loader_mock import get_host
from tests.integration.utils import entity_is_empty, random_name, run_commander


def get_user_plugin_permissions(session, id_):
    return _get_permissions(session, 'plugin', 'user', id_)


def get_user_entity_permissions(session, id_):
    return _get_permissions(session, 'entityclass', 'user', id_)


def get_user_package_permissions(session, id_):
    return _get_permissions(session, 'package', 'user', id_)


def get_role_entity_permissions(session, id_):
    return _get_permissions(session, 'entityclass', 'role', id_)


def _get_permissions(session, resource_type, principal_type, id_):
    # noinspection PyProtectedMember
    headers = session._get_token_header()
    headers.update({"Content-Type": "application/json"})
    response = requests.get(urljoin(get_host()['url'],
                                    'menu/admin/permissionmanager/{}/{}/{}'.format(resource_type, principal_type, id_)),
                            headers=headers)
    permissions = json.loads(response.content)['permissions']
    return permissions


def entity_is_row_level_secured(admin_session, entity_id):
    """Workaround: there is no endpoint to check whether an entity is row level secured."""
    assert not entity_is_empty(admin_session, entity_id), "Need an entity with data to check RLS"

    name = random_name()
    run_commander('add user {}'.format(name))
    run_commander('give {} read {}'.format(name, entity_id))

    user_session = molgenis.client.Session(urljoin(get_host()['url'], '/api/'))
    user_session.login(name, name)
    return entity_is_empty(user_session, entity_id)
