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

    def __eq__ (self, other):
        if isinstance (other, Template): 
            if self._variables != other._variables: return False
            if self._string != other._string: return False
            return True
        else:
            return False
    
    def __key(self):
        return (self._string)

    def __hash__(self):
        return hash(self.__key())
