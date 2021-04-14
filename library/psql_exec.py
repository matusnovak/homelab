from ansible.module_utils.basic import AnsibleModule
import psycopg2
from docker.client import DockerClient
from docker.tls import TLSConfig
from docker.errors import NotFound
import socket
from contextlib import closing


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


PROXY_IMAGE = 'hpello/tcp-proxy'


def create_proxy(docker: DockerClient, container_id: str, port: int):
    # Find the container
    container = docker.containers.get(container_id)

    # Get the network alias
    networks = container.attrs['NetworkSettings']['Networks']
    network_names = list(networks.keys())

    # TODO: Choose the right network if more than one is present
    network_name = network_names[0]
    assert network_name is not None
    assert isinstance(network_name, str)

    # All containers have 12 alpha numeric alias
    # that is added into all attached networks
    alias = container.attrs['Id'][:12]

    # Find free port
    free_port = find_free_port()

    # Pull the proxy image
    try:
        docker.images.get(PROXY_IMAGE + ':latest')
    except NotFound:
        docker.images.pull(PROXY_IMAGE, 'latest')

    # Create proxy into the target container
    proxy = docker.containers.create(
        PROXY_IMAGE + ':latest',
        detach=True,
        command='{} {}'.format(alias, port),
        network=network_name,
        auto_remove=True,
        ports={
            '{}/tcp'.format(port): '{}'.format(free_port)
        },
        name='proxy'
    )
    proxy.start()

    return proxy, free_port


def exec(params: dict):
    docker = DockerClient(
        base_url=params['host'],
        tls=TLSConfig(
            verify=params['tls_verify'],
            ca_cert=params['cert_path']
        )
    )

    proxy, port = create_proxy(docker, params['container'], 5432)

    try:
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
    finally:
        proxy.stop()


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
