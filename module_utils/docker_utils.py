from docker.client import DockerClient
from docker.tls import TLSConfig
from docker.errors import NotFound
import socket
from contextlib import closing, contextmanager


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


PROXY_IMAGE = 'hpello/tcp-proxy'


def _create_proxy(params: dict, container_id: str, port: int):
    docker = DockerClient(
        base_url=params['host'],
        tls=TLSConfig(
            verify=params['tls_verify'],
            ca_cert=params['cert_path']
        )
    )

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


@contextmanager
def create_proxy(params: dict, container_id: str, port: int):
    proxy, port = _create_proxy(params, container_id, port)
    try:
        yield port
    finally:
        proxy.stop()
