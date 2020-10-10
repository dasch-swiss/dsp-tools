# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
THIS_FILE := $(lastword $(MAKEFILE_LIST))
CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

include vars.mk

#################################
# Integration test targets
#################################

# Clones the knora-api git repository
.PHONY: clone-knora-stack
clone-knora-stack:
	@git clone --branch v13.0.0-rc.17 --single-branch --depth 1 https://github.com/dasch-swiss/knora-api.git $(CURRENT_DIR)/.tmp/knora-stack

.PHONY: knora-stack
knora-stack: ## runs the knora-stack
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack env-file
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack stack-down-delete-volumes
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack init-db-test
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack stack-up
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack stack-logs-api-no-follow

.PHONY: dist
dist: ## generate distribution package
	python3 setup.py sdist bdist_wheel

.PHONY: upload
upload: ## upload distribution package to PyPi
	python3 -m twine upload dist/*

.PHONY: upgrade
upgrade: ## upgrade packages necessary for testing, building, packaging and uploading to PyPi
	python3 -m pip install --upgrade pip setuptools wheel tqdm twine pytest mkdocs mkdocs

.PHONY: build-docs
build-docs: ## build docs into the local 'site' folder
	mkdocs build

.PHONY: serve-docs
serve-docs: ## serve docs for local viewing
	mkdocs serve

.PHONY: publish-docs
publish-docs: ## build and publish docs to Github Pages
	mkdocs gh-deploy

.PHONY: install-requirements
install-requirements: ## install requirements
	pip3 install -r requirements.txt

.PHONY: install
install: ## install from source
	pip3 install .

.PHONY: test
test: clean local-tmp clone-knora-stack knora-stack ## runs all tests
	bazel test --test_summary=detailed --test_output=all //test/...

.PHONY: local-tmp
local-tmp:
	@mkdir -p $(CURRENT_DIR)/.tmp

.PHONY: clean
clean: ## cleans the project directory
	@rm -rf $(CURRENT_DIR)/.tmp
	@rm -rf dist/ build/ site/ knora.egg-info/

.PHONY: help
help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
