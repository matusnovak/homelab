---
weight: 1
title: "Requirements"
---

# Requirements

Please make sure that you have went through all of the requirements below. Not doing so will result in unsuccessful deployment.

## OS

It is recommended that you will use Ubuntu or similar Debian based system. This project assumes that you have `apt-get` installed. It is highly recommended that you use [Ubuntu Server](https://ubuntu.com/download/server) for the best experience. Use version `Ubuntu Focal 20.04`

## Python 3

You will need to install Python 3 and pip. The Python 3 already comes installed with the latest Ubuntu OS by default. To install Python and pip, use the following command:

```bash
$ sudo apt-get install python3 python3-pip
```

## Docker

This project requires that you have installed Docker. More information can be found here: https://docs.docker.com/engine/install/ubuntu/ You can use the following steps:

```bash
# Uninstall old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Set up the repository
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker's official repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

Note: You don't need to install Docker compose.

## MicroK8s

This project also requires that you use MicroK8s Kubernetes deployment. It is not recommended to use any other deployments such as K3s or Minikube. More information can be found here: https://ubuntu.com/tutorials/install-a-local-kubernetes-with-microk8s#1-overview You can use the following steps below:

```bash
# Install MicroK8s and kubectl via snap
sudo snap install microk8s kubectl --classic

# Enable addons
# The ":size=40Gi" is optional, sets the registry storage size.
microk8s enable dns storage rbac registry:size=40Gi

# Generate config for the current user
mkdir -p ~/.kube
microk8s config > ~/.kube/config
chmod 600 ~/.kube/config

# Verify that kubectl works correctly
kubectl get all
# Expected output:
# NAME                 TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
# service/kubernetes   ClusterIP   10.152.183.1   <none>        443/TCP   27d
```

## RBAC

This project uses RBAC and it is a requirement to have it enabled. To enable RBAC on your cluster, use the following steps:

```bash
microk8s enable rbac
```

To check whether RBAC is enabled, the following command should print out an output:

```bash
kubectl api-versions | grep rbac.authorization.k8s.io/v1
# Expected output:
# rbac.authorization.k8s.io/v1
# rbac.authorization.k8s.io/v1beta1
```

## Helm

Helm is used in this project to render the application templates and deploy the resources to the cluster. More information can be found here: https://helm.sh/docs/intro/install/ You can use the following steps to install it:

```bash
curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt-get install apt-transport-https --yes
echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

Verify that Helm is installed by running the following command:

```bash
helm version
# Expected output:
# version.BuildInfo{Version:"v3.7.0", GitCommit:"eeac83883cb4014fe60267ec6373570374ce770b", GitTreeState:"clean", GoVersion:"go1.16.8"}
```

## Fix Docker registry config

This project will build and deploy several custom CRD controllers that will allocate resources such as LDAP objects or Postgres databases and users. This is done via a custom Docker images that will be pushed into Kubernetes registry. In order to do so, you will need to allow Docker to push to insecure registries. This is done by **adding the IP address of your master cluster node** into the list of insecure registries.

First, find out the local IP address used by your cluster node.

```bash
# Get the IP address used by the node.
# If you have multiple nodes in your cluster, use with --selector=kubernetes.io/role=master
kubectl get nodes -o jsonpath={.items[*].status.addresses[?\(@.type==\"InternalIP\"\)].address}
# Example output:
# 10.0.0.2
```

Now that you have the IP address, which should be your local network address, add it to the list of insecure registries. Edit the file `/etc/docker/daemon.json` (this file may not exist, create it):

```bash
# Create the file if it does not exist
sudo nano /etc/docker/daemon.json
```

And add/edit the following contents to include the registry:

```json
{
  "insecure-registries" : [
    "localhost:32000",
    "10.0.0.2:32000"
  ]
}
```

Change the IP address `10.0.0.2` to the one you have obtained from above!

Finally, restart the docker:

```bash
sudo systemctl restart docker
```

Note: This is required to be done only on the cluster node from which you will be deploying this project. You do not need to do this on all cluster nodes. In case you are deploying remotely, you will have to do this on your local machine.

## Fix MicroK8s registry mirrors

For MicroK8s to pull images from the built in registry, you will have to fix the configuration for containerd. Edit the following file: `/var/snap/microk8s/current/args/containerd-template.toml`

```bash
sudo nano /var/snap/microk8s/current/args/containerd-template.toml
```

And you should find the following:

```
  # 'plugins."io.containerd.grpc.v1.cri".registry' contains config related to the registry
  [plugins."io.containerd.grpc.v1.cri".registry]

    # 'plugins."io.containerd.grpc.v1.cri".registry.mirrors' are namespace to mirror mapping for all namespaces.
    [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
        endpoint = ["https://registry-1.docker.io", ]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:32000"]
        endpoint = ["http://localhost:32000"]
```

Now add a new mirror with the node IP address:

```
  # 'plugins."io.containerd.grpc.v1.cri".registry' contains config related to the registry
  [plugins."io.containerd.grpc.v1.cri".registry]

    # 'plugins."io.containerd.grpc.v1.cri".registry.mirrors' are namespace to mirror mapping for all namespaces.
    [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
        endpoint = ["https://registry-1.docker.io", ]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."localhost:32000"]
        endpoint = ["http://localhost:32000"]
      #
      # Add this with your node IP address!
      #
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."10.0.0.2:32000"]
        endpoint = ["http://10.0.0.2:32000"]
```

Save the file and restart the MicroK8s:

```bash
# This may take ~2 minutes
sudo microk8s stop
sudo microk8s start
```

Note: You will have to do this on all nodes if you are using multi node cluster!
