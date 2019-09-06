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
