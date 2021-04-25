import requests
import sys
import json


def request(method: str, url: str, code: int = None, json=None, data=None, headers=None):
    print(f'{method} {url}')
    res = requests.request(method, url, json=json,
                           data=data, headers=headers, verify=False)
    if code is not None and res.status_code != code:
        msg = f'{method} {url} received status code: {res.status_code} but expected: {code} response: {res.text}'
        raise Exception(msg)
    return res


def json_file(path: str):
    with open(path) as f:
        return json.load(f)


def create_admin(args: dict) -> bool:
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    # Check if user has been created
    res = request('GET', f'{base_url}/api/users/admin/check', headers=headers)

    # 404 - admin has not been created
    # 204 - ok
    if res.status_code != 204:
        assert res.status_code == 404, "We expect http 404 if admin user has not been created yet"

        # Create user
        data = {
            'Username': args['username'],
            'Password': args['password']
        }
        res = request('POST', f'{base_url}/api/users/admin/init',
                      json=data, code=200, headers=headers)

        return True
    return False


def login(args: dict) -> str:
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    # Log in
    data = {
        'username': args['username'],
        'password': args['password']
    }
    res = request('POST', f'{base_url}/api/auth',
                  json=data, code=200, headers=headers)

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
        'Authorization': f'Bearer {jwt}',
        'Host': args['host']
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
    res = request('PUT', f'{base_url}/api/settings/authentication/checkLDAP', code=204,
                  json=settings, headers=headers)

    ldap['SearchSettings'] = [{
        'BaseDN': args['ldap']['base'],
        'Filter': args['ldap']['filter'],
        'UserNameAttribute': args['ldap']['user_attribute']
    }]

    ldap['AutoCreateUsers'] = True
    settings['AuthenticationMethod'] = 2

    # Save settings
    res = request('PUT', f'{base_url}/api/settings', code=200,
                  json=settings, headers=headers)


def disable_ldap(jwt: str, args: dict, settings: dict):
    base_url = args['url']

    headers = {
        'Authorization': f'Bearer {jwt}',
        'Host': args['host']
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
    res = request('PUT', f'{base_url}/api/settings', code=200,
                  json=settings, headers=headers)


def update_settings(jwt: str, args: dict) -> bool:
    base_url = args['url']

    headers = {
        'Authorization': f'Bearer {jwt}',
        'Host': args['host']
    }

    # Get settings
    res = request('GET', f'{base_url}/api/settings', code=200, headers=headers)

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

    return changed


def main():
    command = sys.argv[1]
    args = json.loads(sys.argv[2])

    commands = {
        'init': command_init
    }

    return commands[command](args)


if __name__ == '__main__':
    if main():
        print('Changed!')
