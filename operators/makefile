.MAIN: build
.PHONY: build

REGISTRY_URL=127.0.0.1:5000

build:
	@cd openldap && $(MAKE) push REGISTRY_URL=${REGISTRY_URL}
	@cd postgres && $(MAKE) push REGISTRY_URL=${REGISTRY_URL}
