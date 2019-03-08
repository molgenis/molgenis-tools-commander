import json
from urllib.parse import urljoin

import requests

from mcmd.client import auth
from mcmd.client.request_handler import request
from mcmd.config import config


@request
def get(url):
    return requests.get(url,
                        headers=_get_default_headers())


@request
def post(url, data):
    return requests.post(url,
                         headers=_get_default_headers(),
                         data=json.dumps(data))


@request
def post_file(url, file_path, params):
    return requests.post(url,
                         headers={'x-molgenis-token': auth.get_token()},
                         files={'file': open(file_path, 'rb')},
                         params=params)


@request
def post_files(files, url):
    return requests.post(url,
                         headers={'x-molgenis-token': auth.get_token()},
                         files=files)


@request
def post_form(url, data):
    return requests.post(url,
                         headers={
                             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                             'x-molgenis-token': auth.get_token()},
                         data=data)


@request
def delete(url):
    return requests.delete(url,
                           headers=_get_default_headers())


@request
def delete_data(url, data):
    return requests.delete(url,
                           headers=_get_default_headers(),
                           data=json.dumps({"entityIds": data}))


@request
def put(url, data):
    return requests.put(url=url,
                        headers=_get_default_headers(),
                        data=data)


@request
def import_by_url(params):
    return requests.post(config.api('import_url'),
                         headers=_get_default_headers(),
                         params=params)


@request
def get_version():
    return requests.get(urljoin(config.api('rest2'), 'version'),
                        headers={'Content-Type': 'application/json'})


def _get_default_headers():
    headers = {'Content-Type': 'application/json',
               'x-molgenis-token': auth.get_token()}
    return headers
