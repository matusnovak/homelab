# Homelab

## Description

TODO

## Apps

TODO

## Deploy

Edit `site.yml` and select what apps you want to use. You will have to modify configuration files for each app accordingly in the `group_vars/homelab/*.yml` files. After that, simply deploy with:

```
ansible-playbook site.yml -v --ask-become-pass
```
