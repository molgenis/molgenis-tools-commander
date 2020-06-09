from abc import abstractmethod, ABC

from mcmd.script.model.templates import Template
from mcmd.script.model.types_ import InputType, ValueType


class Statement:
    """A single or multi-lined statement in a MC script."""
    pass


class Assignment(ABC):
    """
    A statement that assigns a value. Should expose the value's name through the name property.

    $value type = "assignment"
    $input bool is_assigned
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class Templatable:
    """
    A statement that contains one or more Templates. Should expose all its Templates' variables through the variables
    property.
    """

    @property
    @abstractmethod
    def variables(self) -> set:
        pass


class Value(Statement, Templatable, Assignment):
    """
    A value assignment. Supports text (in the form of a Template), booleans and None values.

    $value text = "text {{variable}}"
    $value bool = true
    $value empty
    """

    def __init__(self, name: str, value=None):
        self._name = name
        self.__set_type(value)
        self._value = value

    def __set_type(self, value):
        if value is None:
            self._type = None
        elif isinstance(value, bool):
            self._type = ValueType.BOOL
        elif isinstance(value, Template):
            self._type = ValueType.TEMPLATE
        else:
            raise ValueError('invalid value type: {}'.format(type(value)))

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def type(self) -> ValueType:
        return self._type

    @property
    def variables(self) -> set:
        if self._type == ValueType.TEMPLATE:
            return self._value.variables
        else:
            return set()


class Input(Statement, Templatable, Assignment):
    """
    An input assignment. Doesn't have a value because the inputs are requested from the user at runtime. Supports
    multiple input types and an optional message.

    $input bool yesno
    $input text type : "text"
    """

    def __init__(self, name: str, type_: InputType, message: Template = None):
        self._name = name
        self._type = type_
        self._message = message
        self.__set_variables()

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> InputType:
        return self._type

    @property
    def message(self) -> Template:
        return self._message

    @property
    def variables(self) -> set:
        return self._variables

    def __set_variables(self):
        variables = set()
        if self._message is not None:
            variables |= self._message.variables
        self._variables = variables


class Wait(Statement, Templatable):
    """
    A wait statement. Shows a message until the user presses enter.

    $wait : "Get a snack"
    """

    def __init__(self, message: Template):
        self._message = message

    @property
    def message(self) -> Template:
        return self._message

    @property
    def variables(self) -> set:
        return self._message.variables


class VisibleComment(Statement, Templatable):
    """
    Comments that will be printed to the output.

    # Creating user {{name}}
    """

    def __init__(self, text: Template):
        self._text = text

    @property
    def text(self) -> Template:
        return self._text

    @property
    def variables(self) -> set:
        return self._text.variables


class Command(Statement, Templatable):
    """
    A MOLGENIS Commander command.
    """

    def __init__(self, command: Template):
        self._command = command

    @property
    def command(self) -> Template:
        return self._command

    @property
    def variables(self) -> set:
        return self._command.variables


class InvisibleComment(Statement):
    """
    Comments that won't be processed in any way.

    // this is a comment
    """

    def __init__(self, comment: str):
        self._comment = comment

    @property
    def comment(self) -> str:
        return self._comment


class Empty(Statement):
    """
    An empty line.
    """
    pass
