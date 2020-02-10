from datetime import datetime


def timestamp():
    """Returns a timestamp in the format that MOLGENIS requires."""
    return datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
