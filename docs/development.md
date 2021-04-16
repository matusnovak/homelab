# Homelab: Development

In order to create or update an application, you will have to do the following things:

* Create a new role for your application
* Create template files (if required) for configuration files
* Create role definition file with tasks that deploy the application

Each step is explained in this document below.

## Requirements

TODO

## Creating a role

TODO

## Creating template files

TODO

## Creating tasks

TODO

## Running it locally

Make sure your `hosts` file only contains your localhost. The following are the default contents:

```
[homelab]
127.0.0.1 ansible_connection=local
```

Create a new file named `dev.yml` and specify the role of your app you wish to work on. Example below:

```yml
---
- hosts: homelab
  roles:
    - nextcloud # Name of the role
```

You can use the following command to run Ansible with admin password at the same time. It is very recommended to use `--ask-become-pass` but you can use `ansible_become_pass=password` if you are too lazy like me. The `.vault_pass` is a password for `group_vars/homelab/vault.yml` which contains passwords.

```
ansible-playbook dev.yml -i hosts -v --extra-vars='ansible_become_pass=admin_password_here' --vault-password-file=.vault_pass
```
