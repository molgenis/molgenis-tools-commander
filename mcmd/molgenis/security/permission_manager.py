"""Client for the Permission Manager plugin of MOLGENIS (all versions)."""

from urllib.parse import urljoin

from mcmd.core.errors import McmdError
from mcmd.molgenis import api
from mcmd.molgenis.client import post_form, post
from mcmd.molgenis.principals import PrincipalType, to_role_name
from mcmd.molgenis.resources import ResourceType
from mcmd.molgenis.security.permission import Permission


def grant_permission(principal_type: PrincipalType,
                     principal_name: str,
                     resource_type: ResourceType,
                     entity_type_id: str,
                     permission: Permission):
    data = {'radio-' + entity_type_id: permission.value}

    if principal_type == PrincipalType.USER:
        data['username'] = principal_name
    elif principal_type == PrincipalType.ROLE:
        principal_name = to_role_name(principal_name)
        data['rolename'] = principal_name
    else:
        raise McmdError('Unknown principal type: %s' % principal_type)

    url = urljoin(api.permission_manager_permissions(),
                  '{}/{}'.format(resource_type.get_resource_name(), principal_type.value))
    post_form(url, data)


def enable_row_level_security(entity_type_id: str):
    post(api.permission_manager_rls(), data={'id': entity_type_id,
                                             'rlsEnabled': True})


def disable_row_level_security(entity_type_id: str):
    post(api.permission_manager_rls(), data={'id': entity_type_id,
                                             'rlsEnabled': False})
