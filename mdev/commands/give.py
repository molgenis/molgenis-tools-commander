from mdev import io
from mdev.client import login, grant, user_exists, PrincipalType, role_exists, principal_exists, resource_exists, \
    ResourceType
from mdev.io import multi_choice, highlight
from mdev.utils import MdevError


def give(args):
    login(args)

    # the PermissionManagerController always gives 200 OK so we need to validate everything ourselves
    resource_type = _get_resource_type(args)
    principal_type = _get_principal_type(args)
    io.start('Giving %s %s permission to %s on %s %s' % (principal_type.value,
                                                         highlight(args.receiver),
                                                         highlight(args.permission),
                                                         resource_type.get_label().lower(),
                                                         highlight(args.resource)))

    grant(principal_type, args.receiver, resource_type, args.resource, args.permission)


def _get_principal_type(args):
    if args.user:
        if not user_exists(args.receiver):
            raise MdevError('No user found with name %s' % args.receiver)
        return PrincipalType.USER
    elif args.role:
        if not role_exists(args.receiver):
            raise MdevError('No role found with name %s' % args.receiver)
        return PrincipalType.ROLE
    else:
        # No principal type specified, let's guess it
        results = dict()
        for principal_type in PrincipalType:
            if principal_exists(args.receiver, principal_type):
                results[principal_type.value] = args.receiver

        if len(results) == 0:
            raise MdevError('No principals found with name %s' % args.receiver)
        elif len(results) > 1:
            choices = results.keys()
            answer = multi_choice('Multiple principals found with name %s. Choose one:' % args.receiver, choices)
            return PrincipalType[answer.upper()]
        else:
            return PrincipalType[list(results)[0].upper()]


def _get_resource_type(args):
    if args.entity_type:
        if not resource_exists(args.resource, ResourceType.ENTITY_TYPE):
            raise MdevError('No Entity Type found with id %s' % args.resource)
        return ResourceType.ENTITY_TYPE
    elif args.package:
        if not resource_exists(args.resource, ResourceType.PACKAGE):
            raise MdevError('No Package found with id %s' % args.resource)
        return ResourceType.PACKAGE
    elif args.plugin:
        if not resource_exists(args.resource, ResourceType.PLUGIN):
            raise MdevError('No Plugin found with id %s' % args.resource)
        return ResourceType.PLUGIN
    else:
        # No resource type specified, let's guess it
        results = dict()
        for resource_type in ResourceType:
            if resource_exists(args.resource, resource_type):
                results[resource_type.get_label()] = args.resource

        if len(results) == 0:
            raise MdevError('No resources found with id %s' % args.resource)
        elif len(results) > 1:
            choices = results.keys()
            answer = multi_choice('Multiple resources found for id %s. Choose one:' % args.resource, choices)
            return ResourceType.of_label(answer)
        else:
            return ResourceType.of_label(list(results)[0])
