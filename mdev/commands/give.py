"""
Give a principal (a user or a group) some permission on a resource (a package, entity type or plugin). Unless specified
by the user, the give command will try to figure out the principal- and resource types itself. If a resource or
principal doesn't exist, the program will terminate.
"""

from mdev import io
from mdev.client import login, grant, user_exists, PrincipalType, role_exists, principal_exists, resource_exists, \
    ResourceType
from mdev.io import multi_choice, highlight
from mdev.utils import MdevError


def give(args):
    login(args)

    # The PermissionManagerController always gives 200 OK so we need to validate everything ourselves
    resource_type = _get_resource_type(args)
    principal_type = _get_principal_type(args)
    io.start('Giving %s %s permission to %s on %s %s' % (principal_type.value,
                                                         highlight(args.receiver),
                                                         highlight(args.permission),
                                                         resource_type.get_label().lower(),
                                                         highlight(args.resource)))

    grant(principal_type, args.receiver, resource_type, args.resource, args.permission)


def _get_principal_type(args):
    principal_name = args.receiver
    if args.user:
        if not user_exists(principal_name):
            raise MdevError('No user found with name %s' % principal_name)
        return PrincipalType.USER
    elif args.role:
        if not role_exists(principal_name):
            raise MdevError('No role found with name %s' % principal_name)
        return PrincipalType.ROLE
    else:
        # No principal type specified, let's guess it
        results = dict()
        for principal_type in PrincipalType:
            if principal_exists(principal_name, principal_type):
                results[principal_type.value] = principal_name

        if len(results) == 0:
            raise MdevError('No principals found with name %s' % principal_name)
        elif len(results) > 1:
            choices = results.keys()
            answer = multi_choice('Multiple principals found with name %s. Choose one:' % principal_name, choices)
            return PrincipalType[answer.upper()]
        else:
            return PrincipalType[list(results)[0].upper()]


def _get_resource_type(args):
    resource_id = args.resource
    if args.entity_type:
        if not resource_exists(resource_id, ResourceType.ENTITY_TYPE):
            raise MdevError('No Entity Type found with id %s' % resource_id)
        return ResourceType.ENTITY_TYPE
    elif args.package:
        if not resource_exists(resource_id, ResourceType.PACKAGE):
            raise MdevError('No Package found with id %s' % resource_id)
        return ResourceType.PACKAGE
    elif args.plugin:
        if not resource_exists(resource_id, ResourceType.PLUGIN):
            raise MdevError('No Plugin found with id %s' % resource_id)
        return ResourceType.PLUGIN
    else:
        # No resource type specified, let's guess it
        results = dict()
        for resource_type in ResourceType:
            if resource_exists(resource_id, resource_type):
                results[resource_type.get_label()] = resource_id

        if len(results) == 0:
            raise MdevError('No resources found with id %s' % resource_id)
        elif len(results) > 1:
            choices = results.keys()
            answer = multi_choice('Multiple resources found for id %s. Choose one:' % resource_id, choices)
            return ResourceType.of_label(answer)
        else:
            return ResourceType.of_label(list(results)[0])
