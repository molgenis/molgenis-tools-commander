from mcmd.io.io import spinner


def multi_choice(message, choices):
    if spinner:
        spinner.stop_and_persist()

    message = {
        'type': 'rawlist',
        'name': 'answer',
        'message': message,
        'choices': choices
    }

    return _handle_question(message)


def checkbox(message, choices):
    if spinner:
        spinner.stop_and_persist()

    checks = [{'name': choice, 'value': idx} for idx, choice in enumerate(choices)]

    message = {
        'type': 'checkbox',
        'name': 'answer',
        'message': message,
        'choices': checks,
        'validate': lambda answer: 'You must choose at least one option.' if len(answer) == 0 else True
    }

    answer_ids = _handle_question(message)
    return [choices[idx] for idx in answer_ids]


def input_(message, required=False):
    if spinner:
        spinner.stop_and_persist()

    message = {
        'type': 'input',
        'name': 'answer',
        'message': message,
    }

    if required:
        message['validate'] = lambda answer: "This field can't be empty." if len(answer) == 0 else True

    return _handle_question(message)


def password(message):
    if spinner:
        spinner.warn()

    message = {
        'type': 'password',
        'name': 'answer',
        'message': message,
    }

    return _handle_question(message)


def confirm(message):
    if spinner:
        spinner.stop_and_persist()

    message = {
        'type': 'confirm',
        'default': False,
        'name': 'answer',
        'message': message
    }

    return _handle_question(message)


def _handle_question(question):
    answer = prompt([question])
    if not answer:
        # empty result means that PyInquirer caught an InterruptException
        exit(0)
    else:
        if spinner:
            spinner.start()
        return answer['answer']