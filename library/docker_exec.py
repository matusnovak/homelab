from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.tls import TLSConfig
from docker.errors import NotFound, ContainerError
import json


def execute(params: dict) -> dict:
    docker = DockerClient(
        base_url=params['docker']['host'],
        tls=TLSConfig(
            verify=params['docker']['tls_verify'],
            ca_cert=params['docker']['cert_path']
        )
    )

    container = docker.containers.get(params['container'])

    code, stdout = container.exec_run(params['args'], user=params['user'])

    if code != 0:
        return dict(failed=True, msg=f'Exit code {code}', output=stdout)

    return dict(msg='Success', output=stdout)


def main():
    module_args = {
        'docker': {
            'type': 'dict',
            'required': True,
            'options': {
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
                }
            }
        },
        'container': {
            'type': 'str',
            'required': True,
        },
        'user': {
            'type': 'str',
            'required': False,
            'default': 'root'
        },
        'args': {
            'type': 'list',
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    module.exit_json(**execute(module.params))


if __name__ == '__main__':
    main()
