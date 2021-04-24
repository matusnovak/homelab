from ansible.module_utils.basic import AnsibleModule
import docker
from docker.errors import NotFound, ContainerError
import time
from io import StringIO
import csv


def execute(params: dict, tries: int = 5) -> dict:
    args = [
        'psql',
        '-U',
        params['user'],
        '-t',
        '-A',
        '-F","',
        '-c'
    ]

    def query(q: str):
        return ' '.join(args) + '\"' + q + '\"'

    def decode(output: str) -> list:
        reader = csv.reader(StringIO(output.decode("utf-8")), delimiter=',')
        results = []
        for row in reader:
            results.append(row)
        return results

    client = docker.from_env()

    try:
        container = client.containers.get(params['container'])

        role = params['role']
        role_password = params['role_password']

        cmd = query(
            f'SELECT * FROM pg_catalog.pg_roles WHERE rolname = \'{role}\';')

        code, output = container.exec_run(cmd, environment={
            'PGPASSWORD': params['password']
        })

        if code != 0:
            return dict(failed=True, msg=output.decode("utf-8"))

        rows = decode(output)

        if len(rows) == 1:
            return dict(changed=False, msg='Success')

        queries = [
            f'CREATE ROLE {role};'
            f'ALTER ROLE {role} WITH PASSWORD \'{role_password}\';'
            f'ALTER ROLE {role} WITH LOGIN;'
        ]

        code, output = container.exec_run(query(' '.join(queries)), environment={
            'PGPASSWORD': params['password']
        })

        if code != 0:
            return dict(failed=True, msg=output.decode("utf-8"))

        return dict(changed=True, msg='Success')

    except ContainerError as e:
        could_not_connect = 'could not connect to server' in str(e)
        starting_up = 'the database system is starting up' in str(e)
        if (could_not_connect or starting_up) and tries > 0:
            time.sleep(2)
            return execute(params, tries - 1)

        return dict(failed=True, msg=str(e), tries=tries)
    except NotFound as e:
        return dict(failed=True, msg='No such container')


def main():
    module_args = {
        'container': {
            'type': 'str',
            'required': True
        },
        'user': {
            'type': 'str',
            'required': False,
            'default': 'postgres'
        },
        'password': {
            'type': 'str',
            'required': True,
            'no_log': True
        },
        'role': {
            'type': 'str',
            'required': True
        },
        'role_password': {
            'type': 'str',
            'required': True,
            'no_log': True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    module.exit_json(**execute(module.params))


if __name__ == '__main__':
    main()
