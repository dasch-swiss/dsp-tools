# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is DSP-TOOLS?

DSP-TOOLS is a CLI tool for interacting with the DaSCH Service Platform (DSP) API.
A DSP server is a remote server or a local machine
where the [DSP-API](https://github.com/dasch-swiss/dsp-api) is running on.

The two main tasks that DSP-TOOLS serves for are:

- **Create a project with its data model(s), described in a JSON file, on a DSP server**
  In order to archive your data on the DaSCH Service Platform,
  you need a data model that describes your data.
  The data model is defined in a JSON project definition file.
  The project (incl. its data models) must be created on the DSP server.
  If the DSP server is aware of the data model for your project,
  conforming data can be uploaded into the DSP repository.
- **Upload data, described in an XML file, to a DSP server that has a project with a matching data model**
  DSP-TOOLS allows you to perform bulk imports of your data.
  In order to do so, the data has to be described in an XML file.
  DSP-TOOLS is able to read the XML file
  and upload all data to the DSP server.

All functionalities of DSP-TOOLS revolve around these two basic tasks.

DSP-TOOLS provides the following functionalities:

- `dsp-tools create` creates the project with its data model(s) on a DSP server from a JSON file.
- `dsp-tools get` reads a project with its data model(s) from a DSP server and writes it into a JSON file.
- `dsp-tools validate-data` validates an XML data file according to the ontology previously uploaded on the server.
- `dsp-tools xmlupload` uploads data from an XML file onto a DSP server, incl. multimedia assets referenced in the XML.
- New workflow for `xmlupload`:
    - `dsp-tools upload-files` uploads all multimedia assets that are referenced in an XML file to a DSP server.
    - `dsp-tools ingest-files` kicks off the ingest process on the DSP server,
      and retrieves the mapping CSV when it is finished.
    - `dsp-tools ingest-xmlupload`
      creates the resources contained in the XML file on the DSP server, using the mapping CSV.
- `dsp-tools resume-xmlupload` resumes a previously interrupted `xmlupload` or `ingest-xmlupload`.
- `dsp-tools excel2json` creates an entire JSON project file from a folder with Excel files in it.
    - `dsp-tools excel2lists`
      creates the "lists" section of a JSON project file from one or several Excel files.
      The resulting section can be integrated into a JSON project file
      and then be uploaded to a DSP server with `dsp-tools create`.
    - `dsp-tools excel2resources`
      creates the "resources" section of a JSON project file from an Excel file.
      The resulting section can be integrated into a JSON project file
      and then be uploaded to a DSP server with `dsp-tools create`.
    - `dsp-tools excel2properties`
      creates the "properties" section of a JSON project file from an Excel file.
      The resulting section can be integrated into a JSON project file
      and then be uploaded to a DSP server with `dsp-tools create`.
- `dsp-tools old-excel2json`
  does the same as the newer `excel2json` command, but the Excel format for the `lists` section is different.
    - `dsp-tools old-excel2lists`
      does the same as the newer `excel2lists` command, but the Excel format is different.
- `dsp-tools excel2xml` transforms a data source to XML if it is already structured according to the DSP specifications.
- The module `excel2xml` provides helper methods that can be used in a Python script
  to convert data from a tabular format into XML. (**DEPRECATED in favor of `xmllib`**)
- The `xmllib` library provides helper functions that can be used in a Python script
  to convert data from a tabular format into XML.
- `dsp-tools id2iri` takes an XML file for bulk data import and replaces referenced internal IDs with IRIs.
  The mapping has to be provided with a JSON file.
- `dsp-tools start-stack / stop-stack` assist you in running a DSP stack on your local machine.
- `dsp-tools template` creates a template repository with a minimal JSON and XML file.
- `dsp-tools rosetta` clones the most up to date rosetta repository,
  creates the data model and uploads the data.


## Development Commands

### Environment Setup

- **Install dependencies**: `uv sync --all-extras --dev`
- **Activate virtual environment**: `source .venv/bin/activate`
- **Install pre-commit hooks**: `pre-commit install`

### Code Quality and Linting

- **Run all linters**: `just lint`
- **Format code**: `just format`
- **Type checking**: `just mypy`
- **Check for dead code**: `just vulture`
- **Check specific linters**:
    - `just ruff-check` (Python linting)
    - `just ruff-format-check` (Python formatting)
    - `just yamllint` (YAML linting)
    - `just markdownlint` (Markdown linting)
    - `just darglint` (docstring linting)

### Testing

- **Unit tests**: `just unittests` or `pytest test/unittests/`
- **Integration tests**: `just integration-tests` or `pytest test/integration/`
- **E2E tests (with testcontainers)**: `just e2e-tests` or `pytest -n=auto --dist=loadfile test/e2e/`
- **Legacy E2E tests (requires running DSP stack)**: `just legacy-e2e-tests`
- **Run specific test**: `pytest test/path/to/test.py::TestClass::test_method`

### Development Utilities

- **Start DSP stack**: `dsp-tools start-stack`
- **Build documentation**: `mkdocs serve`
- **Clean artifacts**: `just clean`

## Architecture Overview

### Core Components

#### CLI Module (`src/dsp_tools/cli/`)

- **Entry point**: `entry_point.py` - Main CLI entry point with argument parsing and version checking
- **Argument parsing**: `create_parsers.py` - Creates CLI argument parsers for all commands
- **Action dispatcher**: `call_action.py` - Routes parsed arguments to appropriate command handlers

#### Commands Module (`src/dsp_tools/commands/`)

Generally, each subdirectory implements a specific CLI command.
Some commands share a subdirectory, and some commands live in a single file instead of a directory.

#### xmllib Module (`src/dsp_tools/xmllib/`)

Public API library for programmatic creation of XML files:

- **models/**: Resource and value models for XML generation
- **helpers.py**: Utility functions for creating XML files
- **value_checkers.py**: Validation functions for different value types
- **value_converters.py**: Conversion utilities for values

#### Utils Module (`src/dsp_tools/utils/`)

- **xml_parsing/**: XML file parsing and validation utilities
- **data_formats/**: Date, IRI, and URI utility functions
- **request_utils.py**: HTTP request helpers

### Data Flow Architecture

The system follows this general flow for XML processing:

1. **XML Parsing**: Raw XML → etree Root → XSD validation → ParsedResource
2. **Processing**: ParsedResource → resolve permissions/IRIs → ProcessedResource
3. **Upload/Validation**: ProcessedResource → API calls or SHACL validation

### Key Design Patterns

- **Command Pattern**: CLI commands are implemented as separate modules with consistent interfaces
- **Pipeline Pattern**: XML processing follows a multi-stage pipeline with clear transformations
- **Model-Based**: Heavy use of dataclass models for type safety
- **Client Abstraction**: Separate client classes for different API endpoints

### Testing Strategy

- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test file I/O and cross-module interactions
- **E2E tests**: Test full workflows with testcontainers running DSP stack (database, backend, fontend)
- **Benchmarking tests**: Performance testing for critical algorithms

### Configuration

- **pyproject.toml**: Project metadata, dependencies, and tool configurations
- **justfile**: Task runner with commands for development workflow
- **Pre-commit hooks**: Automated code quality checks on commit

## Important Notes

- Always run `just lint` before committing to ensure code quality
- Use `dmypy restart` if mypy behaves unexpectedly
- The project uses strict type checking - all new code must have proper type annotations
- Docstrings follow Google-style docstrings
- Line length limit is 120 characters
- Use `uv add package` to add dependencies (or `uv add --dev package` for dev dependencies)
- All markdown files must comply with markdownlint rules specified in `.markdownlint.yml`
- Always use descriptive variable names
- Pull request reviews: Only request reviews from one of the following GitHub users:
  BalduinLandolt, Nora-Olivia-Ammann, Notheturtle, seakayone, jnussbaum
- Whenever you modify the codebase, make sure to also update all CLAUDE.md files (if necessary)
