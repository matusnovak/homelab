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


def command_init(args: dict) -> bool:
    base_url = args['url']

    data = {
        'username': args['username'],
        'password': args['password'],
        'recaptcha': ''
    }

    headers = {
        'Host': args['host']
    }

    res = request('POST', f'{base_url}/api/login', json=data, headers=headers)

    if res.status_code == 200:
        print('Admin user already configured')
        return False

    data = {
        'username': 'admin',
        'password': 'admin',
        'recaptcha': ''
    }
    res = request('POST', f'{base_url}/api/login',
                  code=200, json=data, headers=headers)

    xauth = res.text

    data = {
        "what": "user",
        "which": ["all"],
        "data": {
            "id": 1, "username": args['username'],
            "password": args['password'],
            "scope": ".",
            "locale": "en",
            "lockPassword": False,
            "viewMode": "mosaic",
            "singleClick": False,
            "perm": {
                "admin": True,
                "execute": True,
                "create": True,
                "rename": True,
                "modify": True,
                "delete": True,
                "share": True,
                "download": True
            },
            "commands": [],
            "sorting": {
                "by": "name",
                "asc": False
            },
            "rules": [],
            "hideDotfiles": False
        }
    }

    headers = {
        'X-Auth': xauth,
        'Host': args['host']
    }

    res = request('PUT', f'{base_url}/api/users/1',
                  code=200, json=data, headers=headers)
    print('Configured admin user')
    return True


def main():
    command = sys.argv[1]
    args = json.loads(sys.argv[2])

    commands = {
        'init': command_init
    }

    return commands[command](args)


if __name__ == '__main__':
    changed = main()
    if changed:
        print('Changed!')
