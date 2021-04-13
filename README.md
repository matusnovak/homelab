# Homelab

## Description

TODO

## Apps

**See [docs/apps.md](docs/apps.md) to see list of all available apps.**

## Deploy

Edit `homelab.yml` and select what apps you want to use. You will have to modify configuration files for each app accordingly in the `group_vars/homelab/*.yml` files.


After that, simply deploy with:

```
ansible-playbook site.yml -v --ask-become-pass
```
