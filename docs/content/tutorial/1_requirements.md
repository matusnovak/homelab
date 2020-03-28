---
title: 1. Requirements
weight: 10
---

**In order to install the services you will need the following:**

### System requirements

* Any Intel or AMD based 64-bit Linux distribution. Preferably an [Ubuntu](https://ubuntu.com/). Sorry, Raspberry Pi is not supported.
* At least 4GB of free memory
* At least 8GB of disk space

### Docker

You will also need [**Docker**](https://docs.docker.com/install/) and [**Docker Compose**](https://docs.docker.com/compose/install/). 

### Dependencies

Additionally, you will need Python3 and git. If you are on an Ubuntu, you can install them via: `sudo apt-get install -y python3 git`.

### Internet facing server and a domain

All of the services that can be accessed via a web browser will use a reverse proxy called [**Traefik**](https://containo.us/traefik/). In order for Traefik to properly configure TLS certificates via [**Lets' Encrypt**](https://letsencrypt.org/), it will need an open tcp port 80. This port 80 will be used to perform handshake. This also means that **you need to own a domain!**

