.MAIN: help
.PHONY: push operators

ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
NAMESPACE=homelab
DATA_DIR=/homelab
CONFIG_PATH=${DATA_DIR}/config.yml
NAME=homelab

IMAGE_URL=docker.io
IMAGE_NAME=library/busybox:latest

LOCAL_IP_FILTER:=?(@.type==\"InternalIP\")

help:
	@echo "Usage:"
	@echo "make {help,deploy,status,dryrun}"
	@echo "  help   - View this help."
	@echo "  deploy - Deploy all applications."
	@echo "  status - View the status of all deployments."
	@echo "  dryrun - Render all templates, will not deploy any resources, for debug purposes only."

microk8s:
	@echo "Checking MicroK8s status..."
	@microk8s status > /dev/null || (echo "MicroK8s status failed, check with \"microk8s inspect\""; exit 1)

crds:
	@echo "Applying CRDs..."
	@DATA_DIR=${DATA_DIR} CONFIG_PATH=${CONFIG_PATH} python3 "${ROOT_DIR}/crds.py" > /dev/null

operators:
	@echo "Building operators..."
	@cd operators && $(MAKE) build > /dev/null

${CONFIG_PATH}:
	@stat ${CONFIG_PATH} > /dev/null | (echo "Config file ${CONFIG_PATH} does not exist!"; exit 1)

helm: ${CONFIG_PATH}
	@echo "Deploying..."
	@helm upgrade --install --namespace ${NAMESPACE} ${NAME} ${ROOT_DIR} --set "global.dataDir=${DATA_DIR}" --values "${CONFIG_PATH}" > /dev/null

deploy: microk8s crds operators helm
	@echo "Done!"
	@echo "Use 'kubectl --namespace ${NAMESPACE} get all' to view resources."

restart: microk8s
	@kubectl --namespace ${NAMESPACE} rollout restart deployment/${NAME}-${APP}

deployments:
	@kubectl --namespace ${NAMESPACE} get deployments

daemonsets:
	@kubectl --namespace ${NAMESPACE} get daemonsets

status: deployments daemonsets

services:
	@kubectl --namespace ${NAMESPACE} get services

pods:
	@kubectl --namespace ${NAMESPACE} get pods

logs:
	@kubectl --namespace ${NAMESPACE} logs ${NAME}-${APP}

describe:
	@kubectl --namespace ${NAMESPACE} describe pod ${NAME}-${APP}

dryrun: ${CONFIG_PATH}
	@helm template --namespace ${NAMESPACE} ${NAME} ${ROOT_DIR} --set "global.dataDir=${DATA_DIR}" --values "${CONFIG_PATH}"

push:
	$(eval NODE_ADDRESS := $(shell kubectl get nodes -o "jsonpath={.items[*].status.addresses[${LOCAL_IP_FILTER}].address}"))
	@docker pull ${IMAGE_URL}/${IMAGE_NAME}
	@docker tag ${IMAGE_URL}/${IMAGE_NAME} ${NODE_ADDRESS}:32000/${IMAGE_NAME}
	@docker push ${NODE_ADDRESS}:32000/${IMAGE_NAME}
	@docker rmi ${IMAGE_URL}/${IMAGE_NAME} ${NODE_ADDRESS}:32000/${IMAGE_NAME}
	@echo "Kubernetes now has access to image '${NODE_ADDRESS}:32000/${IMAGE_NAME}'"
