"""
Alter settings
"""
import json

from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.errors import McmdError
from mcmd.io import io
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import get, put


# =========
# Arguments
# =========

@arguments('set')
def add_arguments(subparsers):
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
    row = _get_first_row_id(entity)
    url = api.rest1('{}/{}/{}'.format(entity, row, args.setting))
    put(url, json.dumps(args.value))


def _get_settings():
    molgenis_settings = get(api.rest2('sys_md_EntityType'),
                            params={
                                'q': 'extends==sys_set_settings',
                                'attrs': '~id'
                            }).json()['items']
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


def _get_first_row_id(entity):
    settings = get(api.rest2(entity),
                   params={
                       'attrs': '~id'
                   }).json()['items']
    return settings[0]['id']
