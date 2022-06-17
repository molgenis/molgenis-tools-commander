"""
Alter values
"""
import json
import textwrap
from argparse import RawDescriptionHelpFormatter
from pathlib import Path

from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.context import context
from mcmd.core.errors import McmdError
from mcmd.in_out import in_out
from mcmd.in_out.in_out import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import get, put
from mcmd.utils import files


# =========
# Arguments
# =========


@arguments('set')
def add_arguments(subparsers):
    p_set = subparsers.add_parser('set',
                                  help='update a single entity value',
                                  formatter_class=RawDescriptionHelpFormatter,
                                  description=textwrap.dedent(
                                      """
                                      Updates a single value in any entity. When updating a settings entity it is not 
                                      needed to supply the row's identifier (with '--for').

                                      example usage:
                                        # Updating a value in a row:
                                        mcmd set my_patients name john --for patient_1
                                        
                                        # Updating a setting:
                                        mcmd set app title "My MOLGENIS"
                                        
                                        # Using the contents of a file as the value
                                        mcmd set app molgenis_menu --from-resource menu.json
                                        mcmd set app footer --from-path /my/path/footer.txt
                                      """
                                  ))

    p_set.add_argument('type',
                       type=str,
                       help="either 1) a simple name of a settings entity (app, mail, opencpu, auth, dataexplorer or "
                            "audit), "
                            "or 2) the ID of any entity type")

    p_set.add_argument('attribute',
                       type=str,
                       help="the attribute to set")

    p_set.add_argument('value',
                       type=str,
                       help="the value to set the attribute to")

    p_set_file = p_set.add_mutually_exclusive_group()
    p_set_file.add_argument('--from-resource', '-r',
                            action='store_true',
                            help='flag to specify that the value should come from the contents of the specified '
                                 'resource')
    p_set_file.add_argument('--from-path', '-p',
                            action='store_true',
                            help='flag to specify that the value should come from the contents of the specified '
                                 'absolute file path')

    p_set.add_argument('--for', '-i',
                       metavar='ENTITY ID',
                       type=str,
                       dest='for_',
                       help="The id of the row you want to alter")

    p_set.set_defaults(func=set_,
                       write_to_history=True)


# =======
# Globals
# =======


_SETTING_SYNONYMS = {
    'mail': 'sys_set_MailSettings',
    'opencpu': 'sys_set_OpenCpuSettings',
    'app': 'sys_set_app',
    'auth': 'sys_set_auth',
    'dataexplorer': 'sys_set_dataexplorer',
    'audit': 'sys_set_aud'
}


# =======
# Methods
# =======

@command
def set_(args):
    """
    set sets the specified row of the specified table (or setting of specified settings table) to the specified value
    :param args: command line arguments containing: the settings type, the setting to set, and the value to set it to,
    if not a setting also the --for (which row to alter)
    if --from-path or --from-resource is passed the value is assumed to be a file containing the value data to be set
    :return: None
    """
    value = args.value
    value_desc = highlight(value)

    if args.from_path:
        path = Path(args.value)
        value = files.read_file(path)
        value_desc = 'contents of {}'.format(highlight(args.value))
    elif args.from_resource:
        path = files.select_file_from_folders(context().get_resource_folders(), args.value)
        value = files.read_file(path)
        value_desc = 'contents of {}'.format(highlight(args.value))

    if args.for_:
        entity = args.type
        row = args.for_
        in_out.start(
            'Updating {} of {} for id {} to {}'.format(highlight(args.attribute), highlight(args.type),
                                                       highlight(args.for_), value_desc))
    else:
        entity = _get_settings_entity(args.type)
        in_out.start(
            'Updating {} of {} settings to {}'.format(highlight(args.attribute), highlight(args.type),
                                                      value_desc))
        row = _get_first_row_id(entity)

    url = api.rest1('{}/{}/{}'.format(entity, row, args.attribute))
    put(url, json.dumps(value))


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
            raise McmdError('Setting [{}] is not a valid settings entity. If you meant to alter'.format(setting) +
                            ' another table, please provide the --for option to specify the row to alter.')


def _get_first_row_id(entity):
    settings = get(api.rest2(entity),
                   params={
                       'attrs': '~id'
                   }).json()['items']
    return settings[0]['id']
