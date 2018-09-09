.PHONY: build init package deploy

SHELL:=/bin/bash
CURRENT_DIR = "$(shell pwd)"

DOCKER_USER ?= saboteurkid
DOCKER_BUILD_NAME ?= $(shell basename "${CURRENT_DIR}")
VERSION ?= 1.0.0
DOCKER_TAG ?= ${DOCKER_BUILD_NAME}:${VERSION}
DOCKER_REGISTRY ?= docker.io

debug:
	@echo "current directory: ${CURRENT_DIR}"
	@echo "Docker user: ${DOCKER_USER}"
	@echo "Docker build name: ${DOCKER_BUILD_NAME}"
	@echo "Docker tag: ${DOCKER_TAG}"
	@echo "Docker Registry: ${DOCKER_REGISTRY}"

init:
	@virtualenv
	@source env/bin/activate
build:
	@pip install -r requirements.txt
package:
	@-docker rmi -f ${DOCKER_USER}/${DOCKER_TAG}
	docker build -t ${DOCKER_USER}/${DOCKER_TAG} -t ${DOCKER_USER}/${DOCKER_BUILD_NAME}:latest ${CURRENT_DIR}
deploy:
	docker push ${DOCKER_REGISTRY}/${DOCKER_USER}/${DOCKER_TAG}
	docker push ${DOCKER_REGISTRY}/${DOCKER_USER}/${DOCKER_BUILD_NAME}:latest


