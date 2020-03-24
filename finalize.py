#!/usr/bin/env python3

from typing import List
from utils.envfile import load_env
import requests
from requests.auth import HTTPBasicAuth
import os


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


def portainer(url: str, env: dict):
    username = env['ADMIN_USERNAME']
    password = env['ADMIN_PASSWORD']
    json = {
        'Username': username,
        'Password': password
    }
    r = requests.post(url=f'{url}/api/users/admin/init', json=json)
    if r.status_code != 200 and r.status_code != 409:
        r.raise_for_status()

    r = requests.post(url=f'{url}/api/auth', json=json)
    if r.status_code != 200:
        r.raise_for_status()
    jwt = r.json()['jwt']

    dc = env['DOMAIN_COMPONENT']
    json = {
        "LogoURL": "",
        "BlackListedLabels": [],
        "AuthenticationMethod": 2,
        "LDAPSettings": {
            "AnonymousMode": False,
            "ReaderDN": f"cn=admin,{dc}",
            "URL": "openldap:389",
            "TLSConfig": {
                "TLS": False,
                "TLSSkipVerify": True
            },
            "StartTLS": False,
            "SearchSettings": [{
                "BaseDN": f"ou=users,{dc}",
                "Filter": f"(memberOf=cn=traefik,ou=groups,{dc})",
                "UserNameAttribute": "uid"
            }],
            "GroupSearchSettings": [{
                "GroupBaseDN": "",
                "GroupFilter": "",
                "GroupAttribute": ""
            }],
            "AutoCreateUsers": True,
            "Password": password
        },
        "OAuthSettings": {
            "ClientID": "",
            "AccessTokenURI": "",
            "AuthorizationURI": "",
            "ResourceURI": "",
            "RedirectURI": "",
            "UserIdentifier": "",
            "Scopes": "",
            "OAuthAutoCreateUsers": False,
            "DefaultTeamID": 0
        },
        "AllowBindMountsForRegularUsers": True,
        "AllowPrivilegedModeForRegularUsers": True,
        "AllowVolumeBrowserForRegularUsers": False,
        "SnapshotInterval": "5m",
        "TemplatesURL": "",
        "EnableHostManagementFeatures": False,
        "EdgeAgentCheckinInterval": 5
    }
    headers = {
        'Authorization': f'Bearer {jwt}'
    }
    r = requests.put(url=f'{url}/api/settings', json=json, headers=headers)
    if r.status_code != 200:
        r.raise_for_status()


def main():
    env = load_env(os.path.join(ROOT_DIR, '.env'))
    domainame = env['DOMAIN_NAME']

    portainer(f'https://portainer.{domainame}', env)


if __name__ == '__main__':
    main()
