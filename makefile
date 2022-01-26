.MAIN: help
.PHONY: push operators

HOSTNAME:=$(shell cat /etc/hostname)
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
NAMESPACE=homelab
DATA_DIR=/homelab
CONFIG_PATH=${DATA_DIR}/config.yml
REGISTRY_URL=${HOSTNAME}.lan:5443
NAME=homelab

IMAGE_URL=docker.io
IMAGE_NAME=library/busybox:latest

help:
	@echo "Usage:"
	@echo "make {help,deploy,status,dryrun}"
	@echo "  help   - View this help."
	@echo "  deploy - Deploy all applications."
	@echo "  status - View the status of all deployments."
	@echo "  dryrun - Render all templates, will not deploy any resources, for debug purposes only."

crds:
	@echo "Applying CRDs..."
	@DATA_DIR=${DATA_DIR} CONFIG_PATH=${CONFIG_PATH} python3 "${ROOT_DIR}/crds.py"

operators:
	@echo "Building operators..."
	@cd operators && $(MAKE) build REGISTRY_URL=${REGISTRY_URL}

${CONFIG_PATH}:
	@stat ${CONFIG_PATH} > /dev/null | (echo "Config file ${CONFIG_PATH} does not exist!"; exit 1)

helm: ${CONFIG_PATH}
	@echo "Deploying..."
	@helm upgrade --install --namespace ${NAMESPACE} ${NAME} ${ROOT_DIR} --set "global.dataDir=${DATA_DIR}" --values "${CONFIG_PATH}" > /dev/null

deploy: helm
	@echo "Done!"
	@echo "Use 'kubectl --namespace ${NAMESPACE} get all' to view resources."

restart:
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
	@docker pull ${IMAGE_URL}/${IMAGE_NAME}
	@docker tag ${IMAGE_URL}/${IMAGE_NAME} ${REGISTRY_URL}/${IMAGE_NAME}
	@docker push ${REGISTRY_URL}/${IMAGE_NAME}
	@docker rmi ${IMAGE_URL}/${IMAGE_NAME} ${REGISTRY_URL}/${IMAGE_NAME}
	@echo "Kubernetes now has access to image '${REGISTRY_URL}/${IMAGE_NAME}'"
