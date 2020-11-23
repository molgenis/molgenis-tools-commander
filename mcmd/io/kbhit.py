#!/usr/bin/env python
"""
A Python class implementing KBHIT, the standard keyboard-interrupt poller.
Works transparently on Windows and Posix (Linux, Mac OS X).  Doesn't work
with IDLE.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

Author: Simon D. Levy
"""

import os

# Windows
if os.name == 'nt':
    # noinspection PyUnresolvedReferences
    import msvcrt

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    from select import select


class KBHit:

    def __init__(self):
        """Creates a KBHit object that you can call to do various keyboard things.
        """

        if os.name != 'nt':
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)

    def set_normal_term(self):
        """ Resets to normal terminal.  On Windows this is a no-op.
        """

        if os.name != 'nt':
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    @staticmethod
    def getch():
        """ Returns a keyboard character after kbhit() has been called.
        """

        if os.name == 'nt':
            return msvcrt.getch().decode('utf-8')

        else:
            return sys.stdin.read(1)

    @staticmethod
    def kbhit():
        """ Returns True if keyboard character was hit, False otherwise.
        """
        if os.name == 'nt':
            return msvcrt.kbhit()

        else:
            dr, dw, de = select([sys.stdin], [], [], 0)
            return dr != []
