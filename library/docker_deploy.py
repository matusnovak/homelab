from typing import List, Tuple
from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.tls import TLSConfig
from docker.errors import NotFound
import json
import hashlib

DOCKER_PROJECT_LABEL = 'com.docker.compose.project'
DOCKER_CONFIG_HASH_LABEL = 'com.docker.compose.config-hash'


def extract_image_and_tag(name: str) -> Tuple[str, str]:
    # TODO: Fix to work with registry that contains ports
    # example: registry.example.com:5000/library/image:tag
    tokens = name.split(':', maxsplit=2)
    return (tokens[0], tokens[1])


def pull_image(docker: DockerClient, name: str):
    try:
        docker.images.get(name)
    except NotFound:
        if name.startswith('sha256:'):
            docker.images.pull(name, tag=None)
        else:
            image, tag = extract_image_and_tag(name)
            docker.images.pull(image, tag)


def create_container_name(project_name: str, name: str):
    return '{}_{}'.format(project_name, name)


def get_config_hash_value(container):
    labels = container.attrs['Config']['Labels']
    if DOCKER_CONFIG_HASH_LABEL in labels:
        return labels[DOCKER_CONFIG_HASH_LABEL]
    return None


def make_hash(definition: dict):
    return str(hashlib.md5(json.dumps(definition, sort_keys=True).encode('utf-8')).hexdigest())


def create_definition(params: dict):
    definition = {
        'image': params['container']['image'],
        'command': params['container']['command'],
        'user': params['container']['user'],
        'name': create_container_name(params['project'], params['container']['name']),
        'hostname': params['container']['hostname'],
        'networks': {
        },
        'ports': {
        },
        'labels': {
            DOCKER_PROJECT_LABEL: params['project'],
        },
        'volumes': {
        },
        'environment': {
        }
    }

    for network in params['container']['networks']:
        if not network['name']:
            continue

        key = network['name']
        definition['networks'][key] = {
            'aliases': [network['alias']] if network['alias'] else []
        }

    for port in params['container']['ports']:
        if not port['guest'] or not port['host']:
            continue

        key = '{}/{}'.format(port['guest'], port['protocol'])
        definition['ports'][key] = port['host']

    for label in params['container']['labels']:
        if not label['key'] or not label['value']:
            continue

        key = label['key']
        definition['labels'][key] = label['value']

    for environment in params['container']['environment']:
        if not environment['key'] or not environment['value']:
            continue

        key = environment['key']
        definition['environment'][key] = environment['value']

    for volume in params['container']['volumes']:
        if not volume['host'] or not volume['guest']:
            continue

        key = volume['host']
        definition['volumes'][key] = {
            'bind': volume['guest'],
            'mode': 'ro' if volume['read_only'] else 'rw'
        }

    definition['labels'][DOCKER_CONFIG_HASH_LABEL] = make_hash(definition)

    return definition


def find_networks(docker: DockerClient, names: List[str]):
    networks = []
    for name in names:
        try:
            networks.append(docker.networks.get(name))
        except NotFound:
            return None
    return networks


def find_container(docker: DockerClient, name: str):
    try:
        return docker.containers.get(name)
    except NotFound:
        return None


def create_container(docker: DockerClient, definition: dict):
    networking_config = {}
    for network_name, network in definition['networks'].items():
        networking_config[network_name] = docker.api.create_endpoint_config(**{
            'aliases': network['aliases']
        })

        # Docker container can not be connected to multiple networks at once
        # We will have to do that manually if > 1
        break

    volumes = []
    ports = []

    host_config = {
        'port_bindings': definition['ports'],
        'binds': definition['volumes']
    }

    for _, volume in definition['volumes'].items():
        volumes.append(volume['bind'])

    for port_protocol, _ in definition['ports'].items():
        tokens = port_protocol.split('/')
        port = int(tokens[0])
        protocol = tokens[1]
        ports.append((port, protocol))

    args = {
        'image': definition['image'],
        'command': definition['command'],
        'name': definition['name'],
        'hostname': definition['hostname'],
        'labels': definition['labels'],
        'environment': definition['environment'],
        'volumes': volumes,
        'ports': ports,
        'user': definition['user'],
        'host_config': docker.api.create_host_config(**host_config),
        'detach': True,
        'networking_config': docker.api.create_networking_config(networking_config)
    }

    container_id = docker.api.create_container(**args)
    container = docker.containers.get(container_id)

    # Connect to all other networks
    for network_name, item in definition['networks'].items():
        if network_name in networking_config:
            continue

        network = docker.networks.get(network_name)
        network.connect(container_id, aliases=item['aliases'])

    try:
        container.start()

    except Exception as e:
        container.stop()
        container.remove()
        raise e

    return container


def should_start(container):
    return container.attrs['State']['Running'] == False


def create_meta(params: dict, definition: dict, container) -> dict:
    alias = None
    address = None

    # Find first network
    if len(params['container']['networks']) > 0:
        networks_dict = container.attrs['NetworkSettings']['Networks']
        network_name = params['container']['networks'][0]['name']

        network = networks_dict[network_name]
        alias_ignore = container.attrs['Id'][:12]

        if network['Aliases'] != None:
            alias = list(
                filter(lambda a: a != alias_ignore, network['Aliases']))[0]

        address = network['IPAddress']

    return {
        'id': container.id,
        'state': container.attrs['State']['Status'],
        'hostname': definition['hostname'],
        'image': container.attrs['Config']['Image'],
        'address': address,
        'alias': alias
    }


def deploy(check_mode: bool, params: dict):
    docker = DockerClient(
        base_url=params['host'],
        tls=TLSConfig(
            verify=params['tls_verify'],
            ca_cert=params['cert_path']
        )
    )

    # Container naming follows a strict convention
    container_name = create_container_name(
        params['project'], params['container']['name'])

    # Create the expected container definition using parameters passed
    definition = create_definition(params)

    # Find an existing container
    changed = False
    container = find_container(docker, container_name)

    # If we have an existing container, create a definition out of it
    # We will use that for comparison
    if container is not None:
        # Calculate our hash
        definition_hash = definition['labels'][DOCKER_CONFIG_HASH_LABEL]

        # Get the label for the existing container
        existing_hash = get_config_hash_value(container)

        # Are they same?
        if existing_hash is None or existing_hash != definition_hash:
            # We will have to re-create the container
            if check_mode:
                return dict(changed=False, msg='Re-creating')

            # return dict(failed=True, existing=existing_hash, our=definition_hash)

            container.stop()
            container.remove()
            container = None
            changed = True

    # Container found, do we need to start it?
    if container is not None and should_start(container):
        if check_mode:
            meta = create_meta(params, definition, container)
            return dict(changed=True, msg='Starting', **meta)

        container.start()
        changed = True

    # No container found, we will create it
    if container is None:
        if check_mode:
            return dict(changed=True, msg='Creating')

        # Must pull image before creating the container
        pull_image(docker, definition['image'])

        # Create the container
        container = create_container(docker, definition)
        changed = True

    meta = create_meta(params, definition, container)

    return dict(changed=changed, msg='Success', **meta)


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
                'command': {
                    'type': 'list',
                    'required': False,
                    'default': None
                },
                'user': {
                    'type': 'str',
                    'required': False,
                    'default': None
                },
                'name': {
                    'type': 'str',
                    'required': True
                },
                'hostname': {
                    'type': 'str',
                    'required': False,
                    'default': None
                },
                'networks': {
                    'type': 'list',
                    'required': False,
                    'default': []
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
        supports_check_mode=True
    )

    module.exit_json(**deploy(module.check_mode, module.params))


if __name__ == '__main__':
    main()
