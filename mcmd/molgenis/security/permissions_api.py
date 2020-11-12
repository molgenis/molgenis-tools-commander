"""Client for the Permission API of MOLGENIS 8.1.1 and up."""
from urllib.parse import urljoin

from mcmd.core.errors import McmdError
from mcmd.molgenis import api
from mcmd.molgenis.client import get, delete, post, patch
from mcmd.molgenis.principals import PrincipalType, to_role_name
from mcmd.molgenis.security.permission import Permission


def grant_row_permission(principal_type: PrincipalType,
                         principal_name: str,
                         entity_type_id: str,
                         entity_id: str,
                         permission: Permission):
    """Grants a permission on one row to one principal."""

    existing_permissions = _get_existing_permissions(entity_type_id, entity_id, principal_type, principal_name)

    if permission == Permission.NONE:
        if len(existing_permissions) != 0:
            _delete_permission(entity_type_id, entity_id, principal_type, principal_name)
    else:
        if len(existing_permissions) == 0:
            _add_permission(entity_type_id, entity_id, principal_type, principal_name, permission)
        else:
            _update_permission(entity_type_id, entity_id, principal_type, principal_name, permission)


def get_user_plugin_permission(plugin: str, user: str) -> Permission:
    """Gets the permission for a user on a plugin."""
    return _get_permission('plugin', plugin, PrincipalType.USER, user)


def get_role_plugin_permission(plugin: str, role: str) -> Permission:
    """Gets the permission for a role on a plugin."""
    return _get_permission('plugin', plugin, PrincipalType.ROLE, role)


def get_user_entity_type_permission(entity_type: str, user: str) -> Permission:
    """Gets the permission for a user on an entity type."""
    return _get_permission('entityType', entity_type, PrincipalType.USER, user)


def get_role_entity_type_permission(entity_type: str, role: str) -> Permission:
    """Gets the permission for a role on an entity type."""
    return _get_permission('entityType', entity_type, PrincipalType.ROLE, role)


def get_user_package_permission(package: str, user: str) -> Permission:
    """Gets the permission for a user on a package."""
    return _get_permission('package', package, PrincipalType.USER, user)


def get_role_package_permission(package: str, role: str) -> Permission:
    """Gets the permission for a role on a package."""
    return _get_permission('package', package, PrincipalType.ROLE, role)


def get_user_entity_permission(entity_type: str, entity: str, user: str) -> Permission:
    """Gets the permission for a user on an entity."""
    return _get_permission('entity-' + entity_type, entity, PrincipalType.USER, user)


def get_role_entity_permission(entity_type: str, entity: str, role: str) -> Permission:
    """Gets the permission for a role on an entity."""
    return _get_permission('entity-' + entity_type, entity, PrincipalType.ROLE, role)


def is_row_level_secured(entity_type_id: str) -> bool:
    """Returns whether the entity type is row level secured or not."""

    response = get(urljoin(api.permissions(), 'types'))
    types = response.json()['data']
    entity_type_ids = [t['entityType'] for t in types]
    return entity_type_id in entity_type_ids


def _get_permission(type_id: str, object_id: str, principal_type: PrincipalType, principal: str) -> Permission:
    url = urljoin(api.permissions(), '{}/{}?q={}=={}'.format(type_id,
                                                             object_id,
                                                             principal_type.value,
                                                             principal))
    permissions = get(url).json()['data']['permissions']
    if len(permissions) == 0:
        return Permission.NONE
    else:
        return Permission[permissions[0]['permission']]


def _get_existing_permissions(entity_type_id: str, entity_id: str, principal_type: PrincipalType, principal_name: str):
    get_url = urljoin(api.permissions(),
                      'entity-{}/{}?q={}=={}'.format(entity_type_id, entity_id, principal_type.value, principal_name))
    existing_permissions = get(get_url).json()['data']['permissions']
    return existing_permissions


def _delete_permission(entity_type_id: str, entity_id: str, principal_type: PrincipalType, principal_name: str):
    url = _get_entity_url(entity_type_id, entity_id)
    body = _get_principal_body(principal_type, principal_name)
    delete(url, data=body)


def _add_permission(entity_type_id: str,
                    entity_id: str,
                    principal_type: PrincipalType,
                    principal_name: str,
                    permission: Permission):
    url = _get_entity_url(entity_type_id, entity_id)
    body = _get_principal_body(principal_type, principal_name)

    body['permission'] = permission.value.upper()
    post(url, data={'permissions': [body]})


def _update_permission(entity_type_id: str,
                       entity_id: str,
                       principal_type: PrincipalType,
                       principal_name: str,
                       permission: Permission):
    url = _get_entity_url(entity_type_id, entity_id)
    body = _get_principal_body(principal_type, principal_name)

    body['permission'] = permission.value.upper()
    patch(url, data={'permissions': [body]})


def _get_entity_url(entity_type_id: str, entity_id: str) -> str:
    return urljoin(api.permissions(), 'entity-{}/{}'.format(entity_type_id, entity_id))


def _get_principal_body(principal_type: PrincipalType, principal_name: str) -> dict:
    body = dict()
    if principal_type == PrincipalType.USER:
        body['user'] = principal_name
    elif principal_type == PrincipalType.ROLE:
        principal_name = to_role_name(principal_name)
        body['role'] = principal_name
    else:
        raise McmdError('Unknown principal type: %s' % principal_type)
    return body
