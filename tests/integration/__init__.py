"""
The commander interacts with the file system (to be precise: the .mcmd dir in the user's home). To prevent these
interactions during the integration tests, the modules need to be replaced with mocks, which is done in this package.
"""

import sys

from tests.integration import loader_mock, home_mock

sys.modules['mcmd.config.loader'] = loader_mock
sys.modules['mcmd.config.home'] = home_mock
