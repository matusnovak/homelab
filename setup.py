#!/usr/bin/env python3

from string import Template
from typing import List
import bcrypt
import glob
import os
import sys
import re
import shutil

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
SALT = bcrypt.gensalt()
#UID = os.getuid()
UID = 1000


def load_env(path: str) -> dict:
    env = {}

    with open(path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            elif line:
                while line.endswith('\n'):
                    line = line[:-1]
                if line:
                    tokens = line.split('=', 1)
                    if len(tokens) == 2:
                        env[tokens[0].strip()] = tokens[1].strip()
    return env


def get_files(path: str, pattern: str) -> List[str]:
    return glob.iglob(path + pattern, recursive=True)


def copy(dst: str, env: dict, uid=UID, gid=UID, mode=0o644) -> str:
    src = os.path.join(ROOT_DIR, 'templates', dst)
    dst = os.path.join(ROOT_DIR, 'data', dst)
    if not os.path.exists(dst):
        with open(src, 'r') as s:
            with open(dst, 'w') as d:
                t = Template(s.read())
                d.write(t.substitute(env))
            os.chmod(dst, mode)
            os.chown(dst, uid, gid)


def touch(dst: str, uid=UID, gid=UID, mode=0o644):
    dst = os.path.join(ROOT_DIR, 'data', dst)
    if not os.path.exists(dst):
        open(dst, 'w').close()
        os.chmod(dst, mode)
        os.chown(dst, uid, gid)


def mkdir(dst: str, uid=UID, gid=UID, mode=0o755):
    dst = os.path.join(ROOT_DIR, 'data', dst)
    if not os.path.exists(dst):
        os.makedirs(dst, mode)
        os.chown(dst, uid, gid)


def create_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), SALT).decode('utf-8')


def main():
    env = load_env(os.path.join(ROOT_DIR, '.env'))
    env['ADMIN_PASSWORD_HASH'] = create_password(env['ADMIN_PASSWORD'])

    mkdir('ldap/config')
    mkdir('ldap/data')
    mkdir('ldap/ldif')
    copy('ldap/ldif/all.ldif', env)

    mkdir('nextcloud/apps')
    mkdir('nextcloud/config')
    mkdir('nextcloud/html')
    mkdir('nextcloud/theme')

    mkdir('portainer/data')

    mkdir('postgres/data')
    mkdir('postgres/init')
    copy('postgres/init/services.sql', env)

    mkdir('mongo/data')

    mkdir('static')
    copy('static/index.html', env)

    mkdir('traefik')
    mkdir('traefik/config')
    touch('traefik/acme.json', mode=0o600)
    copy('traefik/traefik.yml', env)
    copy('traefik/usersfile', env)
    copy('traefik/config/middlewares.yml', env)
    copy('traefik/config/routers.yml', env)

    mkdir('haste')

    mkdir('prometheus/data')
    mkdir('prometheus/config')
    copy('prometheus/config/prometheus.yml', env)
    copy('prometheus/config/alerts.yml', env)

    mkdir('alertmanager/config')
    copy('alertmanager/config/alertmanager.yml', env)

    mkdir('grafana/data')
    mkdir('grafana/provisioning/datasources')
    mkdir('grafana/config')
    copy('grafana/provisioning/datasources/prometheus.yml', env)
    copy('grafana/config/grafana.ini', env)
    copy('grafana/config/ldap.toml', env)

    mkdir('jellyfin/config')
    mkdir('jellyfin/cache')
    mkdir('jellyfin/transcode')

    mkdir('filebrowser/config')
    mkdir('filebrowser/data')
    copy('filebrowser/config/filebrowser.json', env)

    mkdir('openproject/assets')

    mkdir('rocket/uploads')

    mkdir('onlyoffice/log')
    mkdir('onlyoffice/data')

    mkdir('drone')

    mkdir('artifactory', uid=1030, gid=1030)


if __name__ == '__main__':
    main()
