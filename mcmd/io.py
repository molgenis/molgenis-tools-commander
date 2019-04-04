from PyInquirer import prompt
from colorama import Fore, Style
from halo import Halo

import mcmd.config.config as config
from mcmd.logging import get_logger
from mcmd.utils.kbhit import KBHit

log = get_logger()

_debug_mode = False
spinner = None


def start(message):
    global spinner
    spinner = _new_spinner()
    spinner.start(message)


def succeed():
    global spinner
    if spinner:
        if config.has_option('settings', 'unicorn_mode') and config.get('settings', 'unicorn_mode'):
            spinner.stop_and_persist(symbol='🦄'.encode('utf-8'))
        else:
            spinner.succeed()

        spinner = None


def info(message):
    """Replaces an existing spinner with an info message and restarts the previous spinner afterwards. Just shows the
    info message if there was no spinner running."""
    prev_text = None
    if spinner:
        prev_text = spinner.text
        info_spinner = spinner
    else:
        info_spinner = _new_spinner()

    info_spinner.info(message)

    if prev_text:
        spinner.start(prev_text)


def warn(message):
    if spinner:
        spinner.warn()
    log.warn('  ' + message)

    if spinner:
        spinner.start()


def error(message):
    global spinner
    if spinner:
        spinner.fail()
        spinner = None

    if message:
        log.error('  ' + message.strip('\"\''))


def debug(message):
    global spinner
    if not _debug_mode:
        return

    if spinner:
        spinner.stop_and_persist()
        spinner = None

    log.debug('  ' + message)


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


def wait_for_enter():
    """Waits until the user presses enter. Non-blocking: the program can still be interrupted and closed."""
    kb = KBHit()
    while True:
        if kb.kbhit():
            c = kb.getch()
            if c == '\n':  # Enter
                break


def _new_spinner():
    return Halo(spinner='dots')


def set_debug():
    global _debug_mode
    _debug_mode = True


def newline():
    log.info('')


def highlight(string):
    return Fore.LIGHTBLUE_EX + string + Fore.RESET


def bold(string):
    return Style.BRIGHT + string + Style.RESET_ALL


def dim(string):
    return Style.DIM + string + Style.RESET_ALL


def _handle_question(question):
    answer = prompt([question])
    if not answer:
        # empty result means that PyInquirer caught an InterruptException
        exit(0)
    else:
        if spinner:
            spinner.start()
        return answer['answer']
