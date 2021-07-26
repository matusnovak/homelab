#!/usr/bin/env python3

import argparse
import sys
import subprocess


def deploy(args):
    cmd = ['ansible-playbook', '--ask-become-pass', '-i', 'hosts', 'apps.yml',
           '--tags', args.app_name]
    if args.verbose:
        cmd += ['-v']
    proc = subprocess.run(cmd, stdin=sys.stdin,
                          stderr=sys.stderr, stdout=sys.stdout)

# TODO: add commands for: remove, purge, status, restart


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Homelab')
    subparsers = parser.add_subparsers(
        title='Subcommands', help='Action to perform')

    parser_deploy = subparsers.add_parser('deploy')
    parser_deploy.add_argument(
        '-a', '--app', dest='app_name', required=True, help='Name of the application to deploy')
    parser_deploy.add_argument(
        '-v', '--verbose', dest='verbose', required=False, action='store_true', help='Verbose output')
    parser_deploy.set_defaults(func=deploy)

    args = parser.parse_args()
    args.func(args)
