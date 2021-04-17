import requests
import sys
import json


def expect(res, code: int):
    if res.status_code != code:
        print(f'Received status code: {res.status_code} but expected: {code}')
        print(res.text, file=sys.stderr)
        sys.exit('Request error')


def create_admin(args: dict) -> bool:
    base_url = args['url']

    data = {
        'username': args['username'],
        'password': args['password'],
        'recaptcha': ''
    }
    res = requests.post(f'{base_url}/api/login', json=data)

    if res.status_code == 200:
        return False

    data = {
        'username': 'admin',
        'password': 'admin',
        'recaptcha': ''
    }
    res = requests.post(f'{base_url}/api/login', json=data)
    expect(res, 200)

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
        'X-Auth': xauth
    }

    res = requests.put(f'{base_url}/api/users/1', json=data, headers=headers)
    expect(res, 200)
    return True


def command_init(args: dict) -> dict:
    changed = False

    # Check if admin needs password changing
    changed |= create_admin(args)

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
