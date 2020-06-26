import attr

from mcmd.script.model.statements import Statement


@attr.s(frozen=True, auto_attribs=True)
class Line:
    number: int
    string: str


@attr.s(frozen=True, auto_attribs=True)
class ParsedLine:
    """
    A parsed line contains the line number, original line string and the parsed Statement. A parsed line may have
    dependencies on other lines (through Templates). These are exposed through the dependencies property.
    """

    raw: str
    number: int
    statement: Statement
