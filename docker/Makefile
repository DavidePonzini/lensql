SHELL := /bin/bash
DOCKER_IMAGE=davideponzini/lensql

.PHONY: run rund build

run: build
	docker run --rm -p 8888:8888 $(DOCKER_IMAGE)

rund: build
	docker run -d -p 8888:8888 $(DOCKER_IMAGE)

build:
	docker build -t $(DOCKER_IMAGE) .

