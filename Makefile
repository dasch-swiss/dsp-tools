dist: ## generate distribution package
	python3 setup.py sdist bdist_wheel

upload: ## upload distribution package to PyPi
	python3 -m twine upload dist/*

upgrade: ## upgrade packages necessary for testing, building, packaging and uploading to PyPi
	python3 -m pip install --upgrade pip setuptools wheel tqdm twine pytest mkdocs mkdocs

build-docs: ## build docs into the local 'site' folder
	mkdocs build

serve-docs: ## serve docs for local viewing
	mkdocs serve

publish-docs: ## build and publish docs to Github Pages
	mkdocs gh-deploy

test: ## runs all tests
	python3 -m pytest

clean: ## cleans the project directory
	rm -rf dist/ build/ knora.egg-info/ .pytest_cache/ site/

help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: dist upload upgrade build-docs serve-docs publish-docs clean help
