"""
The commander interacts with the file system (to be precise: the .mcmd dir in the user's home). To prevent these
interactions during the integration tests, the modules need to be replaced with mocks, which is done in this package.
"""

import sys

from tests.integration import loader_mock

# Replace the config loader so the test config is loaded
sys.modules['mcmd.config.loader'] = loader_mock

# noinspection PyProtectedMember,PyUnresolvedReferences
# Remove the possibility for the config to save itself to disk
sys.modules['mcmd.config.config']._persist = lambda: None

# noinspection PyProtectedMember,PyUnresolvedReferences
# Remove the possibility for the store to save itself to disk
sys.modules['mcmd.core.store']._persist = lambda: None
