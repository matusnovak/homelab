import requests
import sys
import json


def expect(res, code: int):
    if res.status_code != code:
        print(f'Received status code: {res.status_code} but expected: {code}')
        print(res.text, file=sys.stderr)
        sys.exit('Request error')


def json_file(path: str):
    with open(path) as f:
        return json.load(f)


def create_admin(args: dict) -> bool:
    base_url = args['url']

    # Check if user has been created
    res = requests.get(f'{base_url}/api/users/admin/check')

    # 404 - admin has not been created
    # 204 - ok
    if res.status_code != 204:
        expect(res, 404)

        # Create user
        data = {
            'Username': args['username'],
            'Password': args['password']
        }
        res = requests.post(f'{base_url}/api/users/admin/init', json=data)
        expect(res, 200)

        return True
    return False


def login(args: dict) -> str:
    base_url = args['url']

    # Log in
    data = {
        'username': args['username'],
        'password': args['password']
    }
    res = requests.post(f'{base_url}/api/auth', json=data)
    expect(res, 200)

    return res.json()['jwt']


def is_ldap_enabled(settings: dict) -> bool:
    return settings['LDAPSettings']['SearchSettings'][0]['Filter'] != ''


def check_ldap_match(settings: dict, args: dict) -> bool:
    ldap = settings['LDAPSettings']
    return (
        settings['AuthenticationMethod'] == 2
        and ldap['URL'] == args['ldap']['host'] + ':' + str(args['ldap']['port'])
        and ldap['AnonymousMode'] == False
        and ldap['ReaderDN'] == args['ldap']['user']
        and ldap['TLSConfig']['TLS'] == False
        and ldap['TLSConfig']['TLSSkipVerify'] == True
        and ldap['StartTLS'] == False
        and len(ldap['SearchSettings']) == 1
        and ldap['SearchSettings'][0]['BaseDN'] == args['ldap']['base']
        and ldap['SearchSettings'][0]['Filter'] == args['ldap']['filter']
        and ldap['SearchSettings'][0]['UserNameAttribute'] == args['ldap']['user_attribute']
    )


def enable_ldap(jwt: str, args: dict, settings: dict):
    base_url = args['url']

    headers = {
        'Authorization': f'Bearer {jwt}'
    }

    ldap = settings['LDAPSettings']
    ldap['URL'] = args['ldap']['host'] + ':' + str(args['ldap']['port'])
    ldap['AnonymousMode'] = False
    ldap['Password'] = args['ldap']['password']
    ldap['ReaderDN'] = args['ldap']['user']

    ldap['TLSConfig']['TLS'] = False
    ldap['TLSConfig']['TLSSkipVerify'] = True
    ldap['StartTLS'] = False

    # Test LDAP connection
    res = requests.put(f'{base_url}/api/settings/authentication/checkLDAP',
                       json=settings, headers=headers)

    if res.status_code == 500:
        return dict(failed=True, msg=res.json()['details'])
    expect(res, 204)

    ldap['SearchSettings'] = [{
        'BaseDN': args['ldap']['base'],
        'Filter': args['ldap']['filter'],
        'UserNameAttribute': args['ldap']['user_attribute']
    }]

    ldap['AutoCreateUsers'] = True
    settings['AuthenticationMethod'] = 2

    # Save settings
    res = requests.put(f'{base_url}/api/settings',
                       json=settings, headers=headers)
    expect(res, 200)


def disable_ldap(jwt: str, args: dict, settings: dict):
    base_url = args['url']

    headers = {
        'Authorization': f'Bearer {jwt}'
    }

    ldap = settings['LDAPSettings']
    ldap['URL'] = ''
    ldap['AnonymousMode'] = False
    ldap['Password'] = ''
    ldap['ReaderDN'] = ''

    ldap['TLSConfig']['TLS'] = False
    ldap['TLSConfig']['TLSSkipVerify'] = False
    ldap['StartTLS'] = False

    ldap['SearchSettings'] = [{
        'BaseDN': '',
        'Filter': '',
        'UserNameAttribute': ''
    }]

    ldap['AutoCreateUsers'] = True
    settings['AuthenticationMethod'] = 1

    # Save settings
    res = requests.put(f'{base_url}/api/settings',
                       json=settings, headers=headers)
    expect(res, 200)


def update_settings(jwt: str, args: dict) -> bool:
    base_url = args['url']

    headers = {
        'Authorization': f'Bearer {jwt}'
    }

    # Get settings
    res = requests.get(f'{base_url}/api/settings', headers=headers)
    expect(res, 200)

    settings = res.json()

    # Check if LDAP is already enabled
    ldap_enabled = is_ldap_enabled(settings)

    # Should we enable LDAP?
    if 'ldap' in args:
        match = False

        # Check if the expected LDAP config matches with what is in Portainer
        if ldap_enabled:
            match = check_ldap_match(settings, args)

        # No match or not yet enabled
        if not match:
            enable_ldap(jwt, args, settings)
            return True

    # Should we disable LDAP?
    elif 'ldap' not in args and ldap_enabled:
        disable_ldap(jwt, args, settings)
        return True

    return False


def command_init(args: dict) -> dict:
    changed = False

    # Check if user has been created
    changed |= create_admin(args)
    jwt = login(args)

    changed |= update_settings(jwt, args)

    return dict(msg='Success', changed=changed)


def main():
    command = sys.argv[1]
    args = json.loads(sys.argv[2])

    commands = {
        'init': command_init
    }

    return commands[command](args)


if __name__ == '__main__':
    print(json.dumps(main()))
