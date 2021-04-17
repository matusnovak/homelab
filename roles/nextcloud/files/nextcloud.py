import requests
import sys
import json
import re
import urllib3


def expect(res, code: int):
    if res.status_code != code:
        print(f'Received status code: {res.status_code} but expected: {code}')
        print(res.text, file=sys.stderr)
        sys.exit('Request error')


def get_token(html: str):
    m = re.findall(
        'data-requesttoken=\\"([A-Za-z0-9\+\-\=\:\/]+)\\"', html, re.M)
    assert len(m) > 0
    return m[0]


def login(args: dict) -> str:
    base_url = args['url']

    session = requests.Session()

    res = session.get(f'{base_url}/login', allow_redirects=False)
    expect(res, 200)

    token = get_token(res.text)

    data = {
        'user': args['username'],
        'password': args['password'],
        'timezone': 'Europe/London',
        'timezone_offset': '0',
        'requesttoken': token
    }

    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }

    res = session.post(f'{base_url}/login', data=data,
                       headers=headers, allow_redirects=False)
    expect(res, 303)

    return session


def query_apps(args: dict, session):
    base_url = args['url']

    res = session.get(f'{base_url}/settings/apps')
    expect(res, 200)

    token = get_token(res.text)

    headers = {
        'requesttoken': token
    }

    res = session.get(f'{base_url}/settings/apps/list', headers=headers)
    expect(res, 200)
    return res.json()['apps']


def enable_app(args: dict, session, name: str):
    base_url = args['url']

    res = session.get(f'{base_url}/settings/apps')
    expect(res, 200)

    headers = {
        'requesttoken': get_token(res.text)
    }

    data = {
        'appIds': [name],
        'groups': []
    }

    res = session.post(f'{base_url}/settings/apps/enable',
                       json=data, headers=headers)
    expect(res, 200)


def configure_ldap(args: dict, session):
    base_url = args['url']

    res = session.get(f'{base_url}/settings/admin/ldap')
    expect(res, 200)

    headers = {
        'requesttoken': get_token(res.text)
    }

    def post_action(action, key=None, value=None):
        if key is not None and value is not None:
            data = {
                'ldap_serverconfig_chooser': 's01',
                'action': action,
                'cfgkey': key,
                'cfgval': str(value)
            }
        else:
            data = {
                'ldap_serverconfig_chooser': 's01',
                'action': action
            }

        res = session.post(f'{base_url}/apps/user_ldap/ajax/wizard.php',
                           data=data, headers=headers)
        expect(res, 200)

    post_action('save', 'ldap_host', args['ldap']['host'])
    post_action('save', 'ldap_port', args['ldap']['port'])
    post_action('save', 'ldap_dn', args['ldap']['user'])
    post_action('save', 'ldap_agent_password', args['ldap']['password'])
    post_action('save', 'ldap_base', args['ldap']['base'])
    post_action('countInBaseDN')

    post_action('save', 'ldap_experienced_admin', '1')

    filter = args['ldap']['filter']
    post_action('save', 'ldap_userlist_filter', filter)

    login_filter = f'(&(objectClass=inetOrgPerson){filter}(uid=%uid))'
    post_action('save', 'ldap_login_filter', login_filter)

    post_action('save', 'ldap_group_filter', '(objectClass=top)')

    post_action('determineGroupMemberAssoc')
    post_action('countGroups')

    post_action('save', 'ldap_configuration_active', '1')


def disable_app(args: dict, session, name: str):
    base_url = args['url']

    res = session.get(f'{base_url}/settings/apps')
    expect(res, 200)

    headers = {
        'requesttoken': get_token(res.text)
    }

    data = {
        'appIds': [name],
        'groups': []
    }

    res = session.post(f'{base_url}/settings/apps/disable',
                       json=data, headers=headers)
    expect(res, 200)


def configure_onlyoffice(args: dict, session):
    base_url = args['url']

    res = session.get(f'{base_url}/settings/admin/onlyoffice')
    expect(res, 200)

    headers = {
        'requesttoken': get_token(res.text)
    }

    data = {
        'documentserver': args['onlyoffice']['address'],
        'documentserverInternal': args['onlyoffice']['internal'],
        'storageUrl': args['onlyoffice']['storage'],
        'verifyPeerOff': 'true',
        'secret': args['onlyoffice']['password'],
        'demo': 'false'
    }

    res = session.put(f'{base_url}/apps/onlyoffice/ajax/settings/address',
                      data=data, headers=headers)
    expect(res, 200)


def command_init(args: dict) -> dict:
    changed = False

    session = login(args)

    apps = query_apps(args, session)

    ldap_found = False
    ldap_active = False
    onlyoffice_found = False
    onlyoffice_active = False

    for app in apps:
        if app['id'] == 'user_ldap':
            ldap_found = True
            ldap_active = app['active']
        if app['id'] == 'onlyoffice':
            onlyoffice_found = True
            onlyoffice_active = app['active']

    if not ldap_found:
        return dict(failed=True, msg='No LDAP app found in NextCloud, possibly a bug')
    if not onlyoffice_found:
        return dict(failed=True, msg='No OnlyOffice app found in NextCloud, possibly a bug')

    if not ldap_active and 'ldap' in args:
        changed = True
        ldap_active = True
        enable_app(args, session, 'user_ldap')

    elif ldap_active and 'ldap' not in args:
        changed = True
        disable_app(args, session, 'user_ldap')

    if ldap_active and 'ldap' in args:
        configure_ldap(args, session)

    if not onlyoffice_active and 'onlyoffice' in args:
        changed = True
        onlyoffice_active = True
        enable_app(args, session, 'onlyoffice')

    elif onlyoffice_active and 'onlyoffice' not in args:
        changed = True
        disable_app(args, session, 'onlyoffice')

    if onlyoffice_active and 'onlyoffice' in args:
        configure_onlyoffice(args, session)

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
