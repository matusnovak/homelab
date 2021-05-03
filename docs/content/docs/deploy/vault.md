---
weight: 4
title: "Vault"
---

# Deploy - Vault

## Ansible Vault

Ansible Vaults work just as any other YAML configuration file, except they are encrypted. More information here: https://docs.ansible.com/ansible/latest/user_guide/vault.html

## Create Vault

To create Vault, simply do the following:

```bash
$ cd /homelab
$ export EDITOR=nano
$ ansible-vault create repo/group_vars/homelab/vault.yml
```

You will be asked to type a new password for this vault. You will need this password if you want to deploy the apps or if you want to edit it.

{{< hint info >}}
**Note:**  

It is recommended that you store your passwords in here (admin passwords, databse passwords, jwt secrets, etc.)
{{< /hint >}}

## Edit Vault

Editing vault is done in the exact same way as creating one. Simply replace `create` with `edit`. You will need the original password you have used during creation.

```bash
$ cd /homelab
$ export EDITOR=nano
$ ansible-vault edit repo/group_vars/homelab/vault.yml
```

## Next

**[Ansible Playbook]({{< ref "playbook.md" >}})**

