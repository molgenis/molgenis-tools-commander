from pathlib import Path

import questionary

from mcmd.io import io


def multi_choice(message, choices):
    question = questionary.select(message, choices=choices)
    return _ask(question)


def checkbox(message, choices):
    checks = [{'name': choice, 'value': idx} for idx, choice in enumerate(choices)]

    question = questionary.checkbox(message, choices=checks)

    answer_ids = _ask(question, _validate_empty_list)
    return [choices[idx] for idx in answer_ids]


def input_(message, required=False):
    question = questionary.text(message)

    if required:
        return _ask(question, _validate_empty_input)
    else:
        return _ask(question)


def input_file_name(location: Path, extension: str = '', suffix: str = ''):
    """
    Asks the user to enter a file name.
    Will check if the file name already exists and ask the user to overwrite or enter a new name.
    :param location: the Path to which the file should be stored
    :param extension: the file extension (e.g. tar.gz)
    :param suffix: a suffix for the file name (for example a timestamp)
    :return: a unique file name
    """
    file_name = ''
    while not file_name:
        name = input_('Please enter a name:', required=True)
        name += suffix

        if location.joinpath(name + extension).exists():
            overwrite = confirm('{} already exists. Overwrite?'.format(location.joinpath(name + extension)))
            if overwrite:
                file_name = name
        else:
            file_name = name

    return file_name


def password(message):
    return _ask(questionary.password(message))


def confirm(message):
    question = questionary.confirm(message, default=False)
    return _ask(question)


def _ask(question, validation=None):
    answer = question.ask()

    if answer is None:
        # None result means that PyInquirer caught an InterruptException
        exit(0)
    elif validation:
        result = validation(answer)
        if result is not True:
            io.error(result)
            return _ask(question, validation)

    return answer


def _validate_empty_list(answer):
    return 'You must choose at least one option.' if len(answer) == 0 else True


def _validate_empty_input(answer):
    return "This field can't be empty." if len(answer) == 0 else True
