"""Update given attribute of given row from given entityType with given value"""
from mdev import io
from mdev.client.molgenis_client import put, login, resource_exists, ResourceType
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError, file_to_string, string_to_json
from pathlib import Path

config = get_config()


def update(args):
    """
    update
    :param args: commandline arguments containing information needed to update items
    :return: None
    :exception MdevError:   1) when a specified entityType does not exist
                            2) when a commandline argument is missing
                            3) when an invalid combination of commandline arguments are used
                            4) when a function is not yet implemented (update entityType)
    """
    login(args)

    if not resource_exists(args.entityType, ResourceType.ENTITY_TYPE):
        raise MdevError("Entity type {} doesn't exist".format(args.entityType))

    if args.rows:
        if args.attribute or args.row or args.to:
            raise MdevError(
                'Invalid input: the [{}] option cannot be combined with the following options: [{}], [{}], and [{}]'
                    .format('rows', 'attribute', 'row', 'to'))
        else:
            _update_rows(args)

    elif args.attribute:
        if not args.row or not args.to:
            _raise_missing_error(['[entityType]', '[attribute]', '[row]', 'value'], 'n [attribute]')
        else:
            _update_value(args)

    elif args.row:
        if not args.to:
            _raise_missing_error(['[entityType]', '[row]', 'value'], ' [row]')
        else:
            _update_row(args)

    else:
        raise MdevError("Updating entity type not yet implemented")


def _update_row(args):
    """
    _update_row updates one row using the update_rows function
    :param args: commandline arguments containing the entityType to update and the data to update it to
    :return: None
    """
    value = args.to
    io.start('Updating row of entity type: {} to {}'.format(highlight(args.entityType), highlight(value)))
    args.rows = '[{}]'.format(value)
    _update_rows(args, False)


def _update_rows(args, rows=True):
    """
    _update_rows updates specified rows of a specified entityType doing a put request
    :param args: commandline arguments containing the entityType to update and the rows to update it with
    :param rows: whether the function is called because the --rows parameter is specified or not (default True)
    :return: None
    """
    # If --rows was used, tell the user what happens and check if the input is a file containing json or json itself
    if rows:
        io.start('Updating rows for entity type: {}'.format(highlight(args.entityType)))

        file = Path(args.rows)
        # Check if commandline argument is a file
        if file.is_file():
            content = file_to_string(args.rows)

        # If argument is not a file, it should be json
        else:
            # TODO: Work with the quick paths
            content = args.rows
    # The --to option was used to specify the update data and can only be json
    else:
        content = args.rows
    json_structure = string_to_json(content)
    data = {'entities': json_structure}
    url = '{}{}'.format(config.get('api', 'rest2'), args.entityType)
    put(url, data)


def _raise_missing_error(missing_values, item):
    """
    _raise_missing_error raises an error when called telling which commandline arguments are missing
    :param missing_values: the missing commandline arguments
    :param item: the item it tries to update
    :return: None
    :exception MdevError: always because that is the purpose of this function
    """
    msg = 'Missing required argument(s). To [{}] a{}, you should specify: '.format('update', item)
    rules = ['the {} to update'.format(value) for value in missing_values]
    msg += ', and '.join(rules)
    msg += ' [to]'
    raise MdevError(msg)


def _update_value(args):
    """
    _update_value updates one attribute of one row of one table with a specified value doing a put request
    :param args: commandline arguments containing the entityType to update, the attribute to update, the row to
                update and the value to update it with
    :return: None
    """
    attr = args.attribute
    row = args.row
    entity_type = args.entityType
    value = args.to

    io.start('Updating attribute: {} of row with id: {} of entity type: {} to value: {}'.format(
        highlight(attr),
        highlight(row),
        highlight(entity_type),
        highlight(value)))
    url = '{}{}/{}/{}'.format(config.get('api', 'rest1'), entity_type, row, attr)
    put(url, value)
