from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.errors import NotFound, ContainerError
import json
from io import StringIO
import csv


def execute(params: dict) -> dict:
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

    docker = DockerClient(
        base_url=params['docker']
    )

    try:
        container = docker.containers.get(params['container'])

        name = params['database']
        extra = params['extra']
        role = params['role']

        cmd = query(
            f'SELECT * FROM pg_catalog.pg_database WHERE datname = \'{name}\';')

        code, output = container.exec_run(cmd, environment={
            'PGPASSWORD': params['password']
        })

        if code != 0:
            return dict(failed=True, msg=output.decode("utf-8"))

        rows = decode(output)

        if len(rows) == 1:
            return dict(changed=False, msg='Success')

        cmd = query(f'CREATE DATABASE {name} {extra};')
        code, output = container.exec_run(cmd, environment={
            'PGPASSWORD': params['password']
        })

        if code != 0:
            return dict(failed=True, msg=output.decode("utf-8"))

        cmd = query(f'GRANT ALL PRIVILEGES ON DATABASE {name} TO {role};')
        code, output = container.exec_run(cmd, environment={
            'PGPASSWORD': params['password']
        })

        if code != 0:
            return dict(failed=True, msg=output.decode("utf-8"))

        return dict(changed=True, msg='Success')

    except ContainerError as e:
        return dict(failed=True, msg=str(e))
    except NotFound as e:
        return dict(failed=True, msg='No such container')


def main():
    module_args = {
        'docker': {
            'type': 'str',
            'required': True
        },
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
        'database': {
            'type': 'str',
            'required': True
        },
        'extra': {
            'type': 'str',
            'required': False,
            'default': ''
        },
        'role': {
            'type': 'str',
            'required': True
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    module.exit_json(**execute(module.params))


if __name__ == '__main__':
    main()
