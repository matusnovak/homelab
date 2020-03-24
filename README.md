# Homelab

TODO

## Deploy

### 1. Install python3 and Docker

TODO

### 2. Create .env file

Copy the `.env.sample` file to `.env` found in the root directory of this repository next to the `docker-compose.yml` file. Edit the variables to suit your needs. Most of the variables have a default value that will work out of the box. However, **you will have to edit some of them**, such as:

* `ADMIN_USERNAME` - The username of the administration account (default is: `admin`).
* `ADMIN_PASSWORD` - The password for the administration account (default is: `admin`).
* `TLS_EMAIL` - The email to use for LetsEncrypt.
* `DATABASE_MASTER_PASSWORD` - The password for the root account of databases (default is: `admin`).

### 3. Run the setup script

Run the the following script in order to setup the configuration files. These files will use the `.env` file you have created in the previous step.

```
./setup.py
# or
python3 setup.py
```

### 4. Deploy everything

```
docker-compose up -d
```

