from ansible.module_utils.basic import AnsibleModule
from docker.errors import NotFound, ContainerError
import docker
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
        '-c',
        '\"' + params['query'] + '\"',
        params['database']
    ]

    client = docker.from_env()
    container_id = params['container']

    try:
        container = client.containers.get(container_id)

        code, output = container.exec_run(' '.join(args), environment={
            'PGPASSWORD': params['password']
        })

        if code != 0:
            return dict(failed=True, msg=output.decode("utf-8"))

        reader = csv.reader(StringIO(output.decode("utf-8")), delimiter=',')
        results = []
        for row in reader:
            results.append(row)
        return dict(msg='Success', result=results)

    except ContainerError as e:
        return dict(failed=True, msg=str(e))
    except NotFound as e:
        return dict(failed=True, msg=f'No such container: {container_id}')


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
        'database': {
            'type': 'str',
            'required': False,
            'default': 'postgres'
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

    module.exit_json(**execute(module.params))


if __name__ == '__main__':
    main()
