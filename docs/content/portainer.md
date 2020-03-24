---
title: Portainer
weight: 20
---

### Description

![screenshot]()

The Portainer will be located at `https://portainer.{YOUR_DOMAIN}` (example: `https://portainer.example.com`). To log in, use the administrator username and password defined in the `.env` file.

Portainer also supports authentication via LDAP. To add a user, simply follow [this guide]().

### Troubleshooting

#### You do not have access to any environment

If you have created a user through LDAP and you get a warning "You do not have access to any environment. Please contact your administrator." then you must log in as the administrator (the one defined in `.env` file) and make this LDAP user an administrator. To do this, go to the "Users" settings page, click on the LDAP user, and toggle the "Administrator" button. If the LDAP user is not visible in the list of users on the settings page, make sure the user tries to log in at least once!

Alternatively, use the paid "Role-Based Access Control" extension.
