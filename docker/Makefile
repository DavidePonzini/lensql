SHELL := /bin/bash
ENV=../.env
DOCKER_IMAGE=davideponzini/lensql

.PHONY: run build

run: build
	docker run --rm -p 8888:8888 $(DOCKER_IMAGE)

rund: build
	docker run -d -p 8888:8888 $(DOCKER_IMAGE)

build: $(ENV)
	source $(ENV) && docker build -t $(DOCKER_IMAGE) \
		--build-arg OPENAI_API_KEY=$$OPENAI_API_KEY \
		--build-arg LENSQL_LOGGER_HOST=$$LENSQL_LOGGER_HOST \
		--build-arg LENSQL_LOGGER_PORT=$$LENSQL_LOGGER_PORT \
		--build-arg LENSQL_LOGGER_DBNAME=$$LENSQL_LOGGER_DBNAME \
		--build-arg LENSQL_LOGGER_USER=$$LENSQL_LOGGER_USER \
		--build-arg LENSQL_LOGGER_PASSWORD=$$LENSQL_LOGGER_PASSWORD \
		.

$(ENV):
	cp $(ENV).template $(ENV)


