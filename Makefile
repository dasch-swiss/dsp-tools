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
	pip3 install -r deps/requirements.txt

.PHONY: test
test: ## runs all tests
	cd test && python3 -m unittest

.PHONY: clean
clean: ## cleans the project directory
	@rm -rf dist/ build/ knora.egg-info/ .pytest_cache/ site/

.PHONY: help
help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: dist upload upgrade build-docs serve-docs publish-docs clean help

.DEFAULT_GOAL := help
