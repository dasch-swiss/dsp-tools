# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
THIS_FILE := $(lastword $(MAKEFILE_LIST))
CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

############################
# Make targets for dsp-tools
############################

.PHONY: dsp-stack
dsp-stack: ## clone the dsp-api git repository and run the dsp-stack
	@mkdir -p .tmp
	@git clone --branch v24.0.8 --single-branch https://github.com/dasch-swiss/dsp-api.git .tmp/dsp-stack
	$(MAKE) -C .tmp/dsp-stack env-file
	$(MAKE) -C .tmp/dsp-stack init-db-test
	$(MAKE) -C .tmp/dsp-stack stack-up
	$(MAKE) -C .tmp/dsp-stack stack-logs-api-no-follow

.PHONY: stack-down
stack-down: ## stop dsp-stack and remove the cloned dsp-api repository
	$(MAKE) -C .tmp/dsp-stack stack-down-delete-volumes
	@test -x .tmp && rm -rf .tmp

.PHONY: dist
dist: ## generate distribution package
	@rm -rf dist/ build/
	poetry build

.PHONY: upload
upload: ## upload distribution package to PyPI
	poetry publish

.PHONY: docs-build
docs-build: ## build docs into the local 'site' folder
	mkdocs build

.PHONY: docs-serve
docs-serve: ## serve docs for local viewing
	mkdocs serve --dev-addr=0.0.0.0:7979

.PHONY: install
install: ## install Poetry, which in turn installs the dependencies and makes an editable installation of dsp-tools
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install

.PHONY: test
test: dsp-stack ## run all tests located in the "test" folder (intended for local usage)
	-poetry run pytest test/	# ignore errors, continue anyway with stack-down
	$(MAKE) stack-down

.PHONY: test-no-stack
test-no-stack: ## run all tests located in the "test" folder, without starting the stack (intended for local usage)
	poetry run pytest test/

.PHONY: test-end-to-end
test-end-to-end: dsp-stack ## run e2e tests (intended for local usage)
	-poetry run pytest test/e2e/	# ignore errors, continue anyway with stack-down
	$(MAKE) stack-down

.PHONY: test-end-to-end-ci
test-end-to-end-ci: dsp-stack ## run e2e tests (intended for GitHub CI, where it isn't possible nor necessary to remove .tmp)
	poetry run pytest test/e2e/

.PHONY: test-end-to-end-no-stack
test-end-to-end-no-stack: ## run e2e tests without starting the dsp-stack (intended for local usage)
	poetry run pytest test/e2e/

.PHONY: test-unittests
test-unittests: ## run unit tests
	poetry run pytest test/unittests/

.PHONY: clean
clean: ## clean local project directories
	@rm -rf dist/ build/ site/ id2iri_*_mapping_*.json stashed_*_properties_*.txt

.PHONY: help
help: ## show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
