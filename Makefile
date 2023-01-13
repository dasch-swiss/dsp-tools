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

.PHONY: clean
clean: ## clean local project directories
	@rm -rf dist/ build/ site/ id2iri_*_mapping_*.json stashed_*_properties_*.txt

.PHONY: help
help: ## show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
