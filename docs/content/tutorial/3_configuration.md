---
title: 3. Configuration
weight: 30
---

These variables are located in the `.env` file. A sample `.env.sample` is provided in the root folder of the repository.

{{% notice note %}}
Make sure you configure these variables! The default values are only as an example. The deployment will not work unless you change them.
{{% /notice %}}

#### DOMAIN_NAME

(example: `homelab.example.com`) This is the domain name that will be used for Traefik and all of your services. This domain name will also be used to generate the TLS certificates via Let's Encrypt.

#### DOMAIN_COMPONENT

(example: `dc=homelab,dc=example,dc=com`) This is a name of the LDAP domain. This should match your `DOMAIN_NAME` and must start with a `dc=...`. 

#### TLS_EMAIL

(example: `email@example.com`) An email to use for Let's Encrypt certificates, this is used by the Traefik proxy.

#### HTTP_PORT

(example: `80`) The port to use for http by Traefik.

#### HTTPS_PORT

(example: `443`) The port to use for https (and TLS) by Traefik.

#### SUBNET_AND_MASK

(example: `172.18.0.0/16`) The subnet with a mask forthe docker network that will be used by all of the services for internal communication. Make sure this is an available subnet. If you are running a fresh install od Docker, and you have not created any networks, then this default subnet `172.18.0.0/16` will be available to you.

#### ADMIN_PASSWORD

(example: `admin`) This is a master password that will be used for: OpenLDAP admin, Postgres master password and Postgres database passwords, Grafana admin, NextCloud admin, Traefik dashboard admin, and Adminer admin login. Make sure you use something secure! You can generate one by running the following command: `openssl rand -hex 16`

#### NEXTCLOUD_DATA

(example: `/mount/external/nextcloud`) The path to an existing directory that will be used to store NextCloud files and configuration files. It is wise to use some large mounted drive in order to store large NextCloud user files.

#### JELLYFIN_MEDIA

(example: `/mount/external/share`) The path to an media folder with movies and tv shows for Jellyfin volume. 

#### GITEA_DATA

(example: `/mount/external/gitea`) The path to to use for Gitea volume to store repository data.

#### FILEBROWSER_MEDIA

(example: `/mount/external/share`) The path to to use for FileBrowser. The FileBrowser can be used to upload or download files from this path. Make sure this folder belongs to the user 1000 and group 1000. Running `sudo chown 1000:1000 /mount/external/share` and `sudo chmod 755 /mount/external/share` will do it.

#### CLOUDFLARED_IP

(example: `172.18.255.1`) This is a static IP address that will be used by the Cloudflared service. Make sure this is a valid IP address based on the **SUBNET_AND_MASK**. Use an IP address from the top of the subnet range. Don't use `172.18.0.2` or similar one. 

#### OPENPROJECT_SECRET_KEY

Any random string to use for NextCloud. You can generate one by running the following command: `openssl rand -hex 16`.
