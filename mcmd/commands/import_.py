from os import path as os_path
from pathlib import Path
from urllib.parse import urljoin

import polling
import requests

import mcmd.config.config as config
import mcmd.io.ask
from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.context import context
from mcmd.core.errors import McmdError
from mcmd.github import client as github
from mcmd.io import io
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import post_file, get, post
from mcmd.utils import files

# =========
# Arguments
# =========

# Store a reference to the parser so that we can show an error message for the custom validation rule
_p_import = None


@arguments('import')
def add_arguments(subparsers):
    global _p_import
    _p_import = subparsers.add_parser('import',
                                      help='import a dataset')
    _p_import.set_defaults(func=import_,
                           write_to_history=True)
    _p_import.add_argument('resource',
                           nargs='?',
                           help='the resource to import - depending on the other options this can be a path, '
                                'file name, or URL')
    p_import_source = _p_import.add_mutually_exclusive_group()
    p_import_source.add_argument('--from-path', '-p',
                                 action='store_true',
                                 help='import a file the old school way: by path')
    p_import_source.add_argument('--from-issue', '-i',
                                 metavar='NUMBER',
                                 help="import a file attachment from a GitHub issue - optionally supply the file name "
                                      "of the attachment")
    p_import_source.add_argument('--from-url', '-u',
                                 action='store_true',
                                 help='import a file from a URL - uses the importByUrl endpoint of the MOLGENIS '
                                      'importer, without downloading the file first')
    _p_import.add_argument('--in',
                           dest='to_package',
                           type=str,
                           metavar='PACKAGE_ID',
                           help='the package to import to')
    _p_import.add_argument('--as',
                           dest='entity_type_id',
                           type=str,
                           metavar='ENTITY_TYPE_ID',
                           help='the id of the entity type (only used when importing VCF files)')
    _p_import.add_argument('--with-action', '-a',
                           dest='import_action',
                           type=str,
                           choices=['add', 'add_update_existing', 'update'],
                           help='strategy to use when importing')
    return _p_import


# =========
# Globals
# =========

_IMPORT_ACTIONS = {'.owl': 'add',
                   '.obo': 'add',
                   '.vcf': 'add'}


# =======
# Methods
# =======

@command
def import_(args):
    _validate_args(args)
    _choose_import_method(args)


def _validate_args(args):
    """The 'resource' argument can't be made required at the parser level because the '--from-issue' argument can be
    used with or without specifying a file name."""
    if not args.resource and not args.from_issue:
        _p_import.error("the following argument is required: resource")


def _choose_import_method(args):
    if args.from_path:
        _import_from_path(args)
    elif args.from_url:
        _import_from_url(args)
    elif args.from_issue:
        _import_from_issue(args)
    else:
        _import_from_quick_folders(args)


def _import_from_url(args):
    file_url = args.resource
    file_name = file_url.split("/")[-1]
    io.start('Importing from URL %s' % highlight(file_url))

    if args.import_action:
        action = args.import_action
    else:
        action = _get_import_action(file_name)

    params = {'action': action,
              'metadataAction': 'upsert'}

    if args.to_package:
        params['packageId'] = args.to_package

    params['url'] = file_url

    response = post(api.import_by_url(), params=params)
    import_run_url = urljoin(config.get('host', 'selected'), response.text)
    status, message = _poll_for_completion(import_run_url)
    if status == 'FAILED':
        raise McmdError(message)


def _import_from_quick_folders(args):
    file_name = os_path.splitext(args.resource)[0]
    path = files.select_file_from_folders(folders=context().get_git_folders() + context().get_dataset_folders(),
                                          file_name=file_name)
    _do_import(path, args.to_package, args.entity_type_id, args.import_action)


def _import_from_issue(args):
    issue_num = args.from_issue
    attachment = _select_attachment(issue_num, args.resource)
    file_path = _download_attachment(attachment, issue_num)
    _do_import(file_path, args.to_package, args.entity_type_id, args.import_action)


def _import_from_path(args):
    file = Path(args.resource)
    if not file.is_file():
        raise McmdError("File %s doesn't exist" % str(file.resolve()))
    _do_import(file, args.to_package, args.entity_type_id, args.import_action)


def _select_attachment(issue_num, wanted_attachment):
    """Gets attachments from a GitHub issue. If wanted_attachment is specified it will try to select that attachment."""
    attachments = github.get_attachments(issue_num)
    if len(attachments) == 0:
        raise McmdError("Issue #%s doesn't contain any files" % issue_num)

    if wanted_attachment:
        selected = [a for a in attachments if a.name == wanted_attachment]
        if len(selected) == 0:
            raise McmdError('There are no attachments named %s.' % wanted_attachment)
        if len(selected) > 1:
            raise McmdError('Multiple attachments with name %s found.' % wanted_attachment)
        return selected[0]
    else:
        if len(attachments) > 1:
            return _choose_attachment(attachments)
        else:
            return attachments[0]


def _create_attachment_map(attachments):
    """"Creates a dict of name/attachment pairs. If the name isn't unique, uses the identifier as key. Example:
            1234/example.xls
            4567/example.xls
            other_example.xls
    """
    names = [a.name for a in attachments]

    attachment_map = dict()
    for a in attachments:
        if names.count(a.name) > 1:
            attachment_map[a.id] = a
        else:
            attachment_map[a.name] = a

    return attachment_map


def _choose_attachment(attachments):
    """Let user choose from multiple attachments. Attachments with duplicate names will display their id."""
    attachment_map = _create_attachment_map(attachments)
    choices = list(attachment_map.keys())

    answer = mcmd.io.ask.multi_choice('Multiple attachments found. Choose which one to import:', choices)
    return attachment_map[answer]


def _download_attachment(attachment, issue_num):
    issue_folder = context().get_issues_folder().joinpath(issue_num)
    issue_folder.mkdir(parents=True, exist_ok=True)
    file_path = issue_folder.joinpath(attachment.name)

    if file_path.exists():
        overwrite = mcmd.io.ask.confirm('File %s already exists. Re-download?' % file_path.name)
        if not overwrite:
            return file_path

    io.start('Downloading %s from GitHub issue %s' % (highlight(attachment.name), highlight('#' + issue_num)))
    try:
        r = requests.get(attachment.url)
        r.raise_for_status()
        with file_path.open('wb') as f:
            f.write(r.content)
    except (OSError, requests.RequestException, requests.HTTPError) as e:
        raise McmdError('Error downloading GitHub attachment: %s' % str(e))
    io.succeed()
    return file_path


def _do_import(file_path, package, entity_type_id, import_action):
    io.start('Importing %s' % (highlight(file_path.name)))

    if import_action:
        action = import_action
    else:
        action = _get_import_action(file_path.name)

    params = {'action': action,
              'metadataAction': 'upsert'}

    if package:
        params['packageId'] = package
    if entity_type_id:
        params['entityTypeId'] = entity_type_id

    response = post_file(api.import_(), file_path.resolve(), params)
    import_run_url = urljoin(config.get('host', 'selected'), response.text)
    status, message = _poll_for_completion(import_run_url)
    if status == 'FAILED':
        raise McmdError(message)


def _get_import_action(file_name):
    file_name = file_name.rstrip('.gz')
    file_name = file_name.rstrip('.zip')
    for file_type, action in _IMPORT_ACTIONS.items():
        if file_name.endswith(file_type):
            return action
    return config.get('settings', 'import_action')


def _poll_for_completion(url):
    def step_function(step):
        """Increases time between polls with one second each time, with a maximum of 10 seconds."""
        step += 1
        return min(step, 10)

    polling.poll(lambda: get(url).json()['status'] != 'RUNNING',
                 step=0,
                 step_function=step_function,
                 poll_forever=True)
    import_run = get(url).json()
    return import_run['status'], import_run['message']
