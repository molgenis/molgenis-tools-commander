from mcmd.core.compatibility import version
from mcmd.core.errors import McmdError
from mcmd.molgenis.principals import PrincipalType
from mcmd.molgenis.resources import ResourceType
from mcmd.molgenis.security import permission_manager, permissions_api
from mcmd.molgenis.security.permission import Permission
from mcmd.molgenis.version import get_version


@version('7.0.0')
def grant_permission(principal_type: PrincipalType,
                     principal_name: str,
                     resource_type: ResourceType,
                     entity_type_id: str,
                     permission: Permission):
    permission_manager.grant_permission(principal_type, principal_name, resource_type, entity_type_id, permission)


# noinspection PyUnusedLocal
@version('7.0.0')
def grant_row_permission(principal_type: PrincipalType,
                         principal_name: str,
                         entity_type_id: str,
                         entity_id: str,
                         permission: Permission):
    raise McmdError(
        "Giving row level security is only possible since MOLGENIS 8.1.1 (you are using {})".format(
            get_version()))


@version('8.1.1')
def grant_row_permission(principal_type: PrincipalType,
                         principal_name: str,
                         entity_type_id: str,
                         entity_id: str,
                         permission: Permission):
    permissions_api.grant_row_permission(principal_type, principal_name, entity_type_id, entity_id, permission)


@version('7.0.0')
def enable_row_level_security(entity_type_id: str):
    permission_manager.enable_row_level_security(entity_type_id)


@version('7.0.0')
def disable_row_level_security(entity_type_id: str):
    permission_manager.disable_row_level_security(entity_type_id)
