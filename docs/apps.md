# Homelab: Apps

The following is a list of available apps and some basic information.

## Authentication

Each app has different authentication methods, but this Homelab project tries to merge them together using LDAP. This is purely optional and can be enabled/disabled on per app basis in their respective YAML configuration files in the `group_vars/homelab` folder. The LDAP is a server that sits behind the apps that provides user data. This is used to verify that the user exists, has the permission to use the app, and validates the password stored in the LDAP. This is not the same as single-sign-on, but is very close to it.

The following are the possible authentication methods the apps can use:

* **None:** The app can be accessed by anyone
* **Internal only:** The app has its own internal authentication method, LDAP can not be used.
* **LDAP-integrated:** The app has native integration with LDAP, perfect choice.
* **LDAP-redirect:** Before entering the app you will be redirected to external authenticator (Authelia) to log-in before being redirected back into the app. This will use LDAP.

## App: Traefik (dependency)

Traefik is an open-source Edge Router that makes publishing your services a fun and easy experience. It receives requests on behalf of your system and finds out which components are responsible for handling them. 

* **Official page:** <https://doc.traefik.io/traefik/>
* **Role name:** `traefik`
* **Config file:** `group_vars/homelab/traefik.yml`
* **Web location:** `https://traefik.example.com/dashboard/` (dashboard)
* **Authentication:** None or LDAP-redirect (for dashboard only)
* **Resource usage:** Medium CPU and low RAM

## App: PostgreSQL (dependency)

PostgreSQL is a powerful, open source object-relational database system with over 30 years of active development that has earned it a strong reputation for reliability, feature robustness, and performance. 

* **Official page:** <https://www.postgresql.org/>
* **Role name:** `postgres`
* **Config file:** N/A
* **Web location:** N/A
* **Authentication:** N/A
* **Resource usage:** Low CPU and low RAM

## App: MongoDB (dependency)

MongoDB is a general purpose, document-based, distributed database built for modern application developers and for the cloud era.

* **Official page:** <https://www.mongodb.com/>
* **Role name:** `mongo`
* **Config file:** N/A
* **Web location:** N/A
* **Authentication:** N/A
* **Resource usage:** Low CPU and low RAM

## App: OpenLDAP (dependency)

OpenLDAP is a free, open-source implementation of the Lightweight Directory Access Protocol developed by the OpenLDAP Project.

* **Official page:** <https://www.openldap.org/>
* **Role name:** `ldap`
* **Config file:** `group_vars/homelab/ldap.yml`
* **Web location:** N/A
* **Authentication:** N/A
* **Resource usage:** Low CPU and low RAM

## App: Portainer

Portainer is a universal container management tool. It works with Kubernetes, Docker, Docker Swarm and Azure ACI and allows you to manage containers without needing to know platform-specific code.

* **Official page:** <https://www.portainer.io/>
* **Role name:** `portainer`
* **Config file:** `group_vars/homelab/portainer.yml`
* **Web location:** `https://portainer.example.com/`
* **Authentication:** Internal or LDAP-integrated (not able to select Portainer specific group permissions via LDAP)
* **Resource usage:** Low CPU and low RAM

## App: phpLDAPadmin

phpLDAPadmin is a web app for administering Lightweight Directory Access Protocol servers.

* **Official page:** <http://phpldapadmin.sourceforge.net/wiki/index.php/Main_Page>
* **Role name:** `phpldapadmin`
* **Config file:** N/A
* **Web location:** `https://ldap.example.com/`
* **Authentication:** LDAP-integrated
* **Resource usage:** Low CPU and low RAM

## App: Adminer

Database management in a single PHP file.

* **Official page:** <https://www.adminer.org/>
* **Role name:** `adminer`
* **Config file:** N/A
* **Web location:** `https://adminer.example.com/`
* **Authentication:** Database specific
* **Resource usage:** Low CPU and low RAM

## App: Haste

Haste is an open-source pastebin software written in node.js, which is easily installable in any network.

* **Official page:** <http://hastebin.com/>
* **Role name:** `haste`
* **Config file:** `group_vars/homelab/haste.yml`
* **Web location:** `https://haste.example.com/`
* **Authentication:** None or LDAP-redirect
* **Resource usage:** Low CPU and low RAM

## App: FileBrowser

FileFrowser provides a file managing interface within a specified directory and it can be used to upload, delete, preview, rename and edit your files.

* **Official page:** <https://filebrowser.org/>
* **Role name:** `filebrowser`
* **Config file:** `group_vars/homelab/filebrowser.yml`
* **Web location:** `https://filebrowser.example.com/`
* **Authentication:** Internal only
* **Resource usage:** Low CPU and low RAM

## App: DevDocs

DevDocs combines multiple API documentations in a fast, organized, and searchable interface. 

* **Official page:** <https://devdocs.io/>
* **Role name:** `devdocs`
* **Config file:** N/A
* **Web location:** `https://devdocs.example.com/`
* **Authentication:** None
* **Resource usage:** Low CPU and low RAM

## App: NextCloud

Nextcloud is a suite of client-server software for creating and using file hosting services.

* **Official page:** <https://nextcloud.com/>
* **Role name:** `nextcloud`
* **Config file:** `group_vars/homelab/nextcloud.yml`
* **Web location:** `https://nextcloud.example.com/`
* **Authentication:** Internal or LDAP-integrated
* **Resource usage:** Low CPU and low RAM

## App: OnlyOffice

OnlyOffice offers a secure online office suite highly compatible with MS Office formats. **This is part of NextCloud!**

* **Official page:** <https://www.onlyoffice.com>
* **Role name:** `nextcloud` (part of nextcloud!)
* **Config file:** `group_vars/homelab/nextcloud.yml`
* **Web location:** `https://nextcloud.example.com/`
* **Authentication:** Uses NextCloud for authentication
* **Resource usage:** Medium CPU and High RAM (depends on number of users)

