import mcmd.config.home


def _raise_exception(msg):
    raise NotImplementedError(msg)


mcmd.config.home.get_properties_file = lambda: _raise_exception(
    "The properties file is not available from within tests")
