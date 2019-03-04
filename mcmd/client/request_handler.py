"""
Error handling of requests to MOLGENIS.

Error responses can come back in varying forms which this decorator tries to unify. Invalidates the current REST token
if a request came back with 401 'no read meatadata permission' or 200 OK with a login page.
"""

import requests

from mcmd.client import auth
from mcmd.utils.errors import McmdError


class InvalidTokenException(Exception):
    pass


def request(func):
    """Request decorator."""

    def handle_request(*args, **kwargs):
        response = str()
        try:
            response = func(*args, **kwargs)
            _check_authentication(response)
            response.raise_for_status()
            return response
        except InvalidTokenException:
            auth.invalidate_token()
            # retry the request
            return handle_request(*args, **kwargs)
        except requests.HTTPError as e:
            if _is_json(response):
                _handle_json_error(response.json())
            else:
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


def _check_authentication(response):
    """
    Raises an InvalidTokenException if the user isn't logged in.

    There's no sure way to figure out if a token is valid or not. The best we can do is assume that any
    'no read metadata' error, or a login page, means that the user isn't logged in.
    """
    if response.status_code == 401 and _is_json(response):
        error = response.json()['errors'][0]
        if 'code' in error and error['code'] == 'DS04' and 'message' in error and error['message'].startswith(
                "No 'Read metadata' permission"):
            raise InvalidTokenException()
    elif response.status_code == 200 and "('#login-form')" in response.text:
        raise InvalidTokenException()
