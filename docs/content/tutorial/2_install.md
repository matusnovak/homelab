---
title: 2. Installation
weight: 20
---

### 2.1. Clone the entire repository:

```sh
git clone https://github.com/matusnovak/homelab.git
cd homelab
```

### 2.2. Setup the environment variables

You will need to provide basic configuration via environment variables. These variables will be used by the Docker Compose to deploy the services. A sample configuration file is provided inside of the root directory of the repository called `.env.sample`.

{{% notice info %}}
Make sure you can see hidden files in your OS. Files starting with a dot in their filenames are considered hidden.
{{% /notice %}}

Copy the `.env.sample` to `.env` and edit these common variables: `DOMAIN_NAME`, `DOMAIN_COMPONENT`, `TLS_EMAIL`, `SECRET_KEY_BASE`, `ADMIN_PASSWORD`, and "Extra properties" at the bottom of the file. You can read more about these variables in the next section [**3. Configuration**]({{< ref "3_configuration.md" >}}).


