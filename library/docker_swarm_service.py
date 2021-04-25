from typing import Tuple
from ansible.module_utils.basic import AnsibleModule
from docker.client import DockerClient
from docker.errors import NotFound, ContainerError
from docker.types.services import EndpointSpec, RestartPolicy, ServiceMode, UpdateConfig, RollbackConfig, Resources, Placement
from docker.types import Healthcheck, NetworkAttachmentConfig, SecretReference, ConfigReference
import json
import docker
import time
import hashlib


DOCKER_CONFIG_HASH_LABEL = 'com.docker.stack.config-hash'
DOCKER_NAMESPACE_LABEL = 'com.docker.stack.namespace'
DOCKER_IMAGE_LBALE = 'com.docker.stack.image'


def get_defaults() -> dict:
    return {
        'image': None,
        'command': None,
        'args': None,
        'constraints': [],
        'preferences': [],
        'maxreplicas': None,
        'platforms': [],
        'container_labels': {},
        'endpoint_spec': None,
        'env': {},
        'hostname': None,
        'init': None,
        'isolation': None,
        'labels': {},
        'log_driver': None,
        'log_driver_options': {},
        'mode': None,
        'mounts': {},
        'name': None,
        'networks': None,
        'resources': None,
        'restart_policy': None,
        'secrets': [],
        'stop_grace_period': None,
        'update_config': None,
        'rollback_config': None,
        'user': None,
        'workdir': None,
        'tty': None,
        'groups': None,
        'open_stdin': None,
        'read_only': None,
        'stop_signal': None,
        'healthcheck': None,
        'hosts': None,
        'dns_config': None,
        'configs': [],
        'privileges': None
    }


def make_hash(definition: dict):
    return str(hashlib.md5(json.dumps(definition, sort_keys=True).encode('utf-8')).hexdigest())


def get_config_hash_value(service):
    labels = service.attrs['Spec']['Labels']
    if DOCKER_CONFIG_HASH_LABEL in labels:
        return labels[DOCKER_CONFIG_HASH_LABEL]
    return None


def deploy_service(client: DockerClient, project_name: str, name: str, definition: dict, timeout: int) -> Tuple[bool, dict]:
    defaults = get_defaults()

    env = []
    if 'environment' in definition and isinstance(definition['environment'], dict):
        for key, value in definition['environment'].items():
            if isinstance(value, str) and value != '':
                env.append(
                    f'{key}={value}'
                )

    def_restart_policy = definition.get('restart_policy', {})

    restart_policy = RestartPolicy(
        condition=def_restart_policy.get('condition', 'none'),
        delay=def_restart_policy.get('delay', 0),
        max_attempts=def_restart_policy.get('max_attempts', 0),
        window=def_restart_policy.get('window', 0)
    )

    def_deploy = definition.get('deploy', {})

    is_global = def_deploy.get('mode', 'replicated') == 'global'

    service_mode = ServiceMode(
        mode=def_deploy.get('mode', 'replicated'),
        replicas=definition.get('replicas', None if is_global else 1)
    )

    update_config = UpdateConfig(
        parallelism=0,
        order='stop-first'
    )

    rollback_config = RollbackConfig(
        parallelism=0,
        order='stop-first'
    )

    def_healthcheck = definition.get('healthcheck', {})

    def get_sec_to_nsec(s: str):
        if s.endswith('s'):
            return int(s[:-1]) * 1000 * 1000 * 1000
        else:
            return int(s)

    healthcheck = Healthcheck(
        test=def_healthcheck.get('test', []),
        interval=get_sec_to_nsec(str(def_healthcheck.get('interval', 0))),
        timeout=get_sec_to_nsec(str(def_healthcheck.get('timeout', 0))),
        retries=int(def_healthcheck.get('retries', 0)),
        start_period=get_sec_to_nsec(
            str(def_healthcheck.get('start_period', 0)))
    )

    def_resources = definition.get('resources', {})
    def_limits = def_resources.get('limits', {})
    def_reservations = def_resources.get('reservations', {})

    resources = Resources(
        cpu_limit=def_limits.get('cpus', None),
        mem_limit=def_limits.get('memory', None),
        cpu_reservation=def_reservations.get('cpus', None),
        mem_reservation=def_reservations.get('memory', None),
        generic_resources=def_reservations.get('generic', None)
    )

    def_placement = def_deploy.get('placement', {})

    def_constraints = def_placement.get('constraints', [])
    def_preferences = def_placement.get('preferences', [])

    preferences = []
    for items in def_preferences:
        for key, value in items.items():
            preferences.append((key, value))

    container_labels = {
        DOCKER_NAMESPACE_LABEL: project_name
    }

    if 'labels' in definition and isinstance(definition['labels'], list):
        for label in definition['labels']:
            if isinstance(label, tuple):
                if label[1] != '':
                    container_labels[label[0]] = label[1]
            elif isinstance(label, str):
                tokens = label.split('=', maxsplit=2)
                if label[1] != '':
                    container_labels[tokens[0]] = tokens[1]

    labels = {
        DOCKER_NAMESPACE_LABEL: project_name,
        DOCKER_IMAGE_LBALE: definition['image']
    }

    if 'labels' in def_deploy and isinstance(def_deploy['labels'], list):
        for label in def_deploy['labels']:
            if isinstance(label, tuple):
                if label[1] != '':
                    labels[label[0]] = label[1]
            elif isinstance(label, str):
                tokens = label.split('=', maxsplit=2)
                if label[1] != '':
                    labels[tokens[0]] = tokens[1]

    ports = {}

    if 'ports' in definition and isinstance(definition['ports'], list):
        for port in definition['ports']:
            if isinstance(port, str):
                host_port, guest_port = port.split(':', maxsplit=2)
                guest_port, protocol = guest_port.split('/', maxsplit=2)

                ports[host_port] = (
                    int(guest_port),
                    protocol if protocol is not None else 'tcp',
                    'ingress'
                )
            elif isinstance(port, dict):
                host_port = port['published']
                guest_port = port['target']

                ports[host_port] = (
                    int(guest_port),
                    port.get('protocol', 'tcp'),
                    port.get('mode', 'ingress')
                )

    endpoint_spec = EndpointSpec(
        mode='vip',
        ports=ports
    )

    networks = []
    for network in definition.get('networks', []):
        if isinstance(network, str):
            networks.append(NetworkAttachmentConfig(
                target=network,
                aliases=[name],
                options={}
            ))

    secrets = []
    for secret in definition.get('secrets', []):
        def get_secret(secret_name: str) -> tuple:
            found = client.secrets.list(filters={
                'name': secret_name
            })
            assert len(found) == 1, "No secret named: {secret_name} found."
            return (found[0].id, found[0].name)

        if isinstance(secret, str):
            secret_id, secret_name = get_secret(secret)
            secrets.append(SecretReference(
                secret_id=secret_id,
                secret_name=secret_name,
                filename=None,
                uid='0',
                gid='0',
                mode=444
            ))

    configs = []
    for config in definition.get('configs', []):
        def get_config(config_name: str) -> tuple:
            found = client.configs.list(filters={
                'name': config_name
            })

            cl = []
            for c in client.configs.list():
                cl.append(c.name)

            assert len(
                found) == 1, f"No config named: {config_name} found. All configs: {cl}."
            return (found[0].id, found[0].name)

        if isinstance(config, str):
            config_id, config_name = get_config(config)
            configs.append(ConfigReference(
                config_id=config_id,
                config_name=config_name,
                filename=None,
                uid='0',
                gid='0',
                mode=444
            ))
        if isinstance(config, dict):
            config_id, config_name = get_config(config['source'])
            configs.append(ConfigReference(
                config_id=config_id,
                config_name=config_name,
                filename=config['target'],
                uid=str(config.get('uid', 0)),
                gid=str(config.get('gid', 0)),
                mode=int(config.get('mode', 444))
            ))

    volumes = []
    for volume in definition.get('volumes', []):
        if isinstance(volume, str) and volume != '':
            volumes.append(volume)

    full_name = f'{project_name}_{name}'

    args = {
        'image': definition['image'],
        'command': definition.get('command', None),
        'hostname': definition.get('hostname', None),
        'user': definition.get('user', None),
        'constraints': def_constraints,
        'preferences': preferences,
        'maxreplicas': def_placement.get('max_replicas_per_node', None),
        'container_labels': container_labels,
        'labels': labels,
        'endpoint_spec': endpoint_spec,
        'networks': networks,
        'args': definition.get('args', None),
        'name': full_name,
        'labels': labels,
        'mounts': volumes,
        'env': env,
        'restart_policy': restart_policy,
        'mode': service_mode,
        'update_config': update_config,
        'rollback_config': rollback_config,
        'healthcheck': healthcheck,
        'resources': resources,
        'secrets': secrets,
        'configs': configs
    }

    defaults.update(args)
    args = defaults

    args_hash = make_hash(args)

    service = None
    changed = False

    args['labels'][DOCKER_CONFIG_HASH_LABEL] = args_hash

    try:
        service = client.services.get(full_name)

        service_hash = get_config_hash_value(service)

        if service_hash is None or service_hash != args_hash:
            changed = True

    except NotFound:
        changed = True

    if changed and service is None:
        del args['rollback_config']
        service = client.services.create(**args)

    elif changed and service is not None:
        del args['rollback_config']
        service.update(**args)

    # wait
    tasks = []

    while timeout > 0:
        timeout -= 1

        tasks = service.tasks(filters={
            'desired-state': 'running'
        })

        if len(tasks) == 0:
            time.sleep(1)
            continue

        all_running = True
        for task in tasks:
            if task['Status']['State'] != 'running':
                all_running = False
                break

        if not all_running:
            time.sleep(1)
            continue

        break

    if timeout <= 0 or len(tasks) == 0:
        msg = f'Timeout while waiting for service: {full_name} to have at least one task running'
        return (changed, dict(failed=True, msg=msg))

    tasks_meta = []
    for task in tasks:
        tasks_meta.append({
            'task_id': task['ID'],
            'id': task['Status']['ContainerStatus']['ContainerID'],
            'status': task['Status']['State'],
            'exit_code': task['Status']['ContainerStatus']['ExitCode'],
            'node': task['NodeID']
        })
        # tasks_meta.append(task)

    meta = {
        'name': name,
        'id': service.attrs['ID'],
        'full_name': full_name,
        'tasks': tasks_meta
    }

    return (changed, meta)


def deploy(project_name: str, definition: dict, timeout: int) -> dict:
    changed = False
    results = {}
    client = docker.from_env()

    for name, value in definition.items():
        ch, result = deploy_service(client, project_name, name, value, timeout)
        changed |= ch
        results[name] = result

        if 'failed' in result:
            return dict(**result)

    return dict(changed=changed, msg='Success', services=results)


def wait_for_tasks(client: DockerClient, full_name: str, timeout: int, expected: int):
    while timeout > 0:
        timeout -= 1

        containers = client.containers.list(filters={
            'name': full_name + '.'
        })

        if len(containers) == expected:
            return

        for container in containers:
            print(f'container is alive: {container.id}')

        time.sleep(1)

    if timeout <= 0:
        raise Exception(
            f'Timeout while waiting for number of replicas of service: {full_name} to be {expected}')


def remove_service(client: DockerClient, project_name: str, name: str, timeout: int) -> bool:
    try:
        full_name = f'{project_name}_{name}'
        service = client.services.get(full_name)

        service.remove()

        wait_for_tasks(client, full_name, timeout, 0)

        return (False, True, 'Service removed')

    except NotFound:
        return (False, False, 'Service not found')


def remove(project_name: str, names: list, timeout: int) -> dict:
    changed = False
    client = docker.from_env()

    for name in names:
        failed, ch, msg = remove_service(client, project_name, name, timeout)
        if failed:
            return dict(failed=True, msg=msg)
        else:
            changed |= ch

    return dict(changed=changed, msg='Services removed')


def restart_service(client: DockerClient, project_name: str, name: str, timeout: int) -> bool:
    try:
        full_name = f'{project_name}_{name}'
        service = client.services.get(full_name)

        num_of_replicas = service.attrs['Spec']['Mode']['Replicated']['Replicas']

        # Scale down first
        service.scale(0)
        wait_for_tasks(client, full_name, timeout, 0)

        # Scale up back
        # We have to try multiple times because of a bug in Docker that has been
        # there for past 5 years and no one is fixing it.
        service = client.services.get(full_name)
        tries = 3
        while tries > 0:
            tries -= 1
            try:
                service.scale(num_of_replicas)
                break
            except Exception as e:
                if tries == 0 or 'update out of sequence' not in str(e):
                    raise e
                time.sleep(1)

        # Double check that all replicas have started
        wait_for_tasks(client, full_name, timeout, num_of_replicas)

        return (False, True, 'Service restarted')

    except NotFound:
        return (False, False, 'Service not found')


def restart(project_name: str, names: list, timeout: int) -> dict:
    changed = False
    client = docker.from_env()

    for name in names:
        failed, ch, msg = restart_service(client, project_name, name, timeout)
        if failed:
            return dict(failed=True, msg=msg)
        else:
            changed |= ch

    return dict(changed=changed, msg='Services restarted')


def main():
    module_args = {
        'project_name': {
            'type': 'str',
            'required': True
        },
        'timeout': {
            'type': int,
            'required': False,
            'default': 30
        },
        'definition': {
            'type': 'dict',
            'required': False,
            'default': None
        },
        'remove': {
            'type': 'list',
            'required': False,
            'default': []
        },
        'restart': {
            'type': 'list',
            'required': False,
            'default': []
        }
    }

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if len(module.params['remove']) > 0:
        module.exit_json(
            **remove(module.params['project_name'], module.params['remove'], module.params['timeout']))

    if len(module.params['restart']) > 0:
        module.exit_json(
            **restart(module.params['project_name'], module.params['restart'], module.params['timeout']))

    if module.params['definition'] is not None:
        module.exit_json(
            **deploy(module.params['project_name'], module.params['definition'], module.params['timeout']))


if __name__ == '__main__':
    main()
