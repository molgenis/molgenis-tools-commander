"""
Alter settings
"""

import mcmd.config.config as config
from mcmd import io
from mcmd.client.molgenis_client import login, get, put
from mcmd.io import highlight
from mcmd.utils import McmdError


# =========
# Arguments
# =========

def arguments(subparsers):
    p_set = subparsers.add_parser('set',
                                  help='Alter settings',
                                  description="Run 'mcmd set -h' to view the help for this sub-command")

    p_set.add_argument('type',
                       type=str,
                       help="The type of setting (table extending from the sys_set_Settings table)")

    p_set.add_argument('setting',
                       type=str,
                       help="The attribute to set")

    p_set.add_argument('value',
                       type=str,
                       help="The value to set the attribute to")

    p_set.set_defaults(func=set,
                       write_to_history=True)


# =======
# Methods
# =======

def _get_settings():
    entity = 'sys_md_EntityType'
    query = 'q=extends==sys_set_settings&attrs=~id'
    molgenis_settings = _quick_get(entity, query)
    return [setting['id'] for setting in molgenis_settings]


def _get_settings_entity(setting):
    possible_settings = _get_settings()
    setting_entity = [set for set in possible_settings if (setting.lower() == set.lower() or
                                                           setting.lower() == set.lower().replace('sys_set_', '') or
                                                           setting.lower() == set.lower().replace('sys_set_',
                                                                                                  '').replace(
                'settings', ''))]
    if len(setting_entity) == 0:
        raise McmdError('Setting: [{}] is not a valid setting'.format(setting))
    else:
        return setting_entity[0]

def _quick_get(entity, q):
    rest = config.api('rest2')
    url = '{}{}?{}'.format(rest, entity, q)
    return get(url).json()['items']

def _get_row_id(entity):
    query = 'attrs=~id'
    settings = _quick_get(entity, query)
    return settings[0]['id']

@login
def set(args):
    entity = _get_settings_entity(args.type)
    io.start(
        'Updating {} of {} settings to {}'.format(highlight(args.setting), highlight(args.type), highlight(args.value)))
    row = _get_row_id(entity)
    url = '{}{}/{}/{}'.format(config.api('rest1'), entity, row, args.setting)
    put(url, args.value)