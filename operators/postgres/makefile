.MAIN: push

REPOSITORY=localhost:32000
IMAGE_NAME=postgres-controller
TAG=latest

build:
	@echo "Building ${REPOSITORY}/${IMAGE_NAME}:${TAG} ..."
	@docker build . -t ${REPOSITORY}/${IMAGE_NAME}:${TAG}

push: build
	@echo "Pushing ${REPOSITORY}/${IMAGE_NAME}:${TAG} ..."
	@docker push ${REPOSITORY}/${IMAGE_NAME}:${TAG}
