import requests
import sys
import re
import argparse

APP_LDAP = 'user_ldap'
APP_ONLYOFFICE = 'onlyoffice'


class NextCloudClient:
    def __init__(self, address: str, host: str):
        self.address = address
        self.host = host
        self.session = requests.Session()

    def request(self, method: str, path: str, code: int = None, json=None, data=None, headers=None):
        url = f'{self.address}{path}'

        print(f'{method} {url}')

        default_headers = {
            'Content-type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0',
            'Host': self.host,
        }

        if not headers:
            headers = {}
        headers.update(default_headers)

        res = self.session.request(method, url, json=json,
                                   data=data, headers=headers, verify=False, allow_redirects=False)

        if code is not None and res.status_code != code:
            msg = f'{method} {url} received status code: {res.status_code} but expected: {code} response: {res.text}'
            raise Exception(msg)
        return res

    def get_token(self, html: str):
        m = re.findall(
            'data-requesttoken=\\"([A-Za-z0-9\\+\\-\\=\\:\\/]+)\\"', html, re.M)
        assert len(m) > 0
        return m[0]

    def login(self, username: str, password: str):
        res = self.request('GET', '/login', code=200)
        token = self.get_token(res.text)

        data = {
            'user': username,
            'password': password,
            'timezone': 'Europe/London',
            'timezone_offset': '0',
            'requesttoken': token
        }

        res = self.request('POST', f'/login', data=data, code=303)

        if not res.headers['location'].endswith('/apps/dashboard/'):
            raise Exception('Login failed, redirect is: {}'.format(res.headers['location']))

    def get_apps(self) -> list:
        res = self.request('GET', f'/settings/apps', code=200)
        token = self.get_token(res.text)

        headers = {
            'requesttoken': token,
        }

        res = self.request('GET', f'/settings/apps/list', code=200, headers=headers)

        return res.json()['apps']

    def enable_app(self, name: str):
        res = self.request('GET', f'/settings/apps', code=200)

        headers = {
            'requesttoken': self.get_token(res.text),
        }

        data = {
            'appIds': [name],
            'groups': []
        }

        res = self.request('POST', f'/settings/apps/enable', json=data, code=200, headers=headers)

    def disable_app(self, name: str):
        res = self.request('GET', f'/settings/apps', code=200)

        headers = {
            'requesttoken': self.get_token(res.text),
        }

        data = {
            'appIds': [name],
            'groups': []
        }

        self.request('POST', f'/settings/apps/disable', json=data, code=200, headers=headers)

    def is_app_enabled(self, name: str) -> bool:
        apps = self.get_apps()
        active = None

        for app in apps:
            if app['id'] == name:
                active = app['active']
                break

        if active is None:
            raise Exception(f'App {name} does not exist')

        return active

    def is_app_installed(self, name: str) -> bool:
        apps = self.get_apps()
        found = False

        for app in apps:
            if app['id'] == name:
                found = True
                break

        return found

    def enable_ldap(self, host: str, port: int, user: str, password: str, base: str, group: str):
        if not self.is_app_installed(APP_LDAP) or not self.is_app_enabled(APP_LDAP):
            print('Enabling LDAP')
            self.enable_app(APP_LDAP)

        print('Configuring LDAP')

        res = self.request('GET', f'/settings/admin/ldap', code=200)

        headers = {
            'requesttoken': self.get_token(res.text),
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

            self.request('POST', f'/apps/user_ldap/ajax/wizard.php',
                         data=data, code=200, headers=headers)

        post_action('save', 'ldap_host', host)
        post_action('save', 'ldap_port', port)
        post_action('save', 'ldap_dn', user)
        post_action('save', 'ldap_agent_password', password)
        post_action('save', 'ldap_base', base)
        post_action('countInBaseDN')

        post_action('save', 'ldap_experienced_admin', '1')
        post_action('save', 'ldap_display_name', 'cn')

        filter = f'(memberOf={group})'
        post_action('save', 'ldap_userlist_filter', filter)

        login_filter = f'(&(objectClass=inetOrgPerson){filter}(uid=%uid))'
        post_action('save', 'ldap_login_filter', login_filter)

        post_action('save', 'ldap_group_filter', '(objectClass=top)')

        post_action('determineGroupMemberAssoc')
        post_action('countGroups')

        post_action('save', 'ldap_configuration_active', '1')

    def disable_ldap(self):
        if self.is_app_enabled(APP_LDAP):
            print('Disabling LDAP')
            self.disable_app(APP_LDAP)

    def enable_onlyoffice(self, host: str, internal: str, storage: str, secret: str):
        if not self.is_app_installed(APP_ONLYOFFICE) or not self.is_app_enabled(APP_ONLYOFFICE):
            print('Enabling OnlyOffice')
            self.enable_app(APP_ONLYOFFICE)

        print('Configuring OnlyOffice')

        res = self.request('GET', f'/settings/admin/onlyoffice', code=200)

        headers = {
            'requesttoken': self.get_token(res.text),
        }

        data = {
            'documentserver': host,
            'documentserverInternal': internal,
            'storageUrl': storage,
            'verifyPeerOff': 'true',
            'secret': secret,
            'demo': 'false'
        }

        self.request('PUT', f'/apps/onlyoffice/ajax/settings/address', data=data, code=200, headers=headers)

    def disable_onlyoffice(self):
        if self.is_app_enabled(APP_ONLYOFFICE):
            print('Disabling OnlyOffice')
            self.disable_app(APP_ONLYOFFICE)


def main(args: dict):
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', type=str, required=True)
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--username', type=str, required=True)
    parser.add_argument('--password', type=str, required=True)
    parser.add_argument('--ldap-host', type=str, required=False)
    parser.add_argument('--ldap-port', type=int, required=False)
    parser.add_argument('--ldap-user', type=str, required=False)
    parser.add_argument('--ldap-password', type=str, required=False)
    parser.add_argument('--ldap-base', type=str, required=False)
    parser.add_argument('--ldap-group', type=str, required=False)
    parser.add_argument('--onlyoffice-host', type=str, required=False)
    parser.add_argument('--onlyoffice-internal', type=str, required=False)
    parser.add_argument('--onlyoffice-storage', type=str, required=False)
    parser.add_argument('--onlyoffice-secret', type=str, required=False)

    args = parser.parse_args(args)

    client = NextCloudClient(args.address, args.host)
    client.login(args.username, args.password)

    if args.ldap_host:
        client.enable_ldap(
            args.ldap_host,
            args.ldap_port,
            args.ldap_user,
            args.ldap_password,
            args.ldap_base,
            args.ldap_group)
    else:
        client.disable_ldap()

    if args.onlyoffice_host:
        client.enable_onlyoffice(
            args.onlyoffice_host,
            args.onlyoffice_internal,
            args.onlyoffice_storage,
            args.onlyoffice_secret)
    else:
        client.disable_onlyoffice()


if __name__ == '__main__':
    main(sys.argv[1:])
