from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.docker_utils import create_proxy
from subprocess import Popen, PIPE
import json


def exec(params: dict):
    with create_proxy(params['docker'], params['container'], params['port']) as port:
        port_arg = ['--port', str(port)]
        args = params['args']
        script = params['script']

        p = Popen(['python3', script] + port_arg + args, stdin=PIPE,
                  stdout=PIPE, stderr=PIPE, bufsize=-1)

        output, error = p.communicate()

        if p.returncode == 0:
            res = json.loads(output)
            return res
        else:
            return dict(failed=True, msg='Error code {}'.format(p.returncode), stdout=output, stderr=error)


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
                },
            }
        },
        'container': {
            'type': 'str',
            'required': True
        },
        'port': {
            'type': 'int',
            'required': True
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
        supports_check_mode=False
    )

    module.exit_json(**exec(module.params))


if __name__ == '__main__':
    main()
