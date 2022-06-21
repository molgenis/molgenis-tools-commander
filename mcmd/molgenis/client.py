import json

import requests
from requests import Response

from mcmd.molgenis import auth
from mcmd.molgenis.request_handler import request

# TODO use a molgenis.client.Session

@request
def get(url, params=None) -> Response:
    return requests.get(url,
                        params=params,
                        headers=_get_default_headers())


@request
def post(url, data=None, params=None):
    kwargs = {'headers': _get_default_headers()}
    if data:
        kwargs['data'] = json.dumps(data)
    if params:
        kwargs['params'] = params

    return requests.post(url, **kwargs)


@request
def patch(url, data=None, params=None):
    kwargs = {'headers': _get_default_headers()}
    if data:
        kwargs['data'] = json.dumps(data)
    if params:
        kwargs['params'] = params

    return requests.patch(url, **kwargs)


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
def delete(url, data=None):
    kwargs = {'headers': _get_default_headers()}
    if data:
        kwargs['data'] = json.dumps(data)

    return requests.delete(url, **kwargs)


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


def _get_default_headers():
    headers = {'Content-Type': 'application/json',
               'x-molgenis-token': auth.get_token()}
    return headers
