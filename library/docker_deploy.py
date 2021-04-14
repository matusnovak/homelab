from typing import List, Tuple
from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.tls import TLSConfig
from docker.errors import NotFound
import copy

DOCKER_PROJECT_LABEL = 'com.docker.compose.project'


def extract_image_and_tag(name: str) -> Tuple[str, str]:
    # TODO: Fix to work with registry that contains ports
    # example: registry.example.com:5000/library/image:tag
    tokens = name.split(':', maxsplit=2)
    return (tokens[0], tokens[1])


def pull_image(docker: DockerClient, name: str):
    if name.startswith('sha256:'):
        docker.images.pull(name, tag=None)
    else:
        image, tag = extract_image_and_tag(name)
        docker.images.pull(image, tag)


def get_image(docker: DockerClient, name: str):
    try:
        return docker.images.get(name)
    except NotFound:
        return None


def add_image_vars(image, definition):
    envs = image.attrs['Config']['Env']
    for env in envs:
        tokens = env.split('=', maxsplit=2)
        key = tokens[0].strip()
        value = tokens[1].strip()

        if key not in definition['environment']:
            definition['environment'][key] = value

    labels = image.attrs['Config']['Labels']
    for label_key, label_value in labels.items():
        if label_key not in definition['labels']:
            definition['labels'][label_key] = label_value


def create_container_name(project_name: str, name: str):
    return '{}_{}'.format(project_name, name)


def create_definition(params: dict):
    definition = {
        'image': params['container']['image'],
        'name': create_container_name(params['project'], params['container']['name']),
        'hostname': params['container']['name'],
        'networks': {
        },
        'ports': {
        },
        'labels': {
            DOCKER_PROJECT_LABEL: params['project']
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
    definition['environment'] = {}

    ignore_alias = attrs['Id'][:12]

    for network_name, data in attrs['NetworkSettings']['Networks'].items():
        definition['networks'][network_name] = {
            'aliases': []
        }

        if data['Aliases'] is not None:
            aliases = list(
                filter(lambda a: a != ignore_alias, data['Aliases']))
            definition['networks'][network_name]['aliases'] = aliases

    ports = attrs['HostConfig']['PortBindings']
    for key, values in ports.items():
        host_port = ''
        if len(values) > 0:
            host_port = values[0]['HostPort']

        definition['ports'][key] = host_port

    for key, value in attrs['Config']['Labels'].items():
        definition['labels'][key] = value

    for env in attrs['Config']['Env']:
        tokens = env.split('=', maxsplit=2)
        key = tokens[0].strip()
        definition['environment'][key] = tokens[1].strip()

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


def create_container(docker: DockerClient, definition: dict):
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
        'environment': definition['environment'],
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
        existing_def = create_definition_existing(container)

        # The definition from the existing container will contain environment
        # variables that were not defined by the user. These come automatically from
        # the image itself. The definition we have created in here will not
        # contain those variables. We will have to add them, but only if missing, from
        # the image. We will also need to make a copy of the definition, because
        # we do not want to create a container with those default environment variables.
        # If we would do that, they would be persistent, and if they change in a new image,
        # we would be still using the old ones. The original definition must not contain these
        # unless explicitly provided in the params from the role/user.
        copied_def = copy.deepcopy(definition)

        image = get_image(docker, container.attrs['Image'])

        # Add env variables from image into the copied definition, if they are missing
        add_image_vars(image, copied_def)

        # Are they same?
        if existing_def != copied_def:
            # We will have to re-create the container
            if check_mode:
                return dict(changed=False, msg='Re-creating')

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
