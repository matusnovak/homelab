---
title: Portainer
---

![Screenshot](../images/portainer.png)

* **Official website:** <https://www.portainer.io/>
* **Homelab url:** `https://portainer.DOMAIN_NAME/`
* **Authentication:** Can be logged in via administrator account created during configuration or via LDAP.
* **Stack name:** `base` (deployed via `./deploy.sh base`).

### Description

Making Docker Management Easy. Build and manage your Docker environments with ease today.

-- portainer.io

### Configuration

{{% notice info %}}
Before configuring the LDAP authentication, make sure you have created at least one user via the phpLdapAdmin and added that user to the "portainer" group. [**Read here how to add a new LDAP user.**]({{< ref "phpldapadmin.md" >}})
{{% /notice %}}

First create the administrator account. You are free to choose any username or password.

![Screenshot](../images/portainer_setup_0.png)

Next, you should automatically see the the Docker endpoint with ~10 running containers.

![Screenshot](../images/portainer_setup_1.png)

To setup LDAP authentication, navigate to Settings -> Authentication and click "LDAP" from the middle column.

![Screenshot](../images/portainer_setup_2.png)

Next, specify the LDAP server hostname followed by a port, reader credentials, and a password. Don't forget to test the connectivity too.

* **LDAP Server:** Must be exactly `openldap:389`. This is the hostname to the OpenLDAP Docker container within the internal Docker network. The `openldap` resolves to `172.18.0.X`.
* **Anonymous mode:** Off
* **Reader DN:** `cn=admin,DOMAIN_COMPONENT`. This is the login DN as specified in the [**phpLdapAdmin documentation.**]({{< ref "phpldapadmin.md" >}})
* **Password:** This is the password used by the reader and it is the password `ADMIN_PASSWORD` from `.env` file.

![Screenshot](../images/portainer_setup_3.png)

For the LDAP security leave everything to Off. The LDAP communication happens only within the Docker network and there is no outside access to that. There would be no point doing TLS anyway.

* **Use StartTLS:** Off
* **Use TLS:** Off
* **Skip verification of server certificate:** Off

![Screenshot](../images/portainer_setup_4.png)

Enable automatic user provisioning. The Portainer will automatically create users if a new user logs in based on LDAP user credentials.

* **Automatic user provisioning:** On

![Screenshot](../images/portainer_setup_5.png)

Finally, you will need to set the Base DN to the organisation unit of `users` from LDAP. LDAP Users are created in organisational unit `ou=users,DOMAIN_COMPONENT` (For example: `ou=users,dc=example,dc=homelab,dc=com`). You don't need to fill in the group details because that feature is only useful in Portainer Enterprise mode (you need a license).

* **Base DN:** Must be set to `ou=users,DOMAIN_COMPONENT`.
* **Username:** Must be set to `uid`.
* **Filter:** Must be set to `(memberOf=cn=portainer,ou=groups,DOMAIN_COMPONENT)`.

![Screenshot](../images/portainer_setup_6.png)

**That's all.**

### Making users administrators

To make the user (that has logged in via LDAP credentials) an administrator, simply go to the Settings -> Users, select the correct user, and set the "Administrator" to On. If the user is not visible in the list of users, make sure the user has logged in at least once.

