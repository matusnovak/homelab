from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.tls import TLSConfig

def build(params: dict):
    docker = DockerClient(
        base_url=params['docker']['host'],
        tls=TLSConfig(
            verify=params['docker']['tls_verify'],
            ca_cert=params['docker']['cert_path']
        )
    )

    docker.images.build(
        path=params['path'],
        tag=params['name']
    )

    image = docker.images.get(params['name'])

    meta = {
        'id': image.attrs['Id']
    }

    return dict(msg='Success', **meta)


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
        'name': {
            'type': 'str',
            'required': True
        },
        'path': {
            'type': 'str',
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    module.exit_json(**build(module.params))


if __name__ == '__main__':
    main()
