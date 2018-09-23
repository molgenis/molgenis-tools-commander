from PyInquirer import prompt
from colorama import Fore
from halo import Halo

from mdev.config.config import get_config
from mdev.logging import get_logger

log = get_logger()
config = get_config()

_debug_mode = False
spinner = None


def start(message):
    global spinner
    spinner = _new_spinner()
    spinner.start(message)


def succeed():
    if spinner:
        if config.has_option('set', 'unicorn_mode') and config.getboolean('set', 'unicorn_mode'):
            spinner.stop_and_persist(symbol='🦄'.encode('utf-8'))
        else:
            spinner.succeed()


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
    if spinner:
        spinner.fail()

    log.error('  ' + message.strip('\"\''))


def debug(message):
    global spinner
    if not _debug_mode:
        return

    if spinner:
        spinner.stop_and_persist()
        spinner = None

    log.debug('  ' + message)


def multi_choice(question, choices):
    if spinner:
        spinner.stop_and_persist()

    questions = [
        {
            'type': 'rawlist',
            'name': 'answer',
            'message': question,
            'choices': choices
        }
    ]
    answer = prompt(questions)['answer']

    if spinner:
        spinner.start()
    return answer


def _new_spinner():
    return Halo(spinner='dots')


def set_debug():
    global _debug_mode
    _debug_mode = True


def highlight(string):
    return Fore.BLUE + string + Fore.RESET
