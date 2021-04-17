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

    args = []
    for arg in params['args']:
        if not isinstance(arg, str):
            args.append(json.dumps(arg))
        else:
            args.append(arg)

    script = params['script']
    command = ['python3', script] + args

    try:
        stdout = docker.containers.run(
            image=params['image'],
            network=params['network'],
            command=command,
            name='scriptrunner',
            volumes={
                script: {
                    'bind': script,
                    'mode': 'ro'
                }
            },
            stderr=True,
            stdout=True
        ).decode("utf-8")

        if stdout == '' or stdout == '\n':
            return dict(failed=True, msg='No output from script')

        try:
            return json.loads(stdout)
        except:
            return dict(failed=True, msg='Unable to parse output', output=stdout)

    except ContainerError as e:
        return dict(failed=True, msg=str(e))

    finally:
        try:
            container = docker.containers.get('scriptrunner')
            container.stop()
            container.remove()
        except NotFound:
            pass


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
        'network': {
            'type': 'str',
            'required': True,
        },
        'image': {
            'type': 'str',
            'required': True,
        },
        'script': {
            'type': 'str',
            'required': True
        },
        'args': {
            'type': 'list',
            'required': False,
            'default': []
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    module.exit_json(**execute(module.params))


if __name__ == '__main__':
    main()
