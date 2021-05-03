---
weight: 3
title: "Configuration"
---

# Deploy - Configuration

## Ansible Variables

Ansible uses variables to specify differences between systems. This project uses these variables to define properties such as: domain name, docker project (i.e. stack name), LDAP information, passwords, etc.

Each application has its own dedicated folder inside of `repo/roles/<name>/defaults/main.yml`. These variables define how the application will be deployed. Some applications depend on variables from other roles (for example, NextCloud depends on Traefik).

The default variables work "out of the box" and are tested on GitHub Actions every time some change is made to this project. Meaning, you don't have to modify them in order for your deployment to succeed.

However, you probably don't want a default domain name of `https://homelab.lan`. **You should go through the variables and override them depending on what you want!**. It is highly recommended that you first check `repo/roles/base/main.yml`!

{{< hint warning >}}
**Warning**  

Don't change the variables in `repo/roles/<name>/defaults/main.yml`. It is recommended that you "override" them in your `repo/group_vars/homelab/*.yml` files.
{{< /hint >}}

You can read more about Ansible variables here: https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html#playbooks-variables

## Select apps to deploy

In order to deploy your Homelab, you will have to create the following file:

```
repo/site.yml
```

That has the following format:

```yml
---
- hosts: homelab
  roles:
    - base
    - postgres
    - ldap
    # etc... name of the roles...

```

You must choose the apps you wish to deploy by simply adding the role name into the `roles:` list. **You must also ensure that all of the dependencies for your app are listed before your app!** For example, NextCloud depends on Traefik, LDAP, and Postgres. Therefore the `- nextcloud` must be listed **after** `- postgres \n - ldap \n - traefik`. 

**To find out what apps you can deploy, their role names, and their dependencies, head over to the [Apps]({{< ref "../apps/_index.md" >}}) page.**

{{< hint warning >}}
**Warning**  

Removing the role from the `repo/site.yml` will not remove the app (i.e. Docker service) from your host. Removing the role chages the configuration of some relevant apps, but it will not remove them. Additionally, removing the role does not remove the data for that app.

Removing files, databases, and Docker services must be done manually! Ansible will take care only for the configuration.

To read more about this, go to the **[Remove App]({{< ref "../maintenance/remove_app.md" >}})** page.
{{< /hint >}}

## Override default variables

To override the default variables, create a folder `repo/group_vars/homelab` and create a file `repo/group_vars/homelab/main.yml`. **This file will contain your variables** in a YAML syntax. Simply copy the key name (for example `domain_name:` from `repo/roles/base/main.yml`) and add it here & change the value.

You can create separate files in this directory. It is recommended that you use `main.yml` or `<role name>.yml` naming conventions.

You should at **minimum** override the following:

* `data_dir` - into `/homelab/data`
* `domain_name` - into your domain of your choosing
* `domain_component` - to match your domain (must be in form of `dc=example,dc=com`)


You should override the **passwords** in an **encrypted YAML** file. This encrypted file is called **Vault**. Head over to the next page to see how that is done.

## Next

**[Vault]({{< ref "vault.md" >}})**
