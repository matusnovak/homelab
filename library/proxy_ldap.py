from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.docker_utils import create_proxy
import ldap
import ldap.modlist as modlist


def search(con, base: str, params: dict):
    res = con.search_s(
        base,
        ldap.SCOPE_SUBTREE,
        params['filter'],
        params['attrs']
    )

    if params['exact'] is not None and len(res) != params['exact']:
        return dict(
            failed=True,
            changed=False,
            msg='Did not receive exact number of results expected',
            results=res
        )

    return dict(msg='Success', changed=False, results=res)


def create_ou(con, base: str, params: dict):
    name = params['name']

    def get_unit():
        res = con.search_s(
            base,
            ldap.SCOPE_SUBTREE,
            f'(&(objectClass=organizationalUnit)(ou={name}))',
            []
        )
        if len(res) == 0:
            return None

        assert len(res) == 1
        return dict(dn=res[0][0], **res[0][1])

    res = get_unit()

    if res is not None:
        return dict(msg='Success', changed=False, **res)

    dn = f'ou={name},{base}'
    attrs = [
        ('objectClass', b'organizationalUnit')
    ]

    con.add_s(dn, attrs)

    res = get_unit()
    assert res is not None

    return dict(msg='Success', changed=True, **res)


def create_group(con, base: str, params: dict):
    name = params['name']

    def get_members():
        return [m['name'].encode('utf-8') for m in params['members']]

    def get_group():
        res = con.search_s(
            base,
            ldap.SCOPE_SUBTREE,
            f'(&(objectClass=groupOfUniqueNames)(cn={name}))',
            []
        )
        if len(res) == 0:
            return None

        assert len(res) == 1
        return dict(dn=res[0][0], **res[0][1])

    res = get_group()

    if res is not None:
        return dict(msg='Success', changed=False, **res)

    dn = f'cn={name},{base}'
    attrs = [
        ('objectClass', b'groupOfUniqueNames'),
        ('uniqueMember', get_members()),
    ]

    con.add_s(dn, attrs)

    res = get_group()
    assert res is not None

    return dict(msg='Success', changed=True, **res)


def exec(params: dict):
    with create_proxy(params['docker'], params['container'], 389) as port:
        con = ldap.initialize(f'ldap://localhost:{port}')

        try:
            code, res = con.bind_s(
                params['user'], params['password'], ldap.AUTH_SIMPLE)
            assert code == 97

            if params['search'] is not None:
                return search(con, params['base'], params['search'])

            if params['organisational_unit'] is not None:
                return create_ou(con, params['base'], params['organisational_unit'])

            if params['group'] is not None:
                return create_group(con, params['base'], params['group'])

            return dict(changed=False, msg='Login success')

        except ldap.LDAPError as e:
            return dict(failed=True, msg=str(e))

        finally:
            con.unbind_s()


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
        'search': {
            'type': 'dict',
            'required': False,
            'options': {
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
            },
            'default': None
        },
        'organisational_unit': {
            'type': 'dict',
            'required': False,
            'options': {
                'name': {
                    'type': 'str',
                    'required': True
                }
            },
            'default': None
        },
        'group': {
            'type': 'dict',
            'required': False,
            'options': {
                'name': {
                    'type': 'str',
                    'required': True
                },
                'members': {
                    'type': 'list',
                    'required': False,
                    'default': []
                }
            },
            'default': None
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    module.exit_json(**exec(module.params))


if __name__ == '__main__':
    main()
