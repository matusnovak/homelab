---
weight: 2
title: "Multi Node cluster"
---

# Optional - Multi node cluster

## 1. Join nodes together

To create a multi node cluster follow the Microk8s documentation here: https://microk8s.io/docs/clustering

## 2. Set node labels

For this project, it is recommended that you add specific labels to your nodes. You can use the node labels to specify which application will deploy on which node. Maybe you want that your Postgres will be running on some node with an SSD storage and maybe you want GitLab to run on some node with more CPU cores.

To view node labels, run the following command:

```bash
kubectl get nodes
# Example output:
# NAME      STATUS   ROLES    AGE   VERSION
# homelab   Ready    <none>   28d   v1.21.5-3+83e2bb7ee39726

# Use the "NAME" from above command output, the pipe with "jq" is optional
kubectl get nodes NAME -o jsonpath={.items[*].metadata.labels} | jq
# Example output:
# {
#  "beta.kubernetes.io/arch": "amd64",
#  "beta.kubernetes.io/os": "linux",
#  "kubernetes.io/arch": "amd64",
#  "kubernetes.io/hostname": "homelab",
#  "kubernetes.io/os": "linux",
#  "microk8s.io/cluster": "true",
# }
```

To add a label to a node, run the following command:

```bash
# Use the "NAME" from the "kubectl get nodes" command output
kubectl label nodes NAME example-label-key=some-value
```

I recommend that you use labels such as the following:

```
# Examples
homelab.local/disk=ssd
homelab.local/cpu=large
homelab.local/type=compute
```

## 3. Specify node selectors for applications

Each application in this project is composed of a Helm chart (sometimes there are multiple charts). Each Helm chart can have multiple deployments/containers. You can find all charts in the `charts` directory in this project.

Each chart has a file `values.yaml`. This file contains the default values used to render the templates and to deploy the resources from the templates. Each chart's `values.yaml` contains the following:

```yaml
# File: charts/traefik/values.yaml
nodeSelector: {}
```

However, sometimes, you may find this multiple times in `values.yaml`. For example, Authelia is composed of the Authelia server itself and a Redis server. In that case you will find the following:

```yaml
# File: charts/authelia/values.yaml
server:
  nodeSelector: {}
redis:
  nodeSelector: {}
```

So you can specify that the Authelia will deploy on cluster node #1 and the Redis for Authelia will deploy on some other cluster node #2.

To specify where the application deploys, you simply add the expected node labels in the node selector. **You should override the selectors in your /homelab/config.yml file! Not in the chart's values.yaml file!**

```yaml
# File: /homelab/config.yml

# By specifying traefik: we are overriding values in charts/traefik/values.yaml
# The path "traefik.nodeSelector" maps directly
# to the path "nodeSelector" in charts/traefik/values.yaml
traefik:
  nodeSelector:
    homelab.local/type: compute

authelia:
  server:
    nodeSelector:
      homelab.local/type: compute
  redis:
    nodeSelector:
      homelab.local/type: compute
```

## 4. Deploy

No additional configuration needed, you can deploy your homelab and the changes will be applied.
