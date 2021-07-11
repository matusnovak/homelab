#!/bin/bash

set -e

mkdir -p /tmp/microk8s
kubectl get all --all-namespaces 2>&1 > /tmp/microk8s/get-all.log
for type in pod service deployment statefulset replicaset daemonset pvc
do
  mkdir -p "/tmp/microk8s/$type"
  mkdir -p "/tmp/microk8s/logs"

  items=$(kubectl get $type --all-namespaces --template "{{range .items}}{{.metadata.namespace}}/{{.metadata.name}} {{end}}")
  
  for item in $items
  do
    echo "Checking: $type - $item"
    name="$(cut -d'/' -f2 <<< $item)"
    namespace="$(cut -d'/' -f1 <<< $item)"

    kubectl describe $type --namespace $namespace $name 2>&1 > "/tmp/microk8s/$type/$namespace-$name.log"

    if [ $type = "pod" ]; then
      containers=$(kubectl get pod --namespace $namespace $name -o "jsonpath={.spec.containers[*].name}")
      for container in $containers
      do
        kubectl logs --namespace $namespace $name -c $container 2>&1 > "/tmp/microk8s/logs/$namespace-$name-$container.log" || true
      done
    fi
  done
done

mkdir -p "/tmp/microk8s/pv"
names=$(kubectl get pv --all-namespaces --template "{{range .items}}{{.metadata.name}} {{end}}")
for name in $names
do
  echo "Checking: pv - $name"
  kubectl describe pv $name 2>&1 > "/tmp/microk8s/pv/$name.log"
done
