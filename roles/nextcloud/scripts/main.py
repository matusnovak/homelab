import requests
import sys
import json
import re
import urllib3


session = requests.Session()


def request(method: str, url: str, code: int = None, json=None, data=None, headers=None):
    print(f'{method} {url}')
    res = session.request(method, url, json=json,
                          data=data, headers=headers, verify=False, allow_redirects=False)
    if code is not None and res.status_code != code:
        msg = f'{method} {url} received status code: {res.status_code} but expected: {code} response: {res.text}'
        raise Exception(msg)
    return res


def get_token(html: str):
    m = re.findall(
        'data-requesttoken=\\"([A-Za-z0-9\+\-\=\:\/]+)\\"', html, re.M)
    assert len(m) > 0
    return m[0]


def login(args: dict) -> str:
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    res = request('GET', f'{base_url}/login', code=200, headers=headers)

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
        'User-Agent': 'Mozilla/5.0',
        'Host': args['host']
    }

    res = request('POST', f'{base_url}/login', data=data,
                  code=303, headers=headers)

    return session


def query_apps(args: dict):
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    res = request('GET', f'{base_url}/settings/apps',
                  code=200, headers=headers)

    token = get_token(res.text)

    headers = {
        'requesttoken': token,
        'Host': args['host']
    }

    res = request('GET', f'{base_url}/settings/apps/list',
                  code=200, headers=headers)

    return res.json()['apps']


def enable_app(args: dict, name: str):
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    res = request('GET', f'{base_url}/settings/apps',
                  code=200, headers=headers)

    headers = {
        'requesttoken': get_token(res.text),
        'Host': args['host']
    }

    data = {
        'appIds': [name],
        'groups': []
    }

    res = request('POST', f'{base_url}/settings/apps/enable',
                  json=data, code=200, headers=headers)


def configure_ldap(args: dict):
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    res = request('GET', f'{base_url}/settings/admin/ldap',
                  code=200, headers=headers)

    headers = {
        'requesttoken': get_token(res.text),
        'Host': args['host']
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

        request('POST', f'{base_url}/apps/user_ldap/ajax/wizard.php',
                data=data, code=200, headers=headers)

    post_action('save', 'ldap_host', args['ldap']['host'])
    post_action('save', 'ldap_port', args['ldap']['port'])
    post_action('save', 'ldap_dn', args['ldap']['user'])
    post_action('save', 'ldap_agent_password', args['ldap']['password'])
    post_action('save', 'ldap_base', args['ldap']['base'])
    post_action('countInBaseDN')

    post_action('save', 'ldap_experienced_admin', '1')
    post_action('save', 'ldap_display_name', 'cn')

    filter = args['ldap']['filter']
    post_action('save', 'ldap_userlist_filter', filter)

    login_filter = f'(&(objectClass=inetOrgPerson){filter}(uid=%uid))'
    post_action('save', 'ldap_login_filter', login_filter)

    post_action('save', 'ldap_group_filter', '(objectClass=top)')

    post_action('determineGroupMemberAssoc')
    post_action('countGroups')

    post_action('save', 'ldap_configuration_active', '1')


def disable_app(args: dict, name: str):
    base_url = args['url']

    res = request('GET', f'{base_url}/settings/apps', code=200)

    headers = {
        'requesttoken': get_token(res.text),
        'Host': args['host']
    }

    data = {
        'appIds': [name],
        'groups': []
    }

    request('POST', f'{base_url}/settings/apps/disable',
            json=data, code=200, headers=headers)


def configure_onlyoffice(args: dict):
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    res = request(
        'GET', f'{base_url}/settings/admin/onlyoffice', code=200, headers=headers)

    headers = {
        'requesttoken': get_token(res.text),
        'Host': args['host']
    }

    data = {
        'documentserver': args['onlyoffice']['address'],
        'documentserverInternal': args['onlyoffice']['internal'],
        'storageUrl': args['onlyoffice']['storage'],
        'verifyPeerOff': 'true',
        'secret': args['onlyoffice']['password'],
        'demo': 'false'
    }

    request('PUT', f'{base_url}/apps/onlyoffice/ajax/settings/address',
            data=data, code=200, headers=headers)


def command_init(args: dict) -> dict:
    changed = False

    login(args)

    apps = query_apps(args)

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

    if 'ldap' in args and not ldap_found:
        raise Exception('No LDAP app found in NextCloud, possibly a bug')
    if 'onlyoffice' in args and not onlyoffice_found:
        raise Exception('No OnlyOffice app found in NextCloud, possibly a bug')

    if not ldap_active and 'ldap' in args:
        changed = True
        ldap_active = True
        enable_app(args, 'user_ldap')

    elif ldap_active and 'ldap' not in args:
        changed = True
        disable_app(args, 'user_ldap')

    if ldap_active and 'ldap' in args:
        configure_ldap(args)

    if not onlyoffice_active and 'onlyoffice' in args:
        changed = True
        onlyoffice_active = True
        enable_app(args, 'onlyoffice')

    elif onlyoffice_active and 'onlyoffice' not in args:
        changed = True
        disable_app(args, 'onlyoffice')

    if onlyoffice_active and 'onlyoffice' in args:
        configure_onlyoffice(args)

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
