from enum import Enum


class InputType(Enum):
    TEXT = 'text'
    BOOL = 'bool'
    PASS = 'pass'


class ValueType(Enum):
    TEMPLATE = 'template'
    BOOL = 'bool'
