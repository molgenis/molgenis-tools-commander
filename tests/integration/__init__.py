"""
The commander interacts with the file system (to be precise: the .mcmd dir in the user's home). To prevent these
interactions during the integration tests, the modules need to be replaced with mocks, which is done in this package.
"""

import sys

from tests.integration import loader_mock


# noinspection PyProtectedMember,PyUnresolvedReferences,PyTypeChecker
def mock_config():
    # Replace the config loader so the test config is loaded
    sys.modules['mcmd.config.loader'] = loader_mock
    # Remove the possibility for the config to save itself to disk
    sys.modules['mcmd.config.config']._persist = lambda: None


# noinspection PyProtectedMember,PyUnresolvedReferences
def mock_store():
    import mcmd.core.store
    # Remove the possibility for the store to save itself to disk
    sys.modules['mcmd.core.store']._persist = lambda: None
    # Remove the possibility for the store to load itself from disk
    sys.modules['mcmd.core.store'].load = lambda: None


mock_config()
mock_store()
