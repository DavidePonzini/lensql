SHELL := /bin/bash
DOCKER_IMAGE=davideponzini/lensql
DOCKER_IMAGE_VERSION=1

.PHONY: run rund build upload

run: build
	docker run --rm -p 8888:8888 $(DOCKER_IMAGE):$(DOCKER_IMAGE_VERSION)

rund: build
	docker run -d -p 8888:8888 $(DOCKER_IMAGE):$(DOCKER_IMAGE_VERSION)

build:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_IMAGE_VERSION) .

upload: build
	docker login
	docker push $(DOCKER_IMAGE):$(DOCKER_IMAGE_VERSION)

