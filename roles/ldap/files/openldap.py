import sys
import json
import ldap


def command_healthcheck(con, args: dict):
    return dict(msg='Success')


def command_group(con, args: dict):
    name = args['name']
    base = args['base']

    def get_members():
        return [m['name'].encode('utf-8') for m in args['members']]

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
        return dict(dn=res[0][0], cn=name)

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


def command_ou(con, args: dict):
    name = args['name']
    base = args['base']

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
        return dict(dn=res[0][0], ou=name)

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


def main():
    command = sys.argv[1]
    args = json.loads(sys.argv[2])

    commands = {
        'healthcheck': command_healthcheck,
        'organizationa_unit': command_ou,
        'group': command_group
    }

    con = ldap.initialize(args['address'])

    try:
        code, res = con.bind_s(
            args['user'], args['password'], ldap.AUTH_SIMPLE)
        assert code == 97

        return commands[command](con, args)

    except ldap.LDAPError as e:
        return dict(failed=True, msg=str(e))

    finally:
        con.unbind_s()


if __name__ == '__main__':
    print(json.dumps(main()))
