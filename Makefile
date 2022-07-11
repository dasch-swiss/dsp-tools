# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
THIS_FILE := $(lastword $(MAKEFILE_LIST))
CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

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
upgrade-dist-tools: ## upgrade packages necessary for testing, building, packaging and uploading to PyPI
	python3 -m pip install --upgrade pip setuptools wheel twine pytest mkdocs

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
	pip3 install -r dev-requirements.txt

.PHONY: install
install: ## install from source (runs setup.py)
	python3 -m pip install --upgrade pip
	pip3 install -e .

.PHONY: test
test: clean local-tmp clone-dsp-repo dsp-stack ## run all tests
	pytest test/

.PHONY: test-end-to-end
test-end-to-end: clean local-tmp clone-dsp-repo dsp-stack ## run e2e tests
	pytest test/e2e/

.PHONY: test-end-to-end-no-stack
test-end-to-end-no-stack: ## run e2e tests without starting the stack (for API development)
	pytest test/e2e/

.PHONY: test-unittests
test-unittests: ## run unit tests
	pytest test/unittests/

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

.PHONY: freeze-requirements
freeze-requirements: ## update (dev-)requirements.txt and setup.py based on pipenv's Pipfile.lock
	pipenv requirements > requirements.txt
	sed -i '' 's/==/~=/g' requirements.txt
	pipenv requirements --dev-only > dev-requirements.txt
	sed -i '' 's/==/~=/g' dev-requirements.txt
	pipenv run pipenv-setup sync
	sed -i '' 's/==/~=/g' setup.py

.DEFAULT_GOAL := help
