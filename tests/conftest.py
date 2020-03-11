"""
Pytest command line options to configure the test environment.
"""


def pytest_addoption(parser):
    parser.addoption('--url',
                     action='store',
                     default='http://localhost:8080/')
    parser.addoption('--username',
                     action='store',
                     default='admin')
    parser.addoption('--password',
                     action='store',
                     default='admin')
    parser.addoption('--pg_user',
                     action='store')
    parser.addoption('--pg_password',
                     action='store')
    parser.addoption('--db_name',
                     action='store',
                     default='molgenis')
    parser.addoption('--molgenis_home',
                     action='store')
    parser.addoption('--minio_data',
                     action='store')
