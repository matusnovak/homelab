from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.tls import TLSConfig
from docker.errors import NotFound

DOCKER_PROJECT_LABEL = 'com.docker.compose.project'


def pull_image(docker: DockerClient, name: str):
    tokens = name.split(':')
    docker.images.pull(tokens[0], tokens[1])


def create_definition(params: dict, name: str):
    definition = {
        'image': params['container']['image'],
        'name': name,
        'hostname': params['container']['name'],
        'alias': params['container']['network']['alias'],
        'ports': {
        },
        'labels': {
            DOCKER_PROJECT_LABEL: params['project']
        },
        'volumes': {
        }
    }

    for port in params['container']['ports']:
        if not port['guest'] or not port['host']:
            continue

        key = '{}/{}'.format(port['guest'], port['protocol'])
        definition['ports'][key] = port['host']

    for label in params['container']['labels']:
        if not label['key'] or label['value']:
            continue

        key = label['key']
        definition['labels'][key] = label['value']

    for volume in params['container']['volumes']:
        if not volume['host'] or not volume['guest']:
            continue

        key = volume['host']
        definition['volumes'][key] = {
            'bind': volume['guest'],
            'mode': 'ro' if volume['read_only'] else 'rw'
        }

    return definition


def find_network(docker: DockerClient, name: str):
    try:
        return docker.networks.get(name)
    except NotFound:
        return None


def find_container(docker: DockerClient, name: str):
    try:
        return docker.containers.get(name)
    except NotFound:
        return None


def deploy(docker: DockerClient, network, definition: dict):
    alias = definition['alias']
    del definition['alias']
    container = docker.containers.create(detach=True, **definition)
    network.connect(container.id, aliases=[alias])
    container.start()
    return container


def should_start(container):
    return container.attrs['State']['Running'] == False


def main():
    module_args = {
        'host': {
            'type': 'str',
            'required': False,
            'default': 'unix://var/run/docker.sock'
        },
        'tls_verify': {
            'type': 'bool',
            'required': False,
            'default': False
        },
        'cert_path': {
            'type': 'str',
            'required': False,
            'default': None
        },
        'project': {
            'type': 'str',
            'required': True,
        },
        'container': {
            'type': 'dict',
            'required': True,
            'options': {
                'image': {
                    'type': 'str',
                    'required': True
                },
                'name': {
                    'type': 'str',
                    'required': True
                },
                'network': {
                    'type': 'dict',
                    'required': True,
                    'options': {
                        'name': {
                            'type': 'str',
                            'required': True
                        },
                        'alias': {
                            'type': 'str',
                            'required': True
                        }
                    }
                },
                'ports': {
                    'type': 'list',
                    'required': False,
                    'default': []
                },
                'labels': {
                    'type': 'list',
                    'required': False,
                    'default': []
                },
                'volumes': {
                    'type': 'list',
                    'required': False,
                    'default': []
                }
            }
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    docker = DockerClient(
        base_url=module.params['host'],
        tls=TLSConfig(
            verify=module.params['tls_verify'],
            ca_cert=module.params['cert_path']
        )
    )

    container_name = '{}_{}'.format(
        module.params['project'],
        module.params['container']['name']
    )
    network_name = module.params['container']['network']['name']

    network = find_network(docker, network_name)
    if network is None:
        module.exit_json(
            failed=True,
            msg='Docker network does not exist'
        )
        return

    definition = create_definition(module.params, container_name)

    changed = False
    container = find_container(docker, container_name)

    if container is not None and should_start(container):
        changed = True

        if module.check_mode:
            module.exit_json(changed=changed, msg='Starting')
            return

        container.start()

    if container is None:
        changed = True

        if module.check_mode:
            module.exit_json(changed=changed, msg='Creating')
            return

        # Must pull image before creating the container
        pull_image(docker, definition['image'])

        # Create the container
        container = deploy(docker, network, definition)

    meta = {
        'id': container.id,
        'state': container.attrs['State']['Status'],
        'hostname': definition['hostname'],
        'image': container.attrs['Config']['Image'],
        'address': module.params['container']['network']['alias']
    }

    module.exit_json(changed=changed, msg='Success', **meta)


if __name__ == '__main__':
    main()
