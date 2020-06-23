import attr

from mcmd.script.model.statements import Statement


@attr.s(frozen=True)
class Line:
    number: int = attr.ib()
    string: str = attr.ib()


@attr.s(frozen=True)
class ScriptLine:
    """
    A parsed line contains the line number, original line string and the parsed Statement. A parsed line may have
    dependencies on other lines (through Templates). These are exposed through the dependencies property.
    """

    raw: str = attr.ib()
    number: int = attr.ib()
    statement: Statement = attr.ib()
