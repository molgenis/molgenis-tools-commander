from abc import abstractmethod
from typing import Optional, Any

import attr

from mcmd.script.model.templates import Template
from mcmd.script.model.types_ import InputType, ValueType


@attr.s(frozen=True)
class Statement:
    """A single or multi-lined statement in a MC script."""
    pass


@attr.s(frozen=True, auto_attribs=True)
class Assignment:
    """
    A statement that assigns a value. Should expose the value's name through the name property.

    $value type = "assignment"
    $input bool is_assigned
    """

    name: str


@attr.s(frozen=True)
class Templatable:
    """
    A statement that contains one or more Templates. Should expose all its Templates' variables through the variables
    property.
    """

    @property
    @abstractmethod
    def variables(self) -> frozenset:
        pass


@attr.s(frozen=True, auto_attribs=True)
class Value(Statement, Templatable, Assignment):
    """
    A value assignment. Supports text (in the form of a Template), booleans and None values.

    $value text = "text {{variable}}"
    $value bool = true
    $value empty
    """

    type: ValueType
    value: Any

    @classmethod
    def from_untyped_value(cls, name: str, value):
        if value is None:
            type_ = None
        elif isinstance(value, bool):
            type_ = ValueType.BOOL
        elif isinstance(value, Template):
            type_ = ValueType.TEMPLATE
        else:
            raise ValueError('invalid value type: {}'.format(type(value)))
        return cls(name, type_, value)

    @property
    def variables(self) -> set:
        if self.type == ValueType.TEMPLATE:
            return self.value.variables
        else:
            return set()


@attr.s(frozen=True, auto_attribs=True)
class Input(Statement, Templatable, Assignment):
    """
    An input assignment. Doesn't have a value because the inputs are requested from the user at runtime. Supports
    multiple input types and an optional message.

    $input bool yesno
    $input text type : "text"
    """

    type: InputType
    message: Optional[Template] = None

    @property
    def variables(self) -> frozenset:
        if self.message is not None:
            return self.message.variables
        else:
            return frozenset()


@attr.s(frozen=True, auto_attribs=True)
class Wait(Statement, Templatable):
    """
    A wait statement. Shows a message until the user presses enter.

    $wait : "Get a snack"
    """

    message: Template

    @property
    def variables(self) -> frozenset:
        return self.message.variables


@attr.s(frozen=True, auto_attribs=True)
class VisibleComment(Statement, Templatable):
    """
    Comments that will be printed to the output.

    # Creating user {{name}}
    """

    text: Template

    @property
    def variables(self) -> frozenset:
        return self.text.variables


@attr.s(frozen=True, auto_attribs=True)
class Command(Statement, Templatable):
    """
    A MOLGENIS Commander command.
    """

    command: Template

    @property
    def variables(self) -> frozenset:
        return self.command.variables


@attr.s(frozen=True, auto_attribs=True)
class InvisibleComment(Statement):
    """
    Comments that won't be processed in any way.

    // this is a comment
    """

    comment: str


@attr.s(frozen=True)
class Empty(Statement):
    """
    An empty line.
    """
    pass
