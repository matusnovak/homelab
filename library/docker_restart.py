from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.tls import TLSConfig
from docker.errors import NotFound


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
        'containers': {
            'type': 'list',
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    docker = DockerClient(
        base_url=module.params['host'],
        tls=TLSConfig(
            verify=module.params['tls_verify'],
            ca_cert=module.params['cert_path']
        )
    )

    # Find an existing container
    containers = []
    for name in module.params['containers']:
        container_name = '{}_{}'.format(
            module.params['project'],
            name
        )
        containers.append(docker.containers.get(container_name))

    # Stop them all in reverse order
    for container in reversed(containers):
        container.stop()

    # Start them in normal order
    for container in containers:
        container.start()

    module.exit_json(changed=True, msg='Success')


if __name__ == '__main__':
    main()
