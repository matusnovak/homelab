---
title: phpLdapAdmin
---

![Screenshot](../images/phpldapadmin.png)

* **Official website:** <http://phpldapadmin.sourceforge.net/wiki/index.php/Main_Page>
* **Homelab url:** `https://ldap.DOMAIN_NAME/`
* **Authentication:** Login is done via a "DN" and a password `ADMIN_PASSWORD`.
* **Stack name:** `base` (deployed via `./deploy.sh base`).

### Description

A web based LDAP browser to manage OpenLDAP server. You can use this web interface to create/edit/delete users and roles/groups.

### Login DN

The Login DN is a "distinguished name" and usually starts with a keyword such as "dc". In this case, in order to log-in, your login DN is a combination of `dc=admin` and `DOMAIN_COMPONENT` defined in your `.env` file. For example: `dc=admin,dc=example,dc=homelab,dc=com`.

### Creating a user

The LDAP groups and an admin account have been set up for you automatically. You don't have to do any additional configuration. To add a new user, all you have to do is to create a new user account in the `ou=users` group and then add this user to their respecive role (the group in `ou=groups`).

First, navigate to `ou=users,DOMAIN_COMPONENT` (for example: `ou=users,dc=example,dc=homelab,dc=com`) as shown in the screenshot below. Select the `ou=users`, click "Create child entry", and select **"Generic User Account"**.

![Screenshot](../images/phpldapadmin_createuser_0.png)

Next, fill in the details. Don't forget to specify GID Number to "user". This is a pre-created posix group with GID Number 500. You will also have to select "Login shell", which does not really mapper and you can simply choose "No Login".

![Screenshot](../images/phpldapadmin_createuser_1.png)

Finally, validate the attributes and click "Commit" button at the bottom.

![Screenshot](../images/phpldapadmin_createuser_2.png)

### Adding a user to role/group

To assign a user to a role/group, first navigate to the `ou=groups,DOMAIN_COMPONENT` (for example: `ou=groups,dc=example,dc=homelab,dc=com`) and click on the group you want to assign the user to. For the purpose of the example, we will assign the user to group "portainer".

![Screenshot](../images/phpldapadmin_assignuser_0.png)

Next, click on "Add value" at the bottom and then click on the magnifying glass icon next to the empty input field.

![Screenshot](../images/phpldapadmin_assignuser_1.png)

Next, find the user you want to add. **Make sure you clock on the [+] icon to see the children!**

![Screenshot](../images/phpldapadmin_assignuser_2.png)

![Screenshot](../images/phpldapadmin_assignuser_3.png)

![Screenshot](../images/phpldapadmin_assignuser_4.png)

Finally, click "Update Object" and "Commit".

![Screenshot](../images/phpldapadmin_assignuser_5.png)

![Screenshot](../images/phpldapadmin_assignuser_6.png)

**That's it! You can repeat this for any other role/group.**
