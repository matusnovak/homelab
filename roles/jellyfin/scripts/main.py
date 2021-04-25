import requests
import sys
import json

PLUGIN_LDAP_NAME = 'LDAP-Auth'


def request(method: str, url: str, code: int, json=None, data=None, headers=None):
    print(f'{method} {url}')
    res = requests.request(method, url, json=json,
                           data=data, headers=headers, verify=False)
    if res.status_code != code:
        msg = f'{method} {url} received status code: {res.status_code} but expected: {code} response: {res.text}'
        raise Exception(msg)
    return res


def is_setup_done(args: dict) -> bool:
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    res = request('GET', f'{base_url}/System/Info/Public',
                  code=200, headers=headers)

    return res.json()['StartupWizardCompleted']


def get_auth_header(token: str):
    return f'MediaBrowser Client="Jellyfin Setup", Device="Ansible", DeviceId="Ansible", Version="0.1.0", Token="{token}"'


def get_headers(token: str, host: str):
    return {
        'X-Emby-Authorization': get_auth_header(token),
        'Host': host
    }


def do_setup(args: dict):
    base_url = args['url']

    # This can be changed later anyway
    data = {
        'MetadataCountryCode': 'US',
        'PreferredMetadataLanguage': 'en',
        'UICulture': 'en-US'
    }

    headers = {
        'Host': args['host']
    }

    res = request(
        'POST', f'{base_url}/Startup/Configuration', code=204, json=data, headers=headers)

    res = request('GET', f'{base_url}/Startup/User',
                  code=200, json=data, headers=headers)

    data = {
        'Name': args['username'],
        'Password': args['password']
    }

    res = request('POST', f'{base_url}/Startup/User',
                  code=204, json=data, headers=headers)

    data = {
        'MetadataCountryCode': 'US',
        'PreferredMetadataLanguage': 'en',
        'UICulture': 'en-US'
    }

    res = request(
        'POST', f'{base_url}/Startup/Configuration', code=204, json=data, headers=headers)

    data = {
        'EnableAutomaticPortMapping': False,
        'EnableRemoteAccess': True
    }

    res = request(
        'POST', f'{base_url}/Startup/RemoteAccess', code=204, json=data, headers=headers)

    res = request('POST', f'{base_url}/Startup/Complete',
                  code=204, headers=headers)


def do_login(args: dict) -> str:
    base_url = args['url']

    username = args['username']

    data = {
        'Username': args['username'],
        'Pw': args['password']
    }

    headers = {
        'Host': args['host'],
        'Content-Type': 'application/json',
        'X-Emby-Authorization': f'MediaBrowser UserId="{username}", Client="Jellyfin Setup", Device="Ansible", DeviceId="Ansible", Version="0.1.0", Token=""'
    }

    res = request(
        'POST', f'{base_url}/Users/authenticatebyname', code=200, json=data, headers=headers)

    return res.json()['AccessToken']


def get_plugins(args: dict, token: str) -> list:
    base_url = args['url']

    headers = get_headers(token, args['host'])

    res = request('GET',
                  f'{base_url}/Plugins', code=200, headers=headers)

    return res.json()


def get_plugin_by_name(args: dict, token: str, name: str):
    plugins = get_plugins(args, token)

    for plugin in plugins:
        if plugin['Name'] == name:
            return plugin
    return None


def check_ldap_enabled(args: dict, token: str):
    plugin = get_plugin_by_name(args, token, PLUGIN_LDAP_NAME)
    if plugin is None:
        return False

    return plugin['Status'] == 'Active'


def check_ldap_installed(args: dict, token: str):
    plugin = get_plugin_by_name(args, token, PLUGIN_LDAP_NAME)
    if plugin is None:
        return False

    return True


def ldap_install(args: dict, token: str):
    base_url = args['url']

    headers = get_headers(token, args['host'])

    res = request('POST',
                  f'{base_url}/Packages/Installed/LDAP%20Authentication', code=204, headers=headers)


def setup_ldap(args: dict, token: str):
    if not check_ldap_installed(args, token):
        ldap_install(args, token)


def get_plugin_config(args: dict, token: str, plugin_id: str):
    base_url = args['url']

    headers = get_headers(token, args['host'])

    res = request('GET',
                  f'{base_url}/Plugins/{plugin_id}/Configuration', code=200, headers=headers)

    return res.json()


def check_ldap_config(args: dict, ldap_config: dict) -> bool:
    return (
        ldap_config['LdapServer'] == args['ldap']['host']
        and ldap_config['LdapPort'] == args['ldap']['port']
        and ldap_config['LdapBaseDn'] == args['ldap']['base']
        and ldap_config['LdapUsernameAttribute'] == args['ldap']['user_attribute']
        and ldap_config['LdapSearchAttributes'] == args['ldap']['user_attribute']
        and ldap_config['LdapSearchFilter'] == args['ldap']['filter']
        and ldap_config['LdapBindUser'] == args['ldap']['user']
        and ldap_config['LdapBindPassword'] == args['ldap']['password']
        and ldap_config['LdapAdminFilter'] == '(objectClass=JellyfinAdministrator)'
        and ldap_config['CreateUsersFromLdap'] == True
        and ldap_config['UseSsl'] == False
        and ldap_config['UseStartTls'] == False
        and ldap_config['SkipSslVerify'] == True
        and ldap_config['EnableCaseInsensitiveUsername'] == False
    )


def update_ldap_config(args: dict, token: str, plugin_id: str):
    base_url = args['url']

    headers = get_headers(token, args['host'])

    data = {
        'LdapServer': args['ldap']['host'],
        'LdapBaseDn': args['ldap']['base'],
        'LdapPort': args['ldap']['port'],
        'LdapSearchAttributes': args['ldap']['user_attribute'],
        'LdapUsernameAttribute': args['ldap']['user_attribute'],
        'LdapSearchFilter': args['ldap']['filter'],
        'LdapAdminFilter': '(objectClass=JellyfinAdministrator)',
        'LdapBindUser': args['ldap']['user'],
        'LdapBindPassword': args['ldap']['password'],
        'CreateUsersFromLdap': True,
        'UseSsl': False,
        'UseStartTls': False,
        'SkipSslVerify': True,
        'EnableCaseInsensitiveUsername': False,
        'LDAPServer': 'openldap'
    }

    res = request('POST',
                  f'{base_url}/Plugins/{plugin_id}/Configuration', code=204, json=data, headers=headers)


def command_ldap(args: dict) -> dict:
    changed = False

    token = do_login(args)

    plugin = get_plugin_by_name(args, token, PLUGIN_LDAP_NAME)
    if plugin is None:
        raise Exception('LDAP plugin is not installed')

    if plugin['Status'] != 'Active':
        raise Exception('LDAP plugin is not active')

    ldap_config = get_plugin_config(args, token, plugin['Id'])

    match = check_ldap_config(args, ldap_config)

    if not match:
        update_ldap_config(args, token, plugin['Id'])
        changed = True

    return changed


def command_init(args: dict) -> dict:
    changed = False

    if not is_setup_done(args):
        do_setup(args)
        changed = True

    token = do_login(args)

    ldap_enabled = check_ldap_enabled(args, token)

    if not ldap_enabled and 'ldap' in args:
        print('LDAP is not enabled, checking if LDAP plugin is enabled')
        if not check_ldap_installed(args, token):
            print('LDAP is not installed, installing it now')
            ldap_install(args, token)

        changed = True

    return changed


def main():
    command = sys.argv[1]
    args = json.loads(sys.argv[2])

    commands = {
        'init': command_init,
        'ldap': command_ldap
    }

    return commands[command](args)


if __name__ == '__main__':
    changed = main()
    if changed:
        print('Changed!')
