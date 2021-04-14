from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.docker_utils import create_proxy
import psycopg2


def exec(params: dict):
    with create_proxy(params, 5432) as port:
        connection = psycopg2.connect(
            host='localhost',
            user=params['user'],
            password=params['password'],
            dbname=params['dbname'],
            port=port
        )

        cursor = connection.cursor()
        assert cursor is not None

        try:
            cursor.execute(params['query'])
            result = cursor.fetchall()

            return dict(msg='Success', result=result)
        except Exception as e:
            return dict(failed=True, msg=str(e))


def main():
    module_args = {
        'host': {
            'type': 'str',
            'required': False,
            'default': 'unix://var/run/docker.sock'
        },
        'tls_verify': {
            'type': 'bool',
            'required': False,
            'default': False
        },
        'cert_path': {
            'type': 'str',
            'required': False,
            'default': None
        },
        'container': {
            'type': 'str',
            'required': True
        },
        'dbname': {
            'type': 'str',
            'required': True
        },
        'user': {
            'type': 'str',
            'required': True
        },
        'password': {
            'type': 'str',
            'required': True,
            'no_log': True
        },
        'query': {
            'type': 'str',
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    module.exit_json(**exec(module.params))


if __name__ == '__main__':
    main()
