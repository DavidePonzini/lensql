DIR=/var/www/html/lensql2/

# To add submodules use in root directory:
#	git submodule add <url> public/...

init:
	npm install
	git submodule update --init --recursive

build:
	npx astro build

copy: build
	rm -rf $(DIR)/*
	mkdir -p $(DIR)
	cp -r dist/* $(DIR)

clean:
	rm -rf dist
