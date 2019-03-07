from typing import List

from mcmd.client.molgenis_client import ResourceType, resource_exists, PrincipalType, principal_exists
from mcmd.io import multi_choice
from mcmd.utils.errors import McmdError


def guess_resource_type(resource_id, types: List[ResourceType]):
    results = dict()
    for resource_type in types:
        if resource_exists(resource_id, resource_type):
            results[resource_type.get_label()] = resource_id

    if len(results) == 0:
        raise McmdError('No resources found with id %s' % resource_id)
    elif len(results) > 1:
        choices = results.keys()
        answer = multi_choice('Multiple resources found for id %s. Choose one:' % resource_id, choices)
        return ResourceType.of_label(answer)
    else:
        return ResourceType.of_label(list(results)[0])


def guess_principal_type(principal_name):
    results = dict()
    for principal_type in PrincipalType:
        if principal_exists(principal_name, principal_type):
            results[principal_type.value] = principal_name

    if len(results) == 0:
        raise McmdError('No principals found with name %s' % principal_name)
    elif len(results) > 1:
        choices = results.keys()
        answer = multi_choice('Multiple principals found with name %s. Choose one:' % principal_name, choices)
        return PrincipalType[answer.upper()]
    else:
        return PrincipalType[list(results)[0].upper()]
