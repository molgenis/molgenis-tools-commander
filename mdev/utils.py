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
