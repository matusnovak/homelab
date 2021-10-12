import os
import yaml
import sys
from typing import List
import subprocess


DATA_PATH = os.getenv('DATA_PATH', '/homelab')
CONFIG_PATH = os.getenv('CONFIG_PATH', f'{DATA_PATH}/config.yml')
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


def command(args: List[str]):
    p = subprocess.Popen(args, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, encoding='utf-8')
    while True:
        stdout = p.stdout.readline()
        if stdout == '' and p.poll() is not None:
            break
        if stdout != '':
            sys.stdout.write(stdout)
            sys.stdout.flush()

    p.stdout.close()
    rc = p.wait()
    if rc != 0:
        raise Exception(f'Command {args} returned code {rc}')


def install_crds(path: str):
    # Despite what Helm's documentation says about the
    # "crds" folder, it's bunch of lies. It does not work.
    # We have to do it ourselves.
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
        for dir in os.listdir(os.path.join(path, 'charts')):
            if dir not in config['deploy'] or config['deploy'][dir] != True:
                continue

            crds_folder = os.path.join(path, 'charts', dir, 'crds')
            if os.path.exists(crds_folder) and os.path.isdir(crds_folder):
                for file in os.listdir(crds_folder):
                    file_full = os.path.join(crds_folder, file)
                    if file.endswith('.yml') or file.endswith('.yaml'):
                        command(['kubectl', 'apply', '-f', file_full])


if __name__ == '__main__':
    install_crds(ROOT_DIR)
