from ansible.module_utils.basic import AnsibleModule
import docker


def execute(params: dict) -> dict:
    client = docker.from_env()

    container = client.containers.get(params['container'])

    code, stdout = container.exec_run(params['args'], user=params['user'])

    if code != 0:
        return dict(failed=True, msg=f'Exit code {code}', output=stdout)

    return dict(msg='Success', output=stdout)


def main():
    module_args = {
        'container': {
            'type': 'str',
            'required': True,
        },
        'user': {
            'type': 'str',
            'required': False,
            'default': 'root'
        },
        'args': {
            'type': 'list',
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
