from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.errors import NotFound, ContainerError
import docker
import json
import string
import random


def extract_image_and_tag(name: str):
    # TODO: Fix to work with registry that contains ports
    # example: registry.example.com:5000/library/image:tag
    tokens = name.split(':', maxsplit=2)
    return (tokens[0], tokens[1])


def pull_image(client: DockerClient, name: str):
    try:
        client.images.get(name)
    except NotFound:
        if name.startswith('sha256:'):
            client.images.pull(name, tag=None)
        else:
            image, tag = extract_image_and_tag(name)
            client.images.pull(image, tag)


def execute(params: dict) -> dict:
    client = docker.from_env()

    volumes = {}
    for volume in params['container']['volumes']:
        key = volume['host']
        volumes[key] = {
            'bind': volume['guest'],
            'mode': 'ro' if volume['read_only'] else 'rw'
        }

    environments = {}
    for environment in params['container']['environment']:
        if not environment['key'] or not environment['value']:
            continue

        key = environment['key']
        environments[key] = environment['value']

    pull_image(client, params['container']['image'])

    container_name = ''.join(random.choice(
        string.ascii_lowercase) for i in range(16))

    try:
        stdout = client.containers.run(
            image=params['container']['image'],
            network=params['container']['network'],
            command=params['container']['command'],
            name=container_name,
            volumes=volumes,
            environment=environments,
            stderr=True,
            stdout=True
        ).decode("utf-8")

        if stdout == '' or stdout == '\n':
            return dict(failed=True, msg='No output from script')

        return dict(msg='Success', output=stdout)

    except ContainerError as e:
        return dict(failed=True, msg=str(e))

    finally:
        try:
            container = client.containers.get(container_name)
            container.stop()
            container.remove()
        except NotFound:
            pass


def main():
    module_args = {
        'container': {
            'type': 'dict',
            'required': True,
            'options': {
                'image': {
                    'type': 'str',
                    'required': True
                },
                'command': {
                    'type': 'list',
                    'required': False,
                    'default': None
                },
                'network': {
                    'type': 'str',
                    'required': False,
                    'default': 'bridge'
                },
                'volumes': {
                    'type': 'list',
                    'required': False,
                    'default': []
                },
                'environment': {
                    'type': 'list',
                    'required': False,
                    'default': []
                }
            }
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    module.exit_json(**execute(module.params))


if __name__ == '__main__':
    main()
