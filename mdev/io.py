from PyInquirer import prompt
from halo import Halo

from mdev.configuration import get_config
from mdev.logging import get_logger

log = get_logger()
config = get_config()
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
    answer = prompt(questions)

    if spinner:
        spinner.start()
    return answer


def _new_spinner():
    return Halo(spinner='dots')
