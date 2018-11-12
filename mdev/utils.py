from pathlib import Path
import ast

class MdevError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def upper_snake(string):
    """
    Transforms a string to uppercase snake style.
    E.g. 'lower-kebab-style' becomes 'LOWER_KEBAB_STYLE'.
    """
    return string.upper().replace('-', '_')


def lower_kebab(string):
    """
    Transforms a string to lowercase kebab style.
    E.g. 'SCREAMING_SNAKE' becomes 'screaming-snake'.
    """
    return string.lower().replace('_', '-')


def config_string_to_paths(config_string):
    """Strips and splits comma separated, multi-line configuration variables and converts them to Paths objects."""
    clean_string = ''.join(config_string.split())
    paths = clean_string.split(',')
    return [Path(path_string) for path_string in paths]


def file_to_string(file_path):
    """
    file_to_string converts content of a file on the specified path to a string
    :param file_path: the path to the file
    :return: data: a string of the content of the specified file
    """
    with open(file_path, 'r') as file:
        data = file.read().replace('\n', '')
    return data


def string_to_json(json_string):
    """
    string_to_json converts a string with json structure to a dictionary
    :param json_string: string formatted in json structure, although both " and ' are allowed
    :return: json_structure: the json string converted to a dictionary
    :exception: MdevError: when json_string does not consist of valid json
    """
    # Easier to Ask for Forgiveness than Permission
    try:
        # Use ast.literal rather than json.loads to accept both ' and " rather than double quotes only
        json_structure = ast.literal_eval(json_string)
        return json_structure
    except:
        raise MdevError("Input rows are not written in valid json")
