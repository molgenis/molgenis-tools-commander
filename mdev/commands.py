import json
import logging
from urllib.parse import urljoin

import requests

LOG = logging.getLogger()


def import_(args, config):
    print("importing")


def make(args, config):
    print("make...", args)

    pass


def add(args, config):
    token = _login(config)

    if args.type == 'user':
        _add_user(args.value, token)
    elif args.type == 'group':
        _add_group(args.value, token, config)


def _add_user(config, username, token):
    try:
        response = requests.post(urljoin(config.get('host'), '/api/v1/sys_sec_User'),
                                 headers={'Content-Type': 'application/json',
                                          'x-molgenis-token': token},
                                 data=json.dumps({'username': username,
                                                  'password_': username,
                                                  'Email': username + "@molgenis.org",
                                                  'active': True}))
        response.raise_for_status()
    except requests.RequestException as e:
        LOG.error(e)
        exit(1)


def _add_group(name, client, config):
    new_group_url = urljoin(config.get('api', 'host'), config.get('api', 'group'))
    client.session.post(new_group_url,
                        headers=client._get_token_header_with_content_type(),
                        data=json.dumps({'name': name, 'label': name}))


def run(args, config):
    print("run", args)


def _login(config):
    host = config.get('api', 'host')
    username = config.get('auth', 'username')
    password = config.get('auth', 'password')

    try:
        response = requests.post(urljoin(host, 'api/v1/login'),
                                 data=json.dumps({"username": username, "password": password}),
                                 headers={"Content-Type": "application/json"})
        response.raise_for_status()
        return response.json()['token']
    except requests.RequestException as e:
        LOG.error(e)
        exit(1)
