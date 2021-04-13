from ansible.module_utils.basic import AnsibleModule
from urllib.request import Request, urlopen, HTTPError
import ssl
import time

# We have to use this custom script because the
# original Ansible's "uri" is shit for healthcheck purposes


def main():
    module_args = {
        'url': {
            'type': 'str',
            'required': True
        },
        'status_code': {
            'type': 'str',
            'required': True
        },
        'delay': {
            'type': 'int',
            'required': False,
            'default': 5
        },
        'retries': {
            'type': 'int',
            'required': False,
            'default': 3
        },
        'headers': {
            'type': 'list',
            'required': False,
            'default': []
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    tries = 0
    status_codes = set([])

    for code in module.params['status_code'].split(','):
        status_codes.add(int(code.strip()))

    last_error = 'Unexpected status code'

    while tries < module.params['retries']:
        try:
            req = Request(url=module.params['url'])

            for header in module.params['headers']:
                tokens = header.split(':', maxsplit=2)
                req.add_header(tokens[0].strip(), tokens[1].strip())

            with urlopen(req, context=ctx) as r:
                if r.getcode() in status_codes:
                    break
        except HTTPError as e:
            last_error = str(e)
            if e.code in status_codes:
                break

        except Exception as e:
            last_error = str(e)

        time.sleep(module.params['delay'])
        tries += 1

    if tries >= module.params['retries']:
        module.exit_json(failed=True, msg=last_error)

    module.exit_json(msg='Success')


if __name__ == '__main__':
    main()
