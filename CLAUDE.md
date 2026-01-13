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
- The module `excel2xml` provides helper methods that can be used in a Python script
  to convert data from a tabular format into XML. (**DEPRECATED in favor of `xmllib`**)
- The `xmllib` library provides helper functions that can be used in a Python script
  to convert data from a tabular format into XML.
- `dsp-tools id2iri` takes an XML file for bulk data import and replaces referenced internal IDs with IRIs.
  The mapping has to be provided with a JSON file.
- `dsp-tools update-legal` converts legal metadata in XML files from the old format to the new format.
  Legal metadata (authorship, copyright, license) is migrated from `<text-prop>` elements
  to attributes on `<bitstream>` or `<iiif-uri>` elements.
  The command handles validation, error correction via CSV workflow, and authorship deduplication.
- `dsp-tools start-stack / stop-stack` assist you in running a DSP stack on your local machine.


## Development Commands

### Environment Setup

- **Install dependencies**: `uv sync --all-extras --dev`
- **Activate virtual environment**: `source .venv/bin/activate`
- **Install pre-commit hooks**: `pre-commit install`

### Code Quality and Linting

- **Run all linters**: `just lint`
- **Format code**: `just format`
- **Type checking**: `just mypy`
    - Use `dmypy restart` if mypy behaves unexpectedly
- **Check for dead code**: `just vulture`
- **Check specific linters**:
    - `just ruff-check` (Python linting)
    - `just ruff-format-check` (Python formatting)
    - `just yamllint` (YAML linting)
    - `just markdownlint` (Markdown linting)

### Testing

- **Unit tests**: `just unittests` or `pytest test/unittests/`
- **Integration tests**: `just integration-tests` or `pytest test/integration/`
- **E2E tests (with testcontainers)**: `just e2e-tests` or `pytest -n=auto --dist=loadfile test/e2e/`
- **Legacy E2E tests (requires running DSP stack)**: `just legacy-e2e-tests`
- **Run specific test**: `pytest test/path/to/test.py::TestClass::test_method`
- **Assertion format**: Use simple assertions without custom error messages.
  Pytest provides clear output on failure without custom messages.
    - **Correct**: `assert "id" in second_list_all_nodes[0]`
    - **Incorrect**: `assert "id" in second_list_all_nodes[0], f"Node missing 'id': {second_list_all_nodes[0]}"`

### Development Utilities

- **Start DSP stack**: `dsp-tools start-stack`
- **Build documentation**: `mkdocs serve`
- **Clean artifacts**: `just clean`
- **Install new dependencies**: `uv add package` (or `uv add --dev package` for dev dependencies)


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
- **E2E tests**: Test full workflows with testcontainers running DSP stack (database, backend, frontend)
- **Benchmarking tests**: Performance testing for critical algorithms

### Configuration

- **pyproject.toml**: Project metadata, dependencies, and tool configurations
- **justfile**: Task runner with commands for development workflow
- **Pre-commit hooks**: Automated code quality checks on commit

## Basic instructions about Claude's role and how to behave

### Our relationship

- You are a Senior Software Developer who supports me in my daily work.
- When I ask you for a solution to a problem, you should always think critically about the problem, and ask back if necessary.
  Perhaps there is an important aspect that I forgot, or perhaps I have misunderstood the problem.
- When I ask you to do something, you should always think critically about it.
  If you think it doesn't make sense, then you should push back, but you should also cite evidence.
- Ask me one question after another, and provide a structured form where I can submit my answers.

### Writing code

- We prefer simple, clean, maintainable solutions over clever or complex ones,
  even if the latter are more concise or performant.
  Readability and maintainability are primary concerns.
- Make the smallest reasonable changes to get to the desired outcome.
  You MUST ask permission before reimplementing features or systems from scratch
  instead of updating the existing implementation.
- When writing comments, avoid referring to temporal context about refactors or recent changes.
  Comments should be evergreen and describe the code as it is, not how it evolved or was recently changed.
- NEVER name things as 'improved' or 'new' or 'enhanced', etc.
  Code naming should be evergreen. What is new someday will be "old" someday.
- Only write docstrings for high-level functions, or if the purpose of a function cannot be derived from its name alone.
  The names of lower-level functions should be self-explanatory, so it would be a duplication to write docstrings.
  In test codes, we most often don't need docstrings.

### Code quality

- The project uses strict type checking - all new code must have proper type annotations
- Docstrings follow Google-style docstrings
- All markdown files must comply with markdownlint rules specified in `.markdownlint.yml`
- Always run `just lint` before committing to ensure code quality
- Whenever you modify the codebase, make sure to also update all CLAUDE.md files (if necessary)
- Tests must cover the functionality being implemented.
- NEVER ignore the output of the system or the tests - Logs and messages often contain CRITICAL information.
- If the logs are supposed to contain errors, capture and test it.

### Getting help

- ALWAYS ask for clarification rather than making assumptions.
- If you're having trouble with something, it's ok to stop and ask for help.

### TDD (Test-Driven Development) Implementation Process

- Write a failing test that defines a desired function or improvement
- Run the test to confirm it fails as expected
- Write minimal code to make the test pass
- Run the test to confirm success
- Refactor code to improve design while keeping tests green
- Repeat the cycle for each new feature or bugfix
- If you want to adjust a test for any reason, ask for confirmation, even if you suspect the test to contain the error.

### Learning-Focused Error Response

When encountering tool failures (ruff, pytest, etc.):

- Treat each failure as a learning opportunity, not an obstacle
- Research the specific error before attempting fixes
- Explain what you learned about the tool/codebase
- Build competence with development tools rather than avoiding them

### Technology preferences

- never install python packages globally with `pip3 install <package>`.
  Always use virtual environments, with `uv`.
- Always use `pathlib` for paths. Avoid `os.path`, and avoid passing around paths as strings.
- Please use modern python syntax and modern patterns.
- Avoid writing classes with a lot of state and behaviour.
  Only use classes to bundle data (with the `dataclasses` library).
  For state and behaviour, please use functions instead of classes.
