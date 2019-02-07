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
