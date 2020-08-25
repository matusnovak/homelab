# Homelab - Docs - Install

## 1. Requirements

### 1.1. System requirements

* Any Intel or AMD based 64-bit Linux distribution. Preferably an [Ubuntu](https://ubuntu.com/). Sorry, Raspberry Pi is not supported.
* At least 4GB of free memory
* At least 8GB of disk space

### 1.2. Docker

You will also need [**Docker**](https://docs.docker.com/install/) and [**Docker Compose**](https://docs.docker.com/compose/install/). 

### 1.3. Dependencies

Additionally, you will need Python3 (with bcrypt) and git. If you are on an Ubuntu, you can install them via:

```bash
sudo apt-get install -y python3 python3-pip git
python3 -m pip install bcrypt
```

### 1.4. Internet facing server and a domain

All of the services that can be accessed via a web browser will use a reverse proxy called [**Traefik**](https://containo.us/traefik/). In order for Traefik to properly configure TLS certificates via [**Lets' Encrypt**](https://letsencrypt.org/), it will need an open tcp port 80. This port 80 will be used to perform handshake. This also means that **you need to own a domain!**

## 2. Installation

### 2.1. Clone

Clone this repository.

```sh
git clone https://github.com/matusnovak/homelab.git
cd homelab
```

### 2.2. Configure environment variables

You will need to provide basic configuration via environment variables. These variables will be used by the Docker Compose to deploy the services. A sample configuration file is provided inside of the root directory of the repository called `.env.sample`. 

Note! Make sure you can see hidden files in your OS. Files starting with a dot in their filenames are considered hidden.

Copy the `.env.sample` to `.env` and edit the variables. **Read the [config.md](config.md) documentation to see what variables you need to modify.**

### 2.3. Create data folder with config files

After you have configured the `.env` file you will need to setup the configuration files and folder structure. All you have to do is to run the `setup.py` script as the root. This script will create your initial `./data` folder based on your modified `.env` file and files from `./templates` folder. This will set up most of the configuration files for all of the services, but some manual configuration will be needed.

**You need to modify your .env file before running this command!**

```bash
sudo ./setup.py
```

### 2.4. Deploy the base stack

All of the services in this Homelab depend on the **"base" stack**. This base stack contains services such as Mongo database, Traefik reverse proxy, and all of the common things that are needed for other things.

```
./deploy.sh base
```

After this is deployed, you should be able to access:

* https://portainer.your-domain.com/ - Service [Portainer](https://www.portainer.io/) - a docker user interface.
* https://traefik.your-domain.com/ - Service [Traefik](https://containo.us/traefik/) - web dashboard for Traefik reverse proxy and TSL termination.
* https://adminer.your-domain.com/ - Service [Adminer](https://www.adminer.org/) - for accessing Postgres database.
* https://ldap.your-domain.com/ - Service [phpLdapAdmin](http://phpldapadmin.sourceforge.net/wiki/index.php/Main_Page) - for managing LDAP users and groups.
* https://auth.your-domain.com/ - Service [Authelia](https://github.com/authelia/authelia) - for logging in for services via LDAP that do not have their internal authentication, such as Traefik dashboard.
* https://static.your-domain.com/ - Simple Nginx server that serves static files from `./data/nginx` folder.

**Read more about each service at [services.md] documentation.**

## 3. Deploy a service

Now you can deploy additional services of your chosing. All of them are optional, only the "base" stack is required. 

### 3.1. Haste! Your own pastebin.

Try "Haste", which is a self hosted pastebin. All you have to do is to run: `./deploy.sh haste` and it will be available at https://haste.your-domain.com/. 

### 3.2. More services

Some services need environment variables to be properly set in the `.env` file (see [config.md](config.md)) and some require additional manual configuration. **Read the [services.md](services.md) documentation to learn about what services you can deploy and what you need to do.**

