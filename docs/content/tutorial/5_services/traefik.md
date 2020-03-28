---
title: Traefik
---

![Screenshot](../images/traefik.png)

* **Official website:** <https://containo.us/traefik/>
* **Homelab url:** `https://traefik.DOMAIN_NAME/dashboard/#/`
* **Authentication:** Basic auth using username `admin` and password `ADMIN_PASSWORD`.
* **Stack name:** `base` (deployed via `./deploy.sh base`).

### Description

Traefik serves as a reverse proxy that routes traffic from port 80 and port 443 (defined in `.env` file via `HTTP_PORT` and `HTTPS_PORT`) to the destination Docker container based on the URL rule. Traefik also exposes port 8080 (this port is exposed only to the internal Docker network) which serves the dashboard as seen in the screenshot above. This dashboard can be accessed by going to the address `https://traefik.DOMAIN_NAME/dashboard/#/` and authenticating as an administrator. The Traefik handles the routing, so you don't have to specify the internal port.

**No additional configuration needed!**
