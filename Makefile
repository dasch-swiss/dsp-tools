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
	@git clone --branch main --single-branch --depth 1 https://github.com/dasch-swiss/dsp-api.git .tmp/dsp-stack
	cd .tmp/dsp-stack
	git checkout $(git rev-list --tags --max-count=1)
	cd ../..
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
	python3 setup.py sdist bdist_wheel

.PHONY: upload
upload: ## upload distribution package to PyPI
	python3 -m twine upload dist/*

.PHONY: docs-build
docs-build: ## build docs into the local 'site' folder
	mkdocs build

.PHONY: docs-serve
docs-serve: ## serve docs for local viewing
	mkdocs serve --dev-addr=0.0.0.0:7979

.PHONY: install-requirements
install-requirements: ## install Python dependencies from the diverse requirements.txt files
	python3 -m pip install --upgrade pip
	pip3 install -r requirements.txt
	pip3 install -r docs/requirements.txt
	pip3 install -r dev-requirements.txt

.PHONY: install
install: ## install from source (runs setup.py)
	python3 -m pip install --upgrade pip
	pip3 install -e .

.PHONY: test
test: dsp-stack ## run all tests located in the "test" folder (intended for local usage)
	-pytest test/
	$(MAKE) stack-down

.PHONY: test-no-stack
test-no-stack: ## run all tests located in the "test" folder, without starting the stack (intended for local usage)
	pytest test/

.PHONY: test-end-to-end
test-end-to-end: dsp-stack ## run e2e tests (intended for local usage)
	-pytest test/e2e/
	$(MAKE) stack-down

.PHONY: test-end-to-end-ci
test-end-to-end-ci: dsp-stack ## run e2e tests (intended for GitHub CI, where it isn't possible nor necessary to remove .tmp)
	pytest test/e2e/

.PHONY: test-end-to-end-no-stack
test-end-to-end-no-stack: ## run e2e tests without starting the dsp-stack (intended for local usage)
	pytest test/e2e/

.PHONY: test-unittests
test-unittests: ## run unit tests
	pytest test/unittests/

.PHONY: clean
clean: ## clean local project directories
	@rm -rf dist/ build/ site/ dsp_tools.egg-info/ id2iri_*_mapping_*.json stashed_*_properties_*.txt

.PHONY: help
help: ## show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: freeze-requirements
freeze-requirements: ## update (dev-)requirements.txt and setup.py based on pipenv's Pipfile.lock
	pipenv run pipenv requirements > requirements.txt
	sed -i '' 's/==/~=/g' requirements.txt
	pipenv run pipenv requirements --dev-only > dev-requirements.txt
	sed -i '' 's/==/~=/g' dev-requirements.txt
	pipenv run pipenv-setup sync
	sed -i '' 's/==/~=/g' setup.py
	autopep8 --global-config pyproject.toml --aggressive --in-place setup.py

.DEFAULT_GOAL := help
