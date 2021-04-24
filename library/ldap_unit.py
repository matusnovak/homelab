from ansible.module_utils.basic import AnsibleModule
import docker
from docker.errors import NotFound, ContainerError


def execute(params: dict, tries: int = 5) -> dict:
    client = docker.from_env()

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

    def modify(values: list):
        echo = '\"'
        for key, value in values:
            if len(echo) != 1:
                echo += '\n'
            echo += f'{key}: {value}'
        echo += "\""

        args = [
            '/bin/bash',
            '-c',
            '\'',
            'echo',
            echo,
            '|',
            'ldapmodify',
            '-x',
            '-H',
            'ldap://localhost',
            '-D',
            params['user'],
            '-c',
            '-w',
            params['password'],
            '\''
        ]

        return ' '.join(args)

    def get_count(output: str) -> int:
        for line in output.split('\n'):
            if line.startswith('# numEntries:'):
                tokens = line.split(':')
                return int(tokens[1].rstrip())
        return 0

    try:
        ou = params['ou']
        dn = 'ou=' + ou + ',' + params['base']

        container = client.containers.get(params['container'])

        cmd = query(f'(&(ou={ou})(objectClass=organizationalUnit))')
        code, output = container.exec_run(cmd)

        if code != 0:
            return dict(failed=True, msg=output.decode('utf-8'))

        if get_count(output.decode('utf-8')) != 0:
            return dict(changed=False, msg='Already exists')

        values = [
            ('dn', dn),
            ('changetype', 'add'),
            ('objectClass', 'top'),
            ('objectClass', 'organizationalUnit'),
            ('ou', ou)
        ]

        cmd = modify(values)
        code, output = container.exec_run(cmd)

        if code != 0:
            return dict(failed=True, msg=output.decode('utf-8'))

        return dict(changed=True, msg='Entry created')

    except ContainerError as e:
        cant_contact = 'Can\'t contact LDAP server' in str(e)
        if cant_contact and tries > 0:
            return execute(params, tries - 1)

        return dict(failed=True, msg=str(e), tries=tries)
    except NotFound as e:
        return dict(failed=True, msg='No such container')


def main():
    module_args = {
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
        'ou': {
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
