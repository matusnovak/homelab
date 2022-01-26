.MAIN: push

REGISTRY_URL=127.0.0.1:5000
IMAGE_NAME=openldap-controller
TAG=latest

build:
	@echo "Building ${REGISTRY_URL}/${IMAGE_NAME}:${TAG} ..."
	@docker build . -t ${REGISTRY_URL}/${IMAGE_NAME}:${TAG}

push: build
	@echo "Pushing ${REGISTRY_URL}/${IMAGE_NAME}:${TAG} ..."
	@docker push ${REGISTRY_URL}/${IMAGE_NAME}:${TAG}
