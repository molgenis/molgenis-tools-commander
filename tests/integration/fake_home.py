import mcmd.config.home


def _raise_exception(msg):
    raise NotImplementedError(msg)


def get_history_file():
    return None


def get_issues_folder():
    return None


def get_scripts_folder():
    return None


mcmd.config.home.get_properties_file = lambda: _raise_exception(
    "The properties file is not available from within tests")
