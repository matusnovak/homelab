---
title: 4. Deploy
weight: 40
---

After you have configured the environment variables, you can deploy the initial stack. 

{{% notice warning %}}
Don't use `docker-compose up` within the root directory. It will only mess up things. Use the provided `deploy.sh` script instead.
{{% /notice %}}

As you may have already noticed, the root folder contains multiple `docker-compose.*.yml` files. **Each one of these files is considered a stack.** All of these files define a set of services. Each service will be deployed based on the environment variables in the `.env` file. So, a stack has one or more service, which will be created as a Docker container with shared Docker network.

### Deploy the base stack first!

{{% notice info %}}
The base service contains Postgres and Mongo databases alongside with Traefik reverse proxy and some additional services. This base stack also creates the shared network! This is an essential stack and all of the other stacks will not work without it.
{{% /notice %}}

To deploy it, use the following command:

```bash
./deploy.sh base
```

The deploy script is a simple alias of:

```bash
docker-compose -p homelab_${STACK} -f docker-compose.${STACK}.yml up -d
```

Now you can navigate to your domain URL as you have specified in the `.env` file with `DOMAIN_NAME` variable. **But, you will get 404 Page not found error!**. So why do you get 404? Because each service that can be accessed through a web browser is on a specific subdomain. For example Traefik dashboard (the reverse proxy that will be at the front of all web requests on ports 80 and 443) is on address `https://traefik.DOMAIN_NAME`. You can change this by going into each docker-compose file and changing: `traefik.http.routers.example.rule=Host('example.${DOMAIN_NAME}')` for each service.

You should be able to access the Traefik dashboard on address `https://traefik.DOMAIN_NAME` and you will need to log-in with username: `admin` and password: `ADMIN_PASSWORD` (the password is in the `.env` file).

### Next steps

Some of the services in the base stack need additional configuration. For example, you need to configure the administrator account for the Portainer service. You will also need to setup the LDAP authentication. **Follow the steps for each of the service in the [5. Services](../5_services/) section**.

