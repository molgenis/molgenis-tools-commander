from typing import Optional
from urllib.parse import urljoin

import requests

from tests.integration.loader_mock import get_host


def get_user_plugin_permission(session, plugin, user) -> Optional[str]:
    return _get_permission(session, 'plugin', plugin, 'user', user)


def get_user_entity_type_permission(session, entity_type, user) -> Optional[str]:
    return _get_permission(session, 'entityType', entity_type, 'user', user)


def get_user_package_permission(session, package, user) -> Optional[str]:
    return _get_permission(session, 'package', package, 'user', user)


def get_role_entity_type_permission(session, entity_type, role) -> Optional[str]:
    return _get_permission(session, 'entityType', entity_type, 'role', role)


def get_user_entity_permission(session, entity_type, entity, user) -> Optional[str]:
    return _get_permission(session, 'entity-' + entity_type, entity, 'user', user)


def get_role_entity_permission(session, entity_type, entity, role) -> Optional[str]:
    return _get_permission(session, 'entity-' + entity_type, entity, 'role', role)


def _get_permission(session, type_id, object_id, principal_type, principal) -> Optional[str]:
    headers = _configure_headers(session)
    response = requests.get(urljoin(get_host()['url'],
                                    'api/permissions/{}/{}?q={}=={}'.format(type_id,
                                                                            object_id,
                                                                            principal_type,
                                                                            principal)),
                            headers=headers)
    permissions = response.json()['data']['permissions']
    if len(permissions) == 0:
        return None
    else:
        return permissions[0]['permission']


def entity_is_row_level_secured(admin_session, entity_type_id: str):
    headers = _configure_headers(admin_session)
    response = requests.get(urljoin(get_host()['url'], 'api/permissions/types'),
                            headers=headers)

    types = response.json()['data']
    entity_type_ids = [t['entityType'] for t in types]
    return entity_type_id in entity_type_ids


def _configure_headers(session):
    # noinspection PyProtectedMember
    headers = session._get_token_header()
    headers.update({"Content-Type": "application/json"})
    return headers
