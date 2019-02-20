import pytest

from tests.integration.utils import run_commander, random_name


def _token_by_token_query(token):
    return [{
        "field": "token",
        "operator": "EQUALS",
        "value": token
    }]


@pytest.mark.integration
def test_add_token(session):
    token = random_name()
    run_commander('add token admin {}'.format(token))

    result = session.get('sys_sec_Token', q=_token_by_token_query(token), expand=['user'])
    assert len(result) == 1

    token = result[0]
    assert token['User']['username'] == 'admin'
