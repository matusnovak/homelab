#!/usr/bin/env python3

from string import Template
from typing import List
from utils.envfile import load_env
import bcrypt
import glob
import os
import sys
import re
import shutil

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
SALT = bcrypt.gensalt()


def get_files(path: str, pattern: str) -> List[str]:
    return glob.iglob(path + pattern, recursive=True)


def transform(src: str, env: dict) -> str:
    s = Template(src)
    return s.substitute(env)


def create_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), SALT).decode('utf-8')


# Transform template files and put them to the data directory
def do_templates(env: dict):
    templates = os.path.join(ROOT_DIR, 'templates')
    data = os.path.join(ROOT_DIR, 'data')
    files = get_files(templates, '**/**')

    for src in files:
        if src == templates:
            continue

        relative = src[len(templates) + 1:]
        dst = os.path.join(data, relative)

        if os.path.isdir(src):
            os.makedirs(dst, exist_ok=True)
        elif os.path.isfile(src):
            with open(src, 'r') as source:
                with open(dst, 'w') as target:
                    target.write(transform(source.read(), env))


# Copy files with their UID GID but only if they do not exists
def do_init():
    init = os.path.join(ROOT_DIR, 'init')
    data = os.path.join(ROOT_DIR, 'data')
    files = get_files(init, '**/**')

    for src in files:
        if src == init:
            continue

        relative = src[len(init) + 1:]
        dst = os.path.join(data, relative)

        if os.path.isdir(src) and not os.path.exists(dst):
            os.makedirs(dst, exist_ok=True)
            st = os.stat(src)
            os.chown(dst, st[os.stat.ST_UID], st[os.stat.ST_GID])

        if os.path.isfile(src) and not os.path.exists(dst):
            shutil.copy2(src, dst)
            st = os.stat(src)
            os.chown(dst, st[os.stat.ST_UID], st[os.stat.ST_GID])


def main():
    env = load_env(os.path.join(ROOT_DIR, '.env'))
    env['ADMIN_PASSWORD_HASH'] = create_password(env['ADMIN_PASSWORD'])

    do_templates(env)
    do_init()


if __name__ == '__main__':
    main()
