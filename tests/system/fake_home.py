import pkg_resources

import mcmd.config.home


def _raise_exception(msg):
    raise NotImplementedError(msg)


_TEST_CONFIG = pkg_resources.resource_filename('tests.system', 'test.yaml')
mcmd.config.home.get_properties_file = lambda: _raise_exception(
    "The properties file is not available from within tests")
