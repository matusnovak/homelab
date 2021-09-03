from homelab.utils.config import config_merge_options
import click
from typing import List
from homelab.apps import APPS, APPS_NAMES, APPS_OPTIONS
from homelab.utils import App, K8s, BASE_OPTIONS


@click.command()
@click.pass_obj
@click.option('--k8s-config', type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True), default=None, help='Path to kubernetes config')
@click.option('-a', '--app', required=True, type=click.Choice(APPS_NAMES), help='Name of the application')
def deploy(ctx: dict, k8s_config: str, app: List[str]):
    #click.echo('hello world!')
    # for i in range(10):
    #    time.sleep(1)
    #    click.echo(f'\rHello {i}', nl=False)
    # click.echo('')

    k8s = K8s(config_file=k8s_config)
    config = config_merge_options(APPS_OPTIONS + BASE_OPTIONS, '')
    app = APPS[app]

    click.echo(f'Deploying app {app.name}...')
    k8s.create_namespace(config['project_name'])
    app.deploy(k8s, config)
