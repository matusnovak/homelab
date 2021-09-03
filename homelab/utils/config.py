from dataclasses import dataclass
from typing import List, Union


@dataclass
class Option:
    key: str
    value: Union[str, None, bool, int, float]
    help: str


BASE_OPTIONS = [
    Option(key='project_name', value='homelab',
           help='Name of the project, this will be used for Kubernetes namespace and other places.')
]


def config_merge_options(options: List[Option], file: str) -> dict:
    data = {}
    for option in options:
        data[option.key] = option.value

    # TODO load from file

    return data
