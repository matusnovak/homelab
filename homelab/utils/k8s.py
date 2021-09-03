import json
import click
from typing import List, Tuple, Dict, Union
from kubernetes import client, config


def dict_deep_compare(d1: dict, d2: dict) -> bool:
    return json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


def is_same_dict(a: dict, b: dict) -> bool:
    return dict_deep_compare(a, b)


def is_same_service_port(a: client.V1ServicePort, b: client.V1ServicePort) -> bool:
    return a.port == b.port and a.name == b.name and a.protocol == b.protocol


def is_same_service_ports(a: List[client.V1ServicePort], b: List[client.V1ServicePort]) -> bool:
    if len(a) != len(b):
        return False

    for port in a:
        found = False
        for t in b:
            if is_same_service_port(port, t):
                found = True
                break
        if not found:
            return False
    return True


def is_same_service_spec(a: client.V1ServiceSpec, b: client.V1ServiceSpec) -> bool:
    return a.type == b.type and \
        is_same_dict(a.selector, b.selector) and \
        is_same_service_ports(a.ports, b.ports)


class K8s:
    def __init__(self, config_file: str):
        configuration = client.Configuration()
        config.load_kube_config(config_file=config_file,
                                client_configuration=configuration)
        self.client = client.ApiClient(configuration=configuration)
        self.core = client.CoreV1Api(self.client)

    # def list_node(self) -> List[client.V1Node]:
    #    return self.core.list_node().items

    def get_pod(self, namespace: str, name: str) -> Union[client.V1Pod, None]:
        field_selector = f'metadata.name={name}'
        items = self.core.list_namespaced_pod(
            namespace=namespace, field_selector=field_selector).items
        if len(items):
            return items[0]
        return None

    # def list_namespace(self) -> List[client.V1Namespace]:
    #    return self.core.list_namespace().items

    def get_namespace(self, name: str) -> Union[client.V1Namespace, None]:
        field_selector = f'metadata.name={name}'
        items = self.core.list_namespace(field_selector=field_selector).items
        if len(items):
            return items[0]
        return None

    def create_namespace(self, name: str) -> Tuple[client.V1Namespace, bool]:
        click.echo(
            f'Creating namespace \'{name}\'... ', nl=False)

        try:
            metadata = client.V1ObjectMeta(name=name)
            body = client.V1Namespace(metadata=metadata)

            item = self.get_namespace(name)

            if item is None:
                item = self.core.create_namespace(body=body)
                click.secho(f'Created!', fg='yellow')
                return item, True

            click.secho(f'Ok!', fg='green')
            return item, False
        except Exception as e:
            click.secho('Failed!', fg='red')
            raise e

    def get_config_map(self, namespace: str, name: str) -> Union[client.V1ConfigMap, None]:
        field_selector = f'metadata.name={name}'
        items = self.core.list_namespaced_config_map(namespace,
                                                     field_selector=field_selector).items
        if len(items):
            return items[0]
        return None

    def create_config_map(self, namespace: str, name: str, data: Dict[str, str]) -> Tuple[client.V1ConfigMap, bool]:
        click.echo(
            f'Creating config map \'{namespace}/{name}\'... ', nl=False)

        try:
            metadata = client.V1ObjectMeta(name=name, namespace=namespace)
            body = client.V1ConfigMap(metadata=metadata, data=data)

            item = self.get_config_map(namespace, name)

            if item is None:
                item = self.core.create_namespaced_config_map(
                    namespace, body=body)
                click.secho('Created!', fg='yellow')
                return item, True

            if not dict_deep_compare(data, item.data):
                item = self.core.patch_namespaced_config_map(
                    name, namespace, body)
                click.secho('Updated!', fg='yellow')
                return item, True

            click.secho('Ok!', fg='green')
            return item, False
        except Exception as e:
            click.secho('Failed!', fg='red')
            raise e

    def get_service(self, namespace: str, name: str) -> Union[client.V1Service, None]:
        field_selector = f'metadata.name={name}'
        items = self.core.list_namespaced_service(namespace,
                                                  field_selector=field_selector).items
        if len(items):
            return items[0]
        return None

    def create_service(self, namespace: str, name: str, ports: client.V1ServicePort, type: str) -> Tuple[client.V1Service, bool]:
        click.echo(
            f'Creating service \'{namespace}/{name}\'... ', nl=False)

        try:
            spec = client.V1ServiceSpec()
            spec.ports = ports
            spec.type = type
            spec.selector = {'app': name}

            labels = {'app': name}
            metadata = client.V1ObjectMeta(
                name=name, namespace=namespace, labels=labels)
            body = client.V1Service(metadata=metadata, spec=spec)

            item = self.get_service(namespace, name)

            if item is None:
                item = self.core.create_namespaced_service(
                    namespace, body=body)
                click.secho(f'Created!', fg='yellow')
                return item, True

            if not is_same_service_spec(item.spec, spec):
                item = self.core.patch_namespaced_service(
                    name, namespace, body=body)
                click.secho(f'Updated!', fg='yellow')
                return item, True

            click.secho(f'Ok!', fg='green')
            return item, False
        except Exception as e:
            click.secho('Failed!', fg='red')
            raise e

    def get_service_account(self, namespace: str, name: str) -> Union[client.V1ServiceAccount, None]:
        field_selector = f'metadata.name={name}'
        items = self.core.list_namespaced_service_account(namespace,
                                                          field_selector=field_selector).items
        if len(items):
            return items[0]
        return None

    def create_service_account(self, namespace: str, name: str) -> Tuple[client.V1ServiceAccount, bool]:
        click.echo(
            f'Creating service account \'{namespace}/{name}\'... ', nl=False)

        try:
            labels = {'app': name}
            metadata = client.V1ObjectMeta(
                name=name, namespace=namespace, labels=labels)
            body = client.V1ServiceAccount(metadata=metadata)

            item = self.get_service_account(namespace, name)

            if item is None:
                item = self.core.create_namespaced_service_account(body=body)
                click.secho(f'Created!', fg='yellow')
                return item, True

            click.secho(f'Ok!', fg='green')
            return item, False
        except Exception as e:
            click.secho('Failed!', fg='red')
            raise e
