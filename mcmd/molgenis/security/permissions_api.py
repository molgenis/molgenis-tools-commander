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
    get_url = urljoin(api.permissions(),
                      'entity-{}/{}?q={}=={}'.format(entity_type_id, entity_id, principal_type.value, principal_name))
    existing_permissions = get(get_url).json()['data']['permissions']

    body = dict()
    if principal_type == PrincipalType.USER:
        body['user'] = principal_name
    elif principal_type == PrincipalType.ROLE:
        principal_name = to_role_name(principal_name)
        body['role'] = principal_name
    else:
        raise McmdError('Unknown principal type: %s' % principal_type)

    url = urljoin(api.permissions(), 'entity-{}/{}'.format(entity_type_id, entity_id))
    if permission.value == 'none':
        if len(existing_permissions) != 0:
            delete(url, data=body)
    else:
        body['permission'] = permission.value.upper()
        permissions = {'permissions': [body]}

        if len(existing_permissions) == 0:
            post(url, data=permissions)
        else:
            patch(url, data=permissions)
