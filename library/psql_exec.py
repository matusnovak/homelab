from ansible.module_utils.basic import AnsibleModule
import psycopg2


def main():
    module_args = {
        'host': {
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

    connection = psycopg2.connect(
        host=module.params['host'],
        user=module.params['user'],
        password=module.params['password'],
        dbname=module.params['dbname'],
    )

    cursor = connection.cursor()
    assert cursor is not None

    try:
        cursor.execute(module.params['query'])
        result = cursor.fetchall()

        module.exit_json(msg='Success', result=result)
    except Exception as e:
        module.exit_json(failed=True, msg=str(e))


if __name__ == '__main__':
    main()
