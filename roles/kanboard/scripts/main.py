import requests
import sys
import json
import re


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
        'name=\\"csrf_token\\"\s+value=\\"([A-Za-z0-9]+)\\"', html, re.M)
    assert len(m) > 0
    return m[0]


def command_init(args: dict) -> bool:
    base_url = args['url']

    headers = {
        'Host': args['host']
    }

    res = request('GET', f'{base_url}/login', code=200, headers=headers)
    token = get_token(res.text)

    data = {
        'username': args['username'],
        'password': 'admin',
        'csrf_token': token,
        'remember_me': '1'
    }

    res = request(
        'POST', f'{base_url}/?controller=AuthController&action=check', data=data, headers=headers)
    if res.status_code == 200:
        print('Admin user already configured')
        return False

    assert res.status_code == 302, "Expected HTTP 302"

    res = request('GET', f'{base_url}/user/1/password',
                  code=200, headers=headers)
    token = get_token(res.text)

    data = {
        'id': '1',
        'csrf_token': token,
        'current_password': 'admin',
        'password': args['password'],
        'confirmation': args['password']
    }

    res = request('POST', f'{base_url}/?controller=UserCredentialController&action=savePassword&user_id=1',
                  code=302, data=data, headers=headers)
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
