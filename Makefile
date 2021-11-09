# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
THIS_FILE := $(lastword $(MAKEFILE_LIST))
CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

include vars.mk

#################################
# Make targets for dsp-tools
#################################

.PHONY: clone-dsp-repo
clone-dsp-repo: ## clone the dsp-api git repository
	@git clone --branch main --single-branch --depth 1 https://github.com/dasch-swiss/dsp-api.git $(CURRENT_DIR)/.tmp/dsp-stack

.PHONY: dsp-stack
dsp-stack: ## run the dsp-stack (deletes existing volumes first)
	$(MAKE) -C $(CURRENT_DIR)/.tmp/dsp-stack env-file
	$(MAKE) -C $(CURRENT_DIR)/.tmp/dsp-stack stack-down-delete-volumes
	$(MAKE) -C $(CURRENT_DIR)/.tmp/dsp-stack init-db-test
	$(MAKE) -C $(CURRENT_DIR)/.tmp/dsp-stack stack-up
	$(MAKE) -C $(CURRENT_DIR)/.tmp/dsp-stack stack-logs-api-no-follow

.PHONY: dist
dist: ## generate distribution package
	python3 setup.py sdist bdist_wheel

.PHONY: upload
upload: ## upload distribution package to PyPI
	python3 -m twine upload dist/*

.PHONY: upgrade-dist-tools
upgrade-dist-tool: ## upgrade packages necessary for testing, building, packaging and uploading to PyPI
	python3 -m pip install --upgrade pip setuptools wheel tqdm twine pytest mkdocs

.PHONY: docs-build
docs-build: ## build docs into the local 'site' folder
	mkdocs build

.PHONY: docs-serve
docs-serve: ## serve docs for local viewing
	mkdocs serve

.PHONY: docs-publish
docs-publish: ## build and publish docs to GitHub Pages
	mkdocs gh-deploy

.PHONY: install-requirements
install-requirements: ## install requirements
	python3 -m pip install --upgrade pip
	pip3 install -r requirements.txt
	pip3 install -r docs/requirements.txt

.PHONY: install
install: ## install from source (runs setup.py)
	python3 -m pip install --upgrade pip
	pip3 install .

.PHONY: test
test: clean local-tmp clone-dsp-repo dsp-stack ## run all tests
	# to run only one test, replace //test/... with p.ex. //test/e2e:test_tools
	bazel test --test_summary=detailed --test_output=all //test/...

.PHONY: test-end-to-end
test-end-to-end: clean local-tmp clone-dsp-repo dsp-stack ## run e2e tests
	bazel test --test_summary=detailed --test_output=all //test/e2e/...

.PHONY: test-unittests
test-unittests: ## run unit tests
	bazel test --test_summary=detailed --test_output=all //test/unittests/...

.PHONY: local-tmp
local-tmp: ## create local .tmp folder
	@mkdir -p $(CURRENT_DIR)/.tmp

.PHONY: clean
clean: ## clean local project directories
	@rm -rf $(CURRENT_DIR)/.tmp
	@rm -rf dist/ build/ site/ knora.egg-info/

.PHONY: help
help: ## show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: run
run: ## create dist, install and run
	$(MAKE) clean
	$(MAKE) dist
	$(MAKE) install
	dsp-tools

.DEFAULT_GOAL := help
