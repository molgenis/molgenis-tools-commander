"""
Alter settings
"""
import json

import mcmd.config.config as config
from mcmd import io
from mcmd.commands._registry import arguments
from mcmd.client.molgenis_client import get, put
from mcmd.command import command
from mcmd.io import highlight
from mcmd.utils.errors import McmdError


# =========
# Arguments
# =========

@arguments('set')
def arguments(subparsers):
    p_set = subparsers.add_parser('set',
                                  help='Alter settings',
                                  description="Run 'mcmd set -h' to view the help for this sub-command")

    p_set.add_argument('type',
                       type=str,
                       help="Simple name of the settings entity (app, mail, opencpu, etc.) or the ID")

    p_set.add_argument('setting',
                       type=str,
                       help="The attribute to set")

    p_set.add_argument('value',
                       type=str,
                       help="The value to set the attribute to")

    p_set.set_defaults(func=set_,
                       write_to_history=True)


# =======
# Globals
# =======


_SETTING_SYNONYMS = {'mail': 'sys_set_MailSettings',
                     'opencpu': 'sys_set_OpenCpuSettings',
                     'app': 'sys_set_app',
                     'auth': 'sys_set_auth',
                     'dataexplorer': 'sys_set_dataexplorer'
                     }


# =======
# Methods
# =======

@command
def set_(args):
    """
    set sets the given setting of the given settings type to the given value
    :param args: command line arguments containing: the settings type, the setting to set, and the value to set it to
    :return: None
    """
    entity = _get_settings_entity(args.type)
    io.start(
        'Updating {} of {} settings to {}'.format(highlight(args.setting), highlight(args.type), highlight(args.value)))
    row = _get_row_id(entity)
    url = '{}{}/{}/{}'.format(config.api('rest1'), entity, row, args.setting)
    put(url, json.dumps(args.value))


def _get_settings():
    entity = 'sys_md_EntityType'
    query = 'q=extends==sys_set_settings&attrs=~id'
    molgenis_settings = _quick_get(entity, query)
    return [setting['id'] for setting in molgenis_settings]


def _get_settings_entity(setting):
    if setting.lower() in _SETTING_SYNONYMS:
        return _SETTING_SYNONYMS[setting.lower()]
    else:
        possible_settings = _get_settings()
        settings_entity = [selected_setting for selected_setting in possible_settings if
                           setting.lower() == selected_setting.lower()]
        if len(settings_entity) == 1:
            return settings_entity[0]
        else:
            raise McmdError('Setting [{}] is not a valid settings entity'.format(setting))


def _quick_get(entity, q):
    rest = config.api('rest2')
    url = '{}{}?{}'.format(rest, entity, q)
    return get(url).json()['items']


def _get_row_id(entity):
    query = 'attrs=~id'
    settings = _quick_get(entity, query)
    return settings[0]['id']
