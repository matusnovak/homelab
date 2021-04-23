from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.errors import NotFound, ContainerError


def execute(params: dict) -> dict:
    docker = DockerClient(
        base_url=params['docker']
    )

    def query(filter: str):
        args = [
            'ldapsearch',
            '-x',
            '-H',
            'ldap://localhost',
            '-b',
            params['base'],
            '-D',
            params['user'],
            '-w',
            params['password'],
            filter
        ]

        return ' '.join(args)

    def get_count(output: str) -> int:
        for line in output.split('\n'):
            if line.startswith('# numEntries:'):
                tokens = line.split(':')
                return int(tokens[1].rstrip())
        return 0

    try:
        cn = params['cn']
        dn = cn + ',' + params['base']

        container = docker.containers.get(params['container'])

        cmd = query(f'(&(cn={cn})(objectClass=groupOfUniqueNames))')
        code, output = container.exec_run(cmd)

        if code != 0:
            return dict(failed=True, msg=output.decode('utf-8'))

        if get_count(output.decode('utf-8')) != 0:
            return dict(changed=False, msg='Success')

        return dict(changed=True, msg='Success')

    except ContainerError as e:
        return dict(failed=True, msg=str(e))
    except NotFound as e:
        return dict(failed=True, msg='No such container')


def main():
    module_args = {
        'docker': {
            'type': 'str',
            'required': True
        },
        'container': {
            'type': 'str',
            'required': True
        },
        'user': {
            'type': 'str',
            'required': True,
        },
        'password': {
            'type': 'str',
            'required': True,
            'no_log': True
        },
        'base': {
            'type': 'str',
            'required': True
        },
        'cn': {
            'type': 'str',
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    module.exit_json(**execute(module.params))


if __name__ == '__main__':
    main()
