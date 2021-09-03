import click
import os
from homelab.commands import COMMAND_LIST


@click.group()
@click.pass_context
@click.option('-v', '--verbose', type=bool, default=False, help='Enable debug logging')
def cli(ctx, verbose):
    ctx.ensure_object(dict)


for cmd in COMMAND_LIST:
    name = cmd.__name__.split('.')[-1]
    cli.add_command(getattr(cmd, name))
