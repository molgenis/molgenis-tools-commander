from typing import NamedTuple, Set

from mcmd.script.model.statements import Statement


class Line(NamedTuple):
    number: int
    string: str


class ParsedLine:
    """
    A parsed line contains the line number, original line string and the parsed Statement. A parsed line may have
    dependencies on other lines (through Templates). These are exposed through the dependencies property.
    """

    def __init__(self, raw_string: str, number: int, statement: Statement):
        self._raw = raw_string
        self._number = number
        self._statement = statement
        self._dependencies = set()

    @property
    def raw(self) -> str:
        return self._raw

    @property
    def number(self) -> int:
        return self._number

    @property
    def statement(self) -> Statement:
        return self._statement

    @property
    def dependencies(self) -> Set['ParsedLine']:
        return self._dependencies

    def add_dependency(self, line: 'ParsedLine'):
        self._dependencies.add(line)

    def __eq__ (self, other): 
        if isinstance (other, ParsedLine):
            if self.raw != other.raw: return False
            if self.number != other.number: return False
            if self.statement != other.statement: return False
            if self.dependencies != other.dependencies: return False
            return True
        else:
            return False

