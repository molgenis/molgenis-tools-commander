from abc import ABC, abstractmethod
from typing import List

from mcmd.script.model.lines import Line, ParsedLine


class ScriptValidationError(ABC, Exception):
    def __init__(self, line_number: int):
        self.line_number = line_number

    @property
    @abstractmethod
    def message(self):
        pass


class InvalidScriptError(Exception):
    def __init__(self, errors: List[ScriptValidationError]):
        self._errors = errors

    @property
    def errors(self) -> List[ScriptValidationError]:
        return self._errors


class ScriptSyntaxError(ScriptValidationError):
    """
    Raised when a line in the script contains a syntax error and couldn't be parsed.
    """

    def __init__(self, error_msg: str, line: Line, column: int = -1):
        super().__init__(line_number=line.number)
        self.error_msg = error_msg.capitalize()
        self.line = line
        self.column = column

    @property
    def message(self) -> str:
        msg = list()
        line_num_text = 'Line {}: '.format(self.line.number)
        msg.append(line_num_text + self.line.string)

        if self.column > -1:
            # add column indicator
            spacing = ' ' * len(line_num_text)
            spacing += ' ' * self.column
            msg.append(spacing + '^')

        msg.append("  - {}".format(self.error_msg))
        return '\n'.join(msg)


class ReassignmentError(ScriptValidationError):
    """
    Raised when a value has already been assigned in an earlier line.
    """

    def __init__(self, name: str, source: ParsedLine, other: ParsedLine):
        super().__init__(line_number=source.number)
        self._name = name
        self._source = source
        self._other = other

    @property
    def message(self):
        msg = list()
        msg.append('Line {}: {}'.format(self._source.number, self._source.raw))
        msg.append("  - Value '{}' is already assigned at line {}".format(self._name,
                                                                          self._other.number))
        return '\n'.join(msg)


class ForwardReferenceError(ScriptValidationError):
    """
    Raised when a Template references a value that is assigned at a later line.
    """

    def __init__(self, name: str, source: ParsedLine, referred: ParsedLine):
        super().__init__(line_number=source.number)
        self._name = name
        self._source = source
        self._referred = referred

    @property
    def message(self):
        msg = list()
        msg.append('Line {}: {}'.format(self._source.number, self._source.raw))
        msg.append("  - Value '{}' referenced before assignment: '{}' is assigned at "
                   "line {}".format(self._name,
                                    self._name,
                                    self._referred.number))
        return '\n'.join(msg)


class UnknownReferenceError(ScriptValidationError):
    """
    Raised when a Template references a value that is not assigned in the script.
    """

    def __init__(self, source: ParsedLine, reference: str):
        super().__init__(line_number=source.number)
        self._source = source
        self._reference = reference

    @property
    def message(self):
        msg = list()
        msg.append('Line {}: {}'.format(self._source.number, self._source.raw))
        msg.append("  - Unknown value '{}'".format(self._reference))
        return '\n'.join(msg)


class RecursiveReferenceError(ScriptValidationError):
    """
    Raised when a value is assigned that references itself.

    $value name = "{{name}}"
    """

    def __init__(self, source: ParsedLine, reference: str):
        super().__init__(line_number=source.number)
        self._source = source
        self._reference = reference

    @property
    def message(self):
        msg = list()
        msg.append('Line {}: {}'.format(self._source.number, self._source.raw))
        msg.append("  - Value '{}' referenced during assignment".format(self._reference))
        return '\n'.join(msg)
