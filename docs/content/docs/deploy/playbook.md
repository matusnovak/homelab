---
weight: 5
title: "Ansible Playbook"
---

# Deploy - Ansible Playbook

## Before you begin

Before you deploy your Homelab, make sure you have done the following:

* Enabled Docker Swarm.
* **You are on the Swarm manager.**
* Set `data_dir` to your desired folder by overwriting it in group_vars.
* Set the desired domain name and domain component.
* Chosen the apps you wish to use by adding their roles into `site.yml`.
* Overwritten any default variables for the apps you wish to use.

## Run the Playbook

To deploy your apps, simply run the playbook using the following command:

```bash
$ cd /homelab/repo
$ ansible-playbook -i hosts site.yml --ask-become-pass --ask-vault-pass
```

After the Playbook has run, you should see the following:

```txt
PLAY RECAP ***********************************************************************
127.0.0.1                  : ok=18  changed=9    unreachable=0    failed=0    skipped=45   rescued=0    ignored=0
```

The `ok=18` means that the tasks have been successful. The `changed=9` means that some tasks have modified your system. Re-running your Playbook without changing any variables will produce `changed=0` (i.e. nothing has been modified).

**You are now able to access your apps!**

**To find out what subdomain to use to access your applications, and how to log in, go to the [Apps]({{< ref "../apps/_index.md" >}}) page.**

## Health check

If you want to check whether your application is alive and accessible, you can use the following curl command:

```bash
$ curl -v -k "https://localhost" -H "Host: nextcloud.yourdomain.name"
```

Simply replace `nextcloud` with the correct subdomain for your app. You need to provide the `Host` header so that Traefik knows where to forward your request to.

## Playbook tips

You can add `-v`, `-vv`, or `-vvv` into the `ansible-playbook` command line to see more verbose output. Note that this output will print out your passwords.

If you are re-running the playbook multiple times, you can create a file `vault.pass` with the Vault password in plaintext (no newlines) and then replace `--ask-vault-pass` with `--vault-password-file vault.pass`. This is NOT recommended but useful for debugging purposes.

You can also use `--extra-vars "ansible_become_pass=SudoPasswordHere"` instead of `--ask-become-pass`. This is NOT recommended but useful for debugging purposes.
