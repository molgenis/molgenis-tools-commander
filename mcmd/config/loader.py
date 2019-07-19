"""
Loads the configuration and handles the addition of new properties.

Some properties require user input (the username and password of the host for example), while others don't (the
API endpoints). New properties should always be added to the 'defaults.yaml' file. Properties that also require user
input can define a custom configurer in this module that will help the user on the CLI instead of letting them edit
the property file directly.
"""

from collections import OrderedDict

import pkg_resources
from ruamel.yaml import YAML

import mcmd.config.config as config
import mcmd.io.io
from mcmd.core.home import get_properties_file
from mcmd.io.io import highlight

_DEFAULT_PROPERTIES = pkg_resources.resource_stream('mcmd.config', 'defaults.yaml')


def property_configurers():
    return {
        'git': _configure_git_root,
        'host': _configure_host
    }


def load_config():
    yaml = YAML()
    default_config = yaml.load(_DEFAULT_PROPERTIES)

    if _is_install_required():
        _install(default_config)

    user_config = yaml.load(get_properties_file())

    if _is_upgrade_required(user_config):
        _upgrade(default_config, user_config)

    # merge the configs so that new properties and list items are added
    _merge(default_config, user_config)

    # pass result to the config module and save to disk
    config.set_config(default_config, get_properties_file())


def _upgrade(default_config, user_config):
    mcmd.io.io.info("Some properties haven't been configured yet. Let's take a moment to fix that.")
    mcmd.io.io.newline()

    for prop, configurer in property_configurers().items():
        if prop not in user_config:
            configurer(default_config)

    config.set_config(default_config, get_properties_file())

    mcmd.io.io.newline()
    mcmd.io.io.info(
        'The configuration file has been updated succesfully ({})'.format(highlight(str(get_properties_file()))))
    exit(0)


def _install(default_config):
    mcmd.io.io.info("Looks like this is your first time running {}!\n  "
                 "Let's take a moment to set things up. It's OK to leave some fields empty, you can always change "
                 "them later.".format(highlight("Molgenis Commander")))
    mcmd.io.io.newline()

    for configurer in property_configurers().values():
        configurer(default_config)

    config.set_config(default_config, get_properties_file())

    mcmd.io.io.newline()
    mcmd.io.io.info('The configuration file has been created at {}'.format(highlight(str(get_properties_file()))))
    exit(0)


def _configure_git_root(config_):
    git_root = mcmd.io.io.input_(
        'Enter the absolute path to your Molgenis git folder (e.g. /Users/me/git/molgenis/)')
    if len(git_root) > 0:
        config_['git']['root'] = git_root


def _configure_host(values):
    _configure_url(values)
    _configure_username(values)
    _configure_password(values)


def _configure_url(values):
    host = mcmd.io.io.input_('Enter the host name of your Molgenis (Default: http://localhost:8080/)')
    if len(host) > 0:
        values['host']['selected'] = host
        values['host']['auth'][0]['url'] = host


def _configure_username(values):
    username = mcmd.io.io.input_('Enter the username of the super user (Default: admin)')
    if len(username) > 0:
        values['host']['auth'][0]['username'] = username


def _configure_password(values):
    password = mcmd.io.io.password('Enter the password of the super user (Leave blank to use command line authentication)')
    if len(password) > 0:
        values['host']['auth'][0]['password'] = password


def _is_install_required():
    return not get_properties_file().exists() or get_properties_file().stat().st_size == 0


def _is_upgrade_required(user_config):
    for prop in property_configurers().keys():
        if prop not in user_config:
            return True
    return False


def _merge(yaml_a, yaml_b):
    """Recursively merge YAML B into YAML A.

    Lists will be combined. Values in YAML B will overwrite values in YAML A.
    """
    for key, section in yaml_b.items():
        if isinstance(section, OrderedDict):
            if key not in yaml_a:
                yaml_a[key] = dict()
            _merge(yaml_a[key], yaml_b[key])
        elif isinstance(section, list):
            if key not in yaml_a:
                yaml_a[key] = list()
            if _is_list_of_objects(section):
                yaml_a[key] = _combine_object_lists(yaml_a[key], section)
            else:
                yaml_a[key] = _combine_lists(yaml_a[key], section)
        else:
            yaml_a[key] = yaml_b[key]


def _combine_object_lists(list_a, list_b):
    """Combines lists of objects by ID."""
    items_by_id_a = {_get_object_id(item): item for item in list_a}
    items_by_id_b = {_get_object_id(item): item for item in list_b}
    items_by_id_a.update(items_by_id_b)
    return [items_by_id_a[key] for key in sorted(items_by_id_a.keys())]


def _get_object_id(ordered_dict):
    """
    Gets the first value of the ordered dict (that represents a YAML object).
    ruamel.YAML uses a CommentedMapValuesView as OrderedDict which doesn't support indexing, so we iterate.
    """
    return next(iter(ordered_dict.values()))


def _combine_lists(list_a, list_b):
    combined_list = list_a
    combined_list.extend(x for x in list_b if x not in list_a)
    return combined_list


def _is_list_of_objects(list_section):
    return len(list_section) > 0 and isinstance(list_section[0], OrderedDict)
