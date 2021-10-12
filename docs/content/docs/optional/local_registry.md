---
weight: 1
title: "Local registry"
---

# Optional - Local registry

All applications will pull Docker images from the internet. But what if you want to be trully offline? In that case you will need to use MicroK8s registry for all of your applications. (You can use any other local registry, as long as it is accessible by all nodes).

## 1. Configure registry

Follow the requirements page for enabling registry and adding the master node IP address to the Docker insecure registry config file.

## 3. Get master node address

We will need to push the containers to the registry by using master node IP address. This is the same address as you have used to configure insecure registry property in the Docker config file from the step above.

```bash
# Get the IP address used by the node.
# If you have multiple nodes in your cluster, use with --selector=kubernetes.io/role=master
kubectl get nodes -o jsonpath={.items[*].status.addresses[?\(@.type==\"InternalIP\"\)].address}
# Example output:
# 10.0.0.2
```

## 2. Pull and push to local registry

Each application is composed of one or more containers where each container has a dedicated Docker image. Which image is used is specified in the application chart. Some applications can have multiple charts. You can find all charts in the `charts` directory in this project.

Each chart has a file `values.yaml`. This file contains the default values used to render the templates and to deploy the resources from the templates. Each chart's `values.yaml` contains the following:

```yaml
# File: charts/traefik/values.yaml
image:
  repository: docker.io/library/traefik
  pullPolicy: IfNotPresent
  tag: "" # Overrides "appVersion" in the Chart.yaml file
```

However, some applications that are composed of multiple containers can have multiple `image.repository` values in the `values.yaml` file. For example, Authelia has the following:

```yaml
server:
  image:
    repository: docker.io/authelia/authelia
    pullPolicy: IfNotPresent
    tag: "" # Overrides "appVersion" in the Chart.yaml file
redis:
  image:
    repository: docker.io/library/redis
    pullPolicy: IfNotPresent
    tag: latest # Not affected by "appVersion" in the Chart.yaml file
```

In the case of Traefik, the tag used for the Docker image is `v2.4` from the `Chart.yml` variable `appVersion`. We will first pull this Docker image with the following command:

```bash
docker pull docker.io/library/traefik:v2.4
# Example output:
# v2.4: Pulling from library/traefik
# ddad3d7c1e96: Pull complete 
# 5f6722e60c2f: Pull complete 
# 3abdcd3bb40c: Pull complete 
# fe4701c53ae5: Pull complete 
# Digest: sha256:840e948af3c8d1e45e986eee7d97004ab29cfccffdf0be4c116ba9aaeff5d17a
# Status: Downloaded newer image for traefik:v2.4
# docker.io/library/traefik:v2.4
```

And then tag the image as the following:

```bash
# Make sure you change the 10.0.0.2 with the master node IP address
docker tag docker.io/library/traefik:v2.4 10.0.0.2:32000/library/traefik:v2.4
# No expected output on success
```

Push the image:

```bash
docker push 10.0.0.2:32000/library/traefik:v2.4
# Example output:
# The push refers to repository [10.0.0.2:32000/library/traefik]
# 3e4e2603f562: Pushed 
# 4e84a7a8360b: Pushed 
# 884c672ad7da: Pushed 
# 9a5d14f9f550: Pushed 
# v2.4: digest: sha256:d6039a8a87021d99b45aafdad699e63fbf388917d2e934e66e20d9e46854ba6f size: 1157
```

You can remove the image from your machine because you will no longer need it. **This will not remove the image from your MicroK8s registry, only from your local Docker.**

```bash
docker rmi docker.io/library/traefik:v2.4 10.0.0.2:32000/library/traefik:v2.4
# Example output:
# Untagged: traefik:v2.4
# Untagged: traefik@sha256:840e948af3c8d1e45e986eee7d97004ab29cfccffdf0be4c116ba9aaeff5d17a
# Untagged: 10.0.0.2:32000/library/traefik:v2.4
# Untagged: 10.0.0.2:32000/library/traefik@sha256:d6039a8a87021d99b45aafdad699e63fbf388917d2e934e66e20d9e46854ba6f
# Deleted: sha256:de1a7c9d5d63d8ab27b26f16474a74e78d252007d3a67ff08dcbad418eb335ae
# Deleted: sha256:d57e5e3eaa3192b0a44fbf4daad843f7fd1aeecffb936ab2d381ecf4ccf15450
# Deleted: sha256:01e78213d9f304ff9ba5f7cd4e3bb0ed8d36a357a617ac86c51db0c0df38ad3a
# Deleted: sha256:1660a9d385d8ce4c2a11fd6aadc26afb09e087d602c07e3036557b7ef73bb072
# Deleted: sha256:9a5d14f9f5503e55088666beef7e85a8d9625d4fa7418e2fe269e9c54bcb853c
```

Done! Now you can use `10.0.0.2:32000/library/traefik:v2.4` in your Kubernetes cluster.

## 3. Override the image

To specify which image to use for the application, you simply override the image repository and tag in your homelab configuration file. **You should override the values in your /homelab/config.yml file! Not in the chart's values.yaml file!**

```yaml
# File: /homelab/config.yml

# By specifying traefik: we are overriding values in charts/traefik/values.yaml
# The path "traefik.image.registry" maps directly
# to the path "image.registry" in charts/traefik/values.yaml
traefik:
  image:
    registry: '10.0.0.2:32000/library/traefik'
    tag: v2.4

authelia:
  server:
    image:
      registry: '10.0.0.2:32000/authelia/authelia'
      tag: latest
  redis:
    image:
      registry: '10.0.0.2:32000/library/redis'
      tag: latest
```

###4. Deploy

No additional configuration needed, you can deploy your homelab and the changes will be applied.
