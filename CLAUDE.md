# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup

- **Install dependencies**: `uv sync --all-extras --dev`
- **Activate virtual environment**: `source .venv/bin/activate`
- **Install pre-commit hooks**: `pre-commit install`

### Code Quality and Linting

- **Run all linters**: `just lint`
- **Format code**: `just format`
- **Type checking**: `just mypy` (uses dmypy daemon for faster runs)
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

DSP-TOOLS is a CLI tool for interacting with the DaSCH Service Platform (DSP) API.
The codebase is organized into several key modules:

### Core Components

#### CLI Module (`src/dsp_tools/cli/`)

- **Entry point**: `entry_point.py` - Main CLI entry point with argument parsing and version checking
- **Argument parsing**: `create_parsers.py` - Creates CLI argument parsers for all commands
- **Action dispatcher**: `call_action.py` - Routes parsed arguments to appropriate command handlers

#### Commands Module (`src/dsp_tools/commands/`)

Each subdirectory implements a specific CLI command:

- **excel2json/**: Convert Excel files to JSON project definitions
- **excel2xml/**: Convert Excel files to XML data files
- **project/**: Create and retrieve (get) DSP projects from JSON definitions
- **xmlupload/**: Upload resources defined in XML data files to DSP server
- **ingest_xmlupload/**: Workflow for uploading resources if the referenced multimedia files are too big for the
  "xmlupload" command
- **validate_data/**: Validate XML data against project ontologies using SHACL
- **resume_xmlupload/**: Resume interrupted XML uploads

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
- **E2E tests**: Test full workflows with testcontainers running DSP stack
- **Benchmarking tests**: Performance testing for critical algorithms

### Configuration

- **pyproject.toml**: Project metadata, dependencies, and tool configurations
- **justfile**: Task runner with commands for development workflow
- **Pre-commit hooks**: Automated code quality checks on commit

## Important Notes

- Always run `just lint` before committing to ensure code quality
- Use `dmypy restart` if mypy behaves unexpectedly
- The project uses strict type checking - all new code must have proper type annotations
- Documentation follows Google-style docstrings
- Line length limit is 120 characters
- Use `uv add package` to add dependencies (or `uv add --dev package` for dev dependencies)
- All markdown files must comply with markdownlint rules specified in `.markdownlint.yml`
    - URLs must be wrapped in angle brackets `<url>` or formatted as proper links `[text](url)` (MD034)
- Always use descriptive variable names
- **Pull request reviews**: Only request reviews from team members of <https://github.com/dasch-swiss>
    - Usual reviewers: BalduinLandolt, Nora-Olivia-Ammann, Notheturtle, seakayone, jnussbaum
    - Ivan (subotic) is also a team member but only rarely asked for reviews
