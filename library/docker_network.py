from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.tls import TLSConfig
from docker.errors import NotFound

DOCKER_PROJECT_LABEL = 'com.docker.compose.project'


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
        'network': {
            'type': 'dict',
            'required': True,
            'options': {
                'name': {
                    'type': 'str',
                    'required': True
                },
                'attachable': {
                    'type': 'bool',
                    'required': False,
                    'default': False
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

    project_name = module.params['project']
    network_name = '{}_{}'.format(
        project_name,
        module.params['network']['name']
    )
    network = None
    changed = False

    try:
        network = docker.networks.get(network_name)

        if DOCKER_PROJECT_LABEL not in network.attrs['Labels'] or \
                network.attrs['Labels'][DOCKER_PROJECT_LABEL] != project_name:
            module.exit_json(
                failed=True,
                msg='Docker network already exist but was not created by us'
            )
            return

    except NotFound:
        if module.check_mode:
            module.exit_json(changed=True, msg='Creating')
            return

        network = docker.networks.create(
            name=network_name,
            driver='bridge',
            check_duplicate=True,
            enable_ipv6=False,
            attachable=module.params['network']['attachable'],
            labels={
                DOCKER_PROJECT_LABEL: project_name
            }
        )

        changed = True

    meta = {
        'name': network.attrs['Name'],
        'subnet': network.attrs['IPAM']['Config'][0]['Subnet'],
        'gateway': network.attrs['IPAM']['Config'][0]['Subnet']
    }

    module.exit_json(changed=changed, msg='Success', **meta)


if __name__ == '__main__':
    main()
