from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.docker_utils import create_proxy
import ldap


def exec(params: dict):
    with create_proxy(params['docker'], params['container'], 389) as port:
        try:
            con = ldap.initialize(f'ldap://localhost:{port}')

            code, res = con.bind_s(
                params['user'], params['password'], ldap.AUTH_SIMPLE)
            assert code == 97

            res = con.search_s(
                params['base'],
                ldap.SCOPE_SUBTREE,
                params['filter'],
                params['attrs']
            )

            if params['exact'] is not None and len(res) != params['exact']:
                return dict(
                    failed=True,
                    msg='Did not receive exact number of results expected',
                    results=res
                )

            return dict(msg='Success', results=res)
        except ldap.LDAPError as e:
            return dict(failed=True, msg=str(e))


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
        'user': {
            'type': 'str',
            'required': True
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
        'filter': {
            'type': 'str',
            'required': True
        },
        'attrs': {
            'type': 'list',
            'required': False,
            'default': []
        },
        'exact': {
            'type': 'int',
            'required': False,
            'default': None
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    module.exit_json(**exec(module.params))


if __name__ == '__main__':
    main()
