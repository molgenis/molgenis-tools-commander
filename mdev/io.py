from PyInquirer import prompt
from halo import Halo

from mdev.logging import get_logger

log = get_logger()
spinner = None


def start(message):
    global spinner
    spinner = _new_spinner()
    spinner.start(message)


def succeed():
    if spinner:
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
