import requests
import sys
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', type=int)
parser.add_argument('--username', dest='username', type=str)
parser.add_argument('--password', dest='password', type=str)


def expect(res, code: int):
    if res.status_code != code:
        print('Received status code: {} but expected: {}'.format(
            res.status_code, code), file=sys.stderr)
        print(res.text, file=sys.stderr)
        sys.exit('Request error')


def main():
    args = parser.parse_args()
    changed = False

    # Check if user has been created
    base_url = 'http://localhost:{}'.format(args.port)
    res = requests.get('{}/api/users/admin/check'.format(base_url))

    # 404 - admin has not been created
    # 204 - ok
    if res.status_code != 204:
        expect(res, 404)

        # Create user
        data = {
            'Username': args.username,
            'Password': args.password
        }
        res = requests.post(
            '{}/api/users/admin/init'.format(base_url), json=data)
        expect(res, 200)

        changed = True

    # Log in
    data = {
        'username': args.username,
        'password': args.password
    }
    res = requests.post('{}/api/auth'.format(base_url), json=data)
    expect(res, 200)

    jwt = res.json()['jwt']

    return dict(msg='Success', changed=changed)


if __name__ == '__main__':
    print(json.dumps(main()))
