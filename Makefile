# Determine this makefile's path.
# Be sure to place this BEFORE `include` directives, if any.
THIS_FILE := $(lastword $(MAKEFILE_LIST))
CURRENT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

############################
# Make targets for dsp-tools
############################

.PHONY: docs-serve
docs-serve: ## serve docs for local viewing
	poetry run mkdocs serve --dev-addr=localhost:7979

.PHONY: install
install: ## install Poetry, which in turn installs the dependencies and makes an editable installation of dsp-tools
	curl -sSL https://install.python-poetry.org | python3 -
	poetry install

.PHONY: test
test: ## run all tests located in the "test" folder
	@dsp-tools start-stack --no-prune
	-poetry run pytest test/	# ignore errors, continue anyway with stop-stack (see https://www.gnu.org/software/make/manual/make.html#Errors)
	@dsp-tools stop-stack

.PHONY: test-no-stack
test-no-stack: ## run all tests located in the "test" folder, without starting the stack (intended for local usage)
	poetry run pytest test/

.PHONY: test-end-to-end
test-end-to-end: ## run e2e tests
	@dsp-tools start-stack --no-prune
	-poetry run pytest test/e2e/	# ignore errors, continue anyway with stop-stack (see https://www.gnu.org/software/make/manual/make.html#Errors)
	@dsp-tools stop-stack

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
