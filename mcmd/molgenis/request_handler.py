"""
Error handling of requests to MOLGENIS.

Error responses can come back in varying forms which this decorator tries to unify.
"""

import requests

from mcmd.molgenis import auth
from mcmd.core.errors import McmdError, MolgenisOfflineError


def request(func):
    """Request decorator."""

    def handle_request(*args, **kwargs):
        auth.check_token()

        response = str()
        try:
            response = func(*args, **kwargs)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            if _is_json(response):
                _handle_json_error(response.json())
            else:
                raise McmdError(str(e))
        except requests.exceptions.ConnectionError:
            raise MolgenisOfflineError()
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
