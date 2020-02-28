# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
THIS_FILE := $(lastword $(MAKEFILE_LIST))
CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

include vars.mk

#################################
# CI targets
#################################

# Clones the knora-api git repository
.PHONY: clone-knora-stack
clone-knora-stack:
	@git clone --single-branch --depth 1 https://github.com/dasch-swiss/knora-api.git $(CURRENT_DIR)/.tmp/knora-stack

.PHONY: knora-stack-ci
knora-stack-ci: ## runs the knora-stack
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack stack-up-ci
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack print-env-file
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack stack-config
	sleep 15
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack init-db-test-unit-minimal
	sleep 15
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack stack-restart-api
	sleep 18
	$(MAKE) -C $(CURRENT_DIR)/.tmp/knora-stack stack-logs-api-no-follow

.PHONY: test-ci
test-ci: ## first starts the knora-stack and then runs the tests
	@$(MAKE) -f $(THIS_FILE) clean
	@$(MAKE) -f $(THIS_FILE) local-tmp
	@$(MAKE) -f $(THIS_FILE) clone-knora-stack
	@$(MAKE) -f $(THIS_FILE) knora-stack-ci
	@$(MAKE) -f $(THIS_FILE) test

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
test: ## runs all tests
	bazel test --test_summary=detailed --test_output=all //...

#################################
# Other
#################################

.PHONY: local-tmp
local-tmp:
	@mkdir -p $(CURRENT_DIR)/.tmp

.PHONY: clean
clean: ## cleans the project directory
	@rm -rf dist/ build/ site/ knora.egg-info/
	@rm -rf $(CURRENT_DIR)/.tmp

.PHONY: help
help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
