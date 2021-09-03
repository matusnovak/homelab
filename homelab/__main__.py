import click
import traceback
from homelab.cli import cli


def main():
    try:
        cli(prog_name='homelab', obj={})
    except Exception as e:
        click.secho(f'Error: {e}', fg='red')
        traceback.print_exc()


if __name__ == '__main__':
    main()
