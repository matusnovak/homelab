from typing import List
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
        'networks': {
        },
        'ports': {
        },
        'labels': {
            DOCKER_PROJECT_LABEL: params['project']
        },
        'volumes': {
        }
    }

    for network in params['container']['networks']:
        if not network['name']:
            continue

        key = network['name']
        definition['networks'][key] = {
            'aliases': [network['alias']]
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

    for volume in params['container']['volumes']:
        if not volume['host'] or not volume['guest']:
            continue

        key = volume['host']
        definition['volumes'][key] = {
            'bind': volume['guest'],
            'mode': 'ro' if volume['read_only'] else 'rw'
        }

    return definition


def create_definition_existing(container):
    definition = {}

    attrs = container.attrs

    definition['image'] = attrs['Config']['Image']
    definition['name'] = attrs['Name'].split('/')[-1]
    definition['hostname'] = attrs['Config']['Hostname']
    definition['networks'] = {}
    definition['ports'] = {}
    definition['labels'] = {}
    definition['volumes'] = {}

    # network = attrs['NetworkSettings']['Networks'][network_name] \
    #    if network_name in attrs['NetworkSettings']['Networks'] else None

    # if network is not None:
    #    ignore_alias = attrs['Id'][:12]
    #    definition['alias'] = list(
    #        filter(lambda a: a != ignore_alias, network['Aliases']))

    ignore_alias = attrs['Id'][:12]

    for network_name, data in attrs['NetworkSettings']['Networks'].items():
        if network_name == 'bridge':
            continue

        definition['networks'][network_name] = {
            'aliases': list(filter(lambda a: a != ignore_alias, data['Aliases']))
        }

    ports = attrs['HostConfig']['PortBindings']
    for key, values in ports.items():
        host_port = ''
        if len(values) > 0:
            host_port = values[0]['HostPort']

        definition['ports'][key] = host_port

    for key, value in attrs['Config']['Labels'].items():
        if key.startswith('org.opencontainers'):
            continue

        definition['labels'][key] = value

    for mount in attrs['Mounts']:
        key = mount['Source']
        definition['volumes'][key] = {
            'bind': mount['Destination'],
            'mode': mount['Mode']
        }

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


def deploy(docker: DockerClient, definition: dict):
    networking_config = {}
    for network_name, network in definition['networks'].items():
        networking_config[network_name] = docker.api.create_endpoint_config(**{
            'aliases': network['aliases']
        })

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
        'name': definition['name'],
        'hostname': definition['hostname'],
        'labels': definition['labels'],
        'volumes': volumes,
        'ports': ports,
        'host_config': docker.api.create_host_config(**host_config),
        'detach': True,
        'networking_config': docker.api.create_networking_config(networking_config)
    }

    container_id = docker.api.create_container(**args)
    container = docker.containers.get(container_id)

    try:
        container.start()

    except Exception as e:
        container.stop()
        container.remove()
        raise e

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

    # Container naming follows a strict convention
    container_name = '{}_{}'.format(
        module.params['project'],
        module.params['container']['name']
    )

    # Create the expected container definition using parameters passed
    definition = create_definition(module.params, container_name)

    # Find an existing container
    changed = False
    container = find_container(docker, container_name)

    # If we have an existing container, create a definition out of it
    # We will use that for comparison
    if container is not None:
        existing_def = create_definition_existing(container)

        # Are they same?
        if existing_def != definition:
            # We will have to re-create the container
            if module.check_mode:
                module.exit_json(changed=changed, msg='Re-creating')
                return

            # module.exit_json(
            #    failed=True, container=existing_def, definition=definition)
            # return
            container.stop()
            container.remove()
            container = None

    # Container found, do we need to start it?
    if container is not None and should_start(container):
        changed = True

        if module.check_mode:
            module.exit_json(changed=changed, msg='Starting')
            return

        container.start()

    # No container found, we will create it
    if container is None:
        changed = True

        if module.check_mode:
            module.exit_json(changed=changed, msg='Creating')
            return

        # Must pull image before creating the container
        pull_image(docker, definition['image'])

        # Create the container
        container = deploy(docker, definition)

    address = None
    if len(module.params['container']['networks']) > 0:
        address = module.params['container']['networks'][0]['alias']

    meta = {
        'id': container.id,
        'state': container.attrs['State']['Status'],
        'hostname': definition['hostname'],
        'image': container.attrs['Config']['Image'],
        'address': address
    }

    module.exit_json(changed=changed, msg='Success', **meta)


if __name__ == '__main__':
    main()
