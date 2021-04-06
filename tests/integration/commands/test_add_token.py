import pytest

from tests.integration.utils import run_commander, random_name


@pytest.mark.integration
def test_add_token(session):
    token = random_name()
    run_commander('add token admin {}'.format(token))

    result = session.get('sys_sec_Token', q='token=={}'.format(token), expand='User')
    assert len(result) == 1

    token = result[0]
    assert token['User']['username'] == 'admin'
