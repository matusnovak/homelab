---
weight: 2
title: "Folder Structure"
---

# Deploy - Folder Structure

## Data folder

All of the persistent data created and used by all of the apps will be located in a single folder defined by `data_dir` variable.

For example, NextCloud will use the following folders:

* `{{ data_dir }}/nextcloud/html`
* `{{ data_dir }}/nextcloud/apps`
* `{{ data_dir }}/nextcloud/config`
* `{{ data_dir }}/nextcloud/theme`

Each app will have its own subfolder. Portainer goes into `portainer`, all Matrix services go into `matrix`, and so on. The name of the subfolder matches the Ansible "rule" of the app. This makes it easier to run backups. (TODO: describe backup options).

For the purpose of this example, we will set variable `data_dir` to `"/homelab/data"`. You will have to create that folder yourself!

```bash
$ sudo mkdir /homelab
$ sudo chown 1000:1000 /homelab
$ mkdir /homelab/data 
```

## Git Repository

Next, you will have to clone this repository somewhere in your system.

Ansible works in a way that you can have all of the configurations located in some local workstation and it will be deployed into some remote server. For the purpose of this example, **we will use the same machine to run the Ansible and to deploy the services into** (i.e. everything is on localhost). Read here for more information: https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html

Clone this repository into your desired folder. We will use `/homelab/repo` as the destination.

```bash
$ cd /homelab 
$ git clone https://github.com/matusnovak/homelab.git repo
# Now you have /homelab/repo
```

{{< hint info >}}
**Note**

All of the configuration (i.e. Ansible variables) will be stored in this repository in the `group_vars/homelab` folder. Don't remove this repository.
{{< /hint >}}

## Next

**[Configuration]({{< ref "configuration.md" >}})**

