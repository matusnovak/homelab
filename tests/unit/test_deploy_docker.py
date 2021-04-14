import library.docker_deploy as library
import docker
import docker.errors
import time


def test_image_tokenization():
    image, tag = library.extract_image_and_tag('traefik:latest')

    assert image == 'traefik'
    assert tag == 'latest'

    image, tag = library.extract_image_and_tag(
        'docker.io/library/traefik:latest')

    assert image == 'docker.io/library/traefik'
    assert tag == 'latest'


def test_create_definition():
    # The following are the parameters we get from a role
    # They are in this structure so it is easier to write and read in
    # the role definition (main.yml) file
    params = {
        'host': 'unix://var/run/docker.sock',
        'project': 'example',
        'container': {
            'image': 'docker.io/library/traefik:latest',
            'name': 'traefik',
            'networks': [
                {
                    'name': 'default',
                    'alias': 'traefik'
                }
            ],
            'ports': [
                {
                    'host': '8080',
                    'guest': '80',
                    'protocol': 'tcp'
                },
                {
                    'host': '5000',
                    'guest': '5000',
                    'protocol': 'udp'
                },
                {
                    # Empty ports should not appear in the container definition below
                    'host': '',
                    'guest': '5000',
                    'protocol': 'tcp'
                }
            ],
            'volumes': [
                {
                    'host': '/tmp/traefik/config',
                    'guest': '/config',
                    'read_only': True
                },
                {
                    # Empty mounts should not appear in the container definition below
                    'host': '/tmp/traefik/data',
                    'guest': '',
                    'read_only': False
                }
            ],
            'labels': [
                {
                    'key': 'traefik.enable',
                    'value': 'true'
                },
                {
                    # Empty values should not appear in the container definition below
                    'key': 'traefik.http.routers.traefik.entrypoints',
                    'value': ''
                }
            ],
            'environment': [
                {
                    'key': 'TRAEFIK_CONFIG_PATH',
                    'value': '/config'
                },
                {
                    # Empty values should not appear in the container definition below
                    'key': 'TRAEFIK_DATA_PATH',
                    'value': ''
                }
            ]
        }
    }

    definition = library.create_definition(params)
    assert definition is not None

    assert definition['image'] == 'docker.io/library/traefik:latest'
    assert definition['name'] == 'example_traefik'

    assert 'default' in definition['networks']
    assert definition['networks']['default']['aliases'] == ['traefik']

    assert '80/tcp' in definition['ports']
    assert definition['ports']['80/tcp'] == '8080'
    assert '5000/udp' in definition['ports']
    assert definition['ports']['5000/udp'] == '5000'
    assert '5000/tcp' not in definition['ports']

    assert '/tmp/traefik/config' in definition['volumes']
    assert definition['volumes']['/tmp/traefik/config']['bind'] == '/config'
    assert definition['volumes']['/tmp/traefik/config']['mode'] == 'ro'
    assert '/tmp/traefik/data' not in definition['volumes']

    assert 'traefik.enable' in definition['labels']
    assert definition['labels']['traefik.enable'] == 'true'
    assert 'traefik.http.routers.traefik.entrypoints' not in definition['labels']

    assert 'TRAEFIK_CONFIG_PATH' in definition['environment']
    assert definition['environment']['TRAEFIK_CONFIG_PATH'] == '/config'
    assert 'TRAEFIK_DATA_PATH' not in definition['environment']


def test_pull_image():
    client = docker.from_env()

    library.pull_image(client, 'docker.io/library/ubuntu:18.04')


def test_add_image_vars():
    client = docker.from_env()

    library.pull_image(client, 'docker.io/library/traefik:v2.1')

    image = library.get_image(client, 'docker.io/library/traefik:v2.1')
    assert image is not None
    assert 'traefik:v2.1' in image.attrs['RepoTags']

    assert 'org.opencontainers.image.title' in image.attrs['Config']['Labels']
    assert image.attrs['Config']['Labels']['org.opencontainers.image.title'] == 'Traefik'

    definition = {
        'image': 'docker.io/library/traefik:v2.1',
        'networks': {
            'bridge': {
                'aliases': []
            }
        },
        'ports': {
            '80/tcp': '80'
        },
        'volumes': {
            '/tmp/traefik/config': '/config'
        },
        'labels': {
            'com.docker.compose.project': 'example',
            'org.opencontainers.image.title': 'Example'
        },
        'environment': {
            'WEB_PORT': '80'
        }
    }

    library.add_image_vars(image, definition)

    assert 'PATH' in definition['environment']
    assert definition['environment']['PATH'] == '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
    assert sorted(definition['environment'].keys()) == sorted([
        'PATH',
        'WEB_PORT'
    ])

    assert 'org.opencontainers.image.description' in definition['labels']
    assert 'org.opencontainers.image.title' in definition['labels']
    assert definition['labels']['org.opencontainers.image.title'] == 'Example'
    assert 'com.docker.compose.project' in definition['labels']
    assert definition['labels']['com.docker.compose.project'] == 'example'
    assert sorted(definition['labels'].keys()) == sorted([
        'org.opencontainers.image.description',
        'org.opencontainers.image.documentation',
        'org.opencontainers.image.title',
        'org.opencontainers.image.url',
        'org.opencontainers.image.vendor',
        'org.opencontainers.image.version',
        'com.docker.compose.project'
    ])


def test_deploy():
    client = docker.from_env()

    def container_exists(name: str) -> bool:
        try:
            client.containers.get('pytest_traefik')
            return True
        except docker.errors.NotFound:
            return False

    def container_stopped(name: str) -> bool:
        try:
            container = client.containers.get('pytest_traefik')
            return container.attrs['State']['Running'] == False
        except docker.errors.NotFound:
            return False

    params = {
        'host': 'unix://var/run/docker.sock',
        'tls_verify': False,
        'cert_path': None,
        'project': 'pytest',
        'container': {
            'image': 'docker.io/library/traefik:v2.1',
            'name': 'traefik',
            'networks': [{
                'name': 'bridge',
                'alias': ''
            }],
            'ports': [{
                'host': '5559',
                'guest': '80',
                'protocol': 'tcp'
            }],
            'volumes': [{
                'host': '/tmp/traefik-pytest',
                'guest': '/config',
                'read_only': True
            }],
            'labels': [{
                'key': 'com.docker.compose.test',
                'value': 'pytest'
            }],
            'environment': [{
                'key': 'HELLO',
                'value': 'World!'
            }]
        }
    }

    container_name = 'pytest_traefik'

    try:
        # Deploy the container, but only do checks
        res = library.deploy(True, params)
        assert res['changed'] == True
        assert container_exists(container_name) == False

        # Deploy the container, but this time do it for real
        assert 'host' in params
        res = library.deploy(False, params)
        assert res['changed'] == True
        assert container_exists(container_name) == True
        assert container_stopped(container_name) == False

        # Nothing should change
        res = library.deploy(False, params)
        assert res['changed'] == False
        assert container_exists(container_name) == True
        assert container_stopped(container_name) == False

        # Manually stop the container
        conatiner = client.containers.get(container_name)
        conatiner.stop()
        conatiner_id = conatiner.attrs['Id']
        assert conatiner_id == res['id']
        assert container_stopped(container_name) == True

        # Start the container, but only do checks
        # Container should stay stopped
        res = library.deploy(True, params)
        assert res['changed'] == True
        assert container_exists(container_name) == True
        assert container_stopped(container_name) == True

        # Start the container, but this time do it for real
        res = library.deploy(False, params)
        assert res['changed'] == True
        assert container_exists(container_name) == True
        assert container_stopped(container_name) == False

        conatiner = client.containers.get(container_name)
        assert conatiner_id == res['id']
        assert conatiner_id == conatiner.attrs['Id']

        # Nothing should change
        res = library.deploy(False, params)
        assert res['changed'] == False
        assert container_exists(container_name) == True

    finally:
        try:
            conatiner = client.containers.get(container_name)
            conatiner.stop()
            conatiner.remove()
        except docker.errors.NotFound:
            pass
