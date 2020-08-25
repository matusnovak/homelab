# Homelab - Docs - Config

## 3. Environment variables

All of these variables are located in the sample `.env.sample` file. You will have to copy it and rename it to `.env` file. You will also have to modify the minimum necessary variables (such as your domain name). See the "required" section below. 

### 3.1. Required

These variables are required to be modified! Deployment will not work unless you modify them.

| Key | Example | Description |
| --- | ------- | ----------- |
| `DOMAIN_NAME` | `homelab.example.com` | This is the domain name that will be used for Traefik and all of your services. This domain name will also be used to generate the TLS certificates via Let's Encrypt. Each service is a subdomain of this domain, for example Traefik will be have traefik.homelab.example.com domain. |
| `DOMAIN_COMPONENT` | `dc=homelab,dc=example,dc=com` | This is a name of the LDAP domain. This should match your `DOMAIN_NAME` and must start with a `dc=...`. |
| `TLS_EMAIL` | `email@example.com` | An email to use for Let's Encrypt certificates, this is used by the Traefik proxy. |
| `HTTP_PORT` | `80` | The port to use for http by Traefik. |
| `HTTPS_PORT` | `443` | The port to use for https (and TLS) by Traefik. |
| `SUBNET_AND_MASK` | `172.18.0.0/16` | The subnet with a mask forthe docker network that will be used by all of the services for internal communication. Make sure this is an available subnet. If you are running a fresh install od Docker, and you have not created any networks, then this default subnet `172.18.0.0/16` will be available to you. |
| `ADMIN_PASSWORD` | `admin` | This is a master password that will be used for: OpenLDAP admin, Postgres master password and Postgres database passwords, Grafana admin, NextCloud admin, Traefik dashboard admin, and Adminer admin login. Make sure you use something secure! You can generate one by running the following command: `openssl rand -hex 16` |
| `AUTHELIA_JWT_SECRET` | `secret` | Any random string to use for Authelia JWT. You can generate one by running the following command: `openssl rand -hex 16`. |
| `AUTHELIA_SECRET` | `secret` | Any random string to use for Authelia. You can generate one by running the following command: `openssl rand -hex 16`. |


### 3.2. Optional

These variables can stay the same as in the `.env.sample`, **but it is hightly recommended that you will generate the secrets!** You don't need to modify these variables if you are not using these services. No need to set `NEXTCLOUD_DATA` if you are not using NextCloud, etc.

| Key | Example | Description |
| --- | ------- | ----------- |
| `NEXTCLOUD_DATA` | `/mount/external/nextcloud` | The path to an existing directory that will be used to store NextCloud files and configuration files. It is wise to use some large mounted drive in order to store large NextCloud user files. |
| `NEXTCLOUD_SHARE` | `/mount/external/share` | The path to optional shared directory, recommended to be used with [External Storage](https://docs.nextcloud.com/server/latest/admin_manual/configuration_files/external_storage_configuration_gui.html) |
| `JELLYFIN_MEDIA` | `/mount/external/share` | The path to an media folder with movies and tv shows for Jellyfin volume. |
| `GITEA_DATA` | `/mount/external/gitea` | The path to to use for Gitea volume to store repository data and configuration files. |
| `FILEBROWSER_MEDIA` | `/mount/external/share` | The path to to use for FileBrowser. The FileBrowser can be used to upload or download files from this path. Make sure this folder belongs to the user 1000 and group 1000. Running `sudo chown 1000:1000 /mount/external/share` and `sudo chmod 755 /mount/external/share` will do it. |
| `CLOUDFLARED_IP` | `172.18.255.1` - default | This is a static IP address that will be used by the Cloudflared service. Make sure this is a valid IP address based on the **SUBNET_AND_MASK**. Use an IP address from the top of the subnet range. Don't use `172.18.0.2` or similar one. |
| `OPENPROJECT_SECRET_KEY` | `secret` | Any random string to use for NextCloud. You can generate one by running the following command: `openssl rand -hex 16`. |
| `ARIA2_SECRET_KEY` | `secret` | Any random string to use for Aria2. You can generate one by running the following command: `openssl rand -hex 16`. |
| `TVHEADEND_RECORDINGS` | `/mount/external/recordings` | Where the recordings from TV Head will be stored. |
| `NEKO_DOWNLOADS` | `/mount/external/downloads` | Where Neko will store the downloads. |
| `TRANSMISSION_DOWNLOADS` | `/mount/external/downloads` | Where Transmission will store the downloads. |
| `QBITTORRENT_DOWNLOADS` | `/mount/external/downloads` | Where qBittorrent saves the data. |
| `QBITTORRENT_VPN_USERNAME` | `user` | Username for VPN inside qBittorrent container. |
| `QBITTORRENT_VPN_PASSWORD` | `password` | Password for VPN inside qBittorrent container. |

Plus a lot of `*_VERSION` variables. Feel free to set explicit version to them. They are used by the `docker-compose.<stackname>.yml` files as versions for the Docker images.
