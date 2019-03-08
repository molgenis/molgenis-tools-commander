from enum import Enum
from typing import List

from mcmd.client.molgenis_client import get
from mcmd.config import config
from mcmd.io import multi_choice
from mcmd.logging import get_logger
from mcmd.utils.errors import McmdError

log = get_logger()


class ResourceType(Enum):
    ENTITY_TYPE = ('sys_md_EntityType', 'entityclass', 'Entity Type')
    THEME = ('sys_set_StyleSheet', 'stylesheet', 'Stylesheet')
    PACKAGE = ('sys_md_Package', 'package', 'Package')
    PLUGIN = ('sys_Plugin', 'plugin', 'Plugin')
    GROUP = ('sys_sec_Group', 'group', 'Group')

    def get_entity_id(self):
        return self.value[0]

    def get_resource_name(self):
        return self.value[1]

    def get_label(self):
        return self.value[2]

    @classmethod
    def of_label(cls, label):
        return ResourceType[label.replace(' ', '_').upper()]


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


def resource_exists(resource_id, resource_type):
    log.debug('Checking if %s %s exists' % (resource_type.get_label(), resource_id))
    response = get(config.api('rest2') + resource_type.get_entity_id() + '?q=id==' + resource_id)
    return int(response.json()['total']) > 0


def one_resource_exists(resources, resource_type):
    log.debug('Checking if one of [{}] exists in [{}]'.format(','.join(resources), resource_type.get_label()))
    response = get(config.api('rest2') + resource_type.get_entity_id() + '?q=id=in=({})'.format(','.join(resources)))
    return int(response.json()['total']) > 0


def ensure_resource_exists(resource_id, resource_type):
    if not resource_exists(resource_id, resource_type):
        raise McmdError('No %s found with id %s' % (resource_type.get_label(), resource_id))
