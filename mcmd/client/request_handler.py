import requests

from mcmd.client import auth
from mcmd.utils.utils import McmdError


def request(func):
    """Request decorator."""
    def handle_request(*args, **kwargs):
        response = str()
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            if not _token_is_valid(response):
                auth.login()
                handle_request(*args, **kwargs)
            if _is_json(response):
                _handle_json_error(response.json())
            raise McmdError(str(e))
        except requests.RequestException as e:
            raise McmdError(str(e))

    return handle_request


def _handle_json_error(response_json):
    if 'errors' in response_json:
        for error in response_json['errors']:
            raise McmdError(error['message'])
    elif 'errorMessage' in response_json:
        raise McmdError(response_json['errorMessage'])


def _is_json(response):
    return response.headers.get('Content-Type') and 'application/json' in response.headers.get('Content-Type')


def _token_is_valid(response):
    """There's no real way to figure out if a token is valid or not. The best we can do is assume that any
    'no read metadata' error means that the user isn't logged in."""
    if response.status_code == 401 and _is_json(response):
        error = response.json()['errors'][0]
        if 'code' in error and error['code'] == 'DS04' and 'message' in error and error['message'].startswith(
                "No 'Read metadata' permission"):
            return False
    return True
