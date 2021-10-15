from typing import Optional

from colorama import Fore, Style
from halo import Halo

import mcmd.config.config as config
from mcmd.io.kbhit import KBHit
from mcmd.io.logging import get_logger

log = get_logger()

_debug_mode = False
spinner: Optional[Halo] = None


def start(message):
    global spinner
    if config.has_option('settings', 'non_interactive') and config.get('settings', 'non_interactive') is True:
        print(message)
    else:
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
    """Turns the current spinner in a warning message (with icon) and starts a new spinner"""
    if spinner:
        spinner.warn()
    log.warn('  ' + message)

    if spinner:
        spinner.start()


def pause():
    """Pause the spinner (with a warning icon), restart it with unpause()"""
    if spinner:
        spinner.warn()


def unpause():
    """Unpause a paused spinner"""
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


def wait_for_enter():
    """Waits until the user presses enter. Non-blocking: the program can still be interrupted and closed."""
    kb = KBHit()
    while True:
        if kb.kbhit():
            c = kb.getch()
            if c in ['\n', '\r\n', '\r']:  # Enter
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
