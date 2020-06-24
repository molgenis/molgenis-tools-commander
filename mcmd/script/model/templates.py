from typing import FrozenSet

import attr
from jinja2 import Environment, meta

_env = Environment(autoescape=False)


@attr.s(frozen=True)
class Template:
    """
    A container for a Jinja2 template. Exposes the variables found in the template through the variables property.
    """

    string: str = attr.ib()
    _template = attr.ib(init=False, eq=False)
    variables: FrozenSet[str] = attr.ib(init=False)

    @_template.default
    def __set_template(self):
        return _env.from_string(self.string)

    @variables.default
    def __set_variables(self) -> frozenset:
        parsed_content = _env.parse(self.string)
        return frozenset(meta.find_undeclared_variables(parsed_content))

    def render(self, values: dict) -> str:
        return self._template.render(values)
