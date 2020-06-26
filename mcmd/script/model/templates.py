from typing import FrozenSet

import attr
import jinja2
from jinja2 import Environment, meta

_env = Environment(autoescape=False)


@attr.s(frozen=True, auto_attribs=True)
class Template:
    """
    A container for a Jinja2 template. Exposes the variables found in the template through the variables property.
    """

    string: str
    _template: jinja2.Template = attr.ib(init=False, eq=False)
    variables: FrozenSet[str] = attr.ib(init=False)

    @_template.default
    def __set_template(self):  # NOSONAR method is not unused
        return _env.from_string(self.string)

    @variables.default
    def __set_variables(self) -> frozenset:  # NOSONAR method is not unused
        parsed_content = _env.parse(self.string)
        return frozenset(meta.find_undeclared_variables(parsed_content))

    def render(self, values: dict) -> str:
        return self._template.render(values)
