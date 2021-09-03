import os
import click
from jinja2 import Template, StrictUndefined
from jinja2.exceptions import TemplateError


def load_file(path: str, config: dict) -> str:
    current_path = os.path.dirname(os.path.realpath(__file__))
    real_path = os.path.abspath(os.path.join(
        current_path, '..', 'files', path))

    with open(real_path, 'r') as f:
        contents = f.read()
        if real_path.endswith('.j2'):
            try:
                t = Template(contents, undefined=StrictUndefined)
                return t.render(**config)
            except TemplateError as e:
                raise Exception(
                    f'Error while rendering template {path}: {str(e.message)}')

        return contents
