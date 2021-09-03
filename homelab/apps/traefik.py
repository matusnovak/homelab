from typing import List
from homelab.utils import App, K8s, Option, load_file
from kubernetes.client import V1ServicePort

options = [
    Option(key='traefik_image', value='docker.io/library/traefik:v2.4',
           help='Docker image name with repository and tag.'),
    Option(key='traefik_http_enabled', value=True,
           help='Enable HTTP listener.'),
    Option(key='traefik_https_enabled', value=True,
           help='Enable HTTPS listener.'),
    Option(key='traefik_log_level', value='DEBUG',
           help='Log level for the console output.'),
    Option(key='traefik_http_port', value=80,
           help='Port number for the HTTP listener.'),
    Option(key='traefik_https_port', value=443,
           help='Port number for the HTTPS listener.'),
    Option(key='traefik_acme_enabled', value=False,
           help='Let Traefik automatically create and renew TLS certificates, for example with Let\'s Encrypt.'),
    Option(key='traefik_acme_email', value='email@example.com',
           help='Email to be used for the ACME resolver.'),
    Option(key='traefik_acme_challenge', value='web',
           help='What type of challenge to use? Choose options from [web, web-secure, or dns]. More here: https://doc.traefik.io/traefik/https/acme/#dnschallenge'),
    Option(key='traefik_dns_challenge_provider', value='route53',
           help='Only used if traefik_acme_challenge is set to "dns". For example: route53. More here: https://doc.traefik.io/traefik/https/acme/#dnschallenge'),
    Option(key='traefik_metrics_enabled', value=True,
           help='Enable metrics for Prometheus and Grafana. Accessible by anyone from inside of the K8s network. You can limit outside access with Authelia.'),
    Option(key='traefik_dashboard_enabled', value=True,
           help='A web dashboard that users can access. Will show the current middlewares and routes that Traefik is using. Not used for configuration.'),
]


class Traefik(App):
    def __init__(self):
        self.name = 'traefik'
        self.options = options

    def get_dependencies(self) -> List[str]:
        return []

    def deploy(self, k8s: K8s, config: dict):
        namespace = config['project_name']

        traefik_config_changed = k8s.create_config_map(
            namespace, 'traefik-config',
            {'traefik.yml': load_file('traefik/traefik.yml.j2', config)})[1]

        k8s.create_service(
            namespace, 'traefik',
            ports=[
                V1ServicePort(
                    name='http', port=config['traefik_http_port'], protocol='TCP'),
                V1ServicePort(
                    name='https', port=config['traefik_https_port'], protocol='TCP')
            ],
            type='NodePort'
        )

        k8s.create_service_account(
            namespace, 'traefik-ingress-controller')


APP = Traefik
