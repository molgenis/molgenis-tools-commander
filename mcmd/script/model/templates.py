from jinja2 import Environment, meta

_env = Environment(autoescape=False)


class Template:
    """
    A container for a Jinja2 template. Exposes the variables found in the template through the variables property.
    """

    def __init__(self, template_str: str):
        self._string = template_str
        self._template = _env.from_string(template_str)

        parsed_content = _env.parse(template_str)
        self._variables = meta.find_undeclared_variables(parsed_content)

    @property
    def variables(self) -> set:
        return self._variables

    @property
    def string(self) -> str:
        return self._string

    def render(self, values: dict) -> str:
        return self._template.render(values)
