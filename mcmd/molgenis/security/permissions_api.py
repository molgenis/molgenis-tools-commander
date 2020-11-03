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
    existing_permissions = _get_existing_permissions(entity_type_id, entity_id, principal_type, principal_name)

    if permission == Permission.NONE:
        if len(existing_permissions) != 0:
            _delete_permission(entity_type_id, entity_id, principal_type, principal_name)
    else:
        if len(existing_permissions) == 0:
            _add_permission(entity_type_id, entity_id, principal_type, principal_name, permission)
        else:
            _update_permission(entity_type_id, entity_id, principal_type, principal_name, permission)


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
