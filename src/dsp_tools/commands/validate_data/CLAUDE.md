# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is validate_data?

The `validate_data` module is a CLI command that validates XML data files against ontologies stored on a DSP server. 
It performs comprehensive validation using SHACL (Shapes Constraint Language) via a Docker-based CLI tool
to ensure data conforms to ontological constraints before upload.

## Key Components

### Core Entry Points

- **validate_data.py**: Main validation orchestrator with two public functions:
    - `validate_data()`: Validates XML files from filesystem
    - `validate_parsed_resources()`: Validates pre-parsed resources (used by the CLI commands `xmlupload` and `ingest-xmlupload`)

### SHACL Validation Engine

- **shacl_cli_validator.py**: Docker-based SHACL validation engine that:
    - Runs SHACL validation using a containerized CLI tool
    - Handles Docker communication and error handling
    - Parses validation results back into Python objects
    - Requires Docker Desktop to be running

### Data Preparation Pipeline (`prepare_data/`)

- **prepare_data.py**: Main data preparation coordinator with functions:
    - `get_info_and_parsed_resources_from_file()`: Extracts resources from XML files
    - `prepare_data_for_validation_from_parsed_resource()`: Prepares data for validation
- **get_rdf_like_data.py**: Converts ParsedResource objects to RDF-like data structures
- **make_data_graph.py**: Creates RDF graphs from RDF-like data

### Validation Pipeline (`validation/`)

- **get_validation_report.py**: Main validation orchestrator that coordinates SHACL validation
- **check_for_unknown_classes.py**: Validates that all classes used in data are defined in the ontology
- **validate_ontology.py**: Validates the ontology itself before data validation
- **check_duplicate_files.py**: Checks for duplicate file references in the data

### Validation Report Processing (`process_validation_report/`)

- **query_validation_result.py**: Processes SHACL validation results into user-friendly formats
- **get_user_validation_message.py**: Converts validation problems into user messages

### API Clients (`api_clients.py`)

- **OntologyClient**: Fetches project ontologies and knora-api ontology from DSP server
- **ListClient**: Retrieves and reformats project lists for validation

### Models

- **models/validation.py**: Core data structures for RDF graphs and validation results
- **models/api_responses.py**: API response models for ontologies, lists, and validation reports
- **models/input_problems.py**: User-facing error/warning message structures
- **models/rdf_like_data.py**: Intermediate data structures for RDF conversion

### SHACL Shape Generation (`sparql/`)

`sparql/` contains the shapes that are ontology specific and are generated during runtime. 

- **construct_shacl.py**: Main SHACL shape construction coordinator
- **cardinality_shacl.py**: Generates cardinality constraint shapes
- **value_shacl.py**: Generates value content validation shapes
- **legal_info_shacl.py**: Generates license validation shapes

### Ontology Independent SHACL Shapes

`src/dsp_tools/resources/validate_data/` contains RDF turtle files with SHACL shapes that apply to all ontologies.

### Utility Functions

- **constants.py**: Defines file paths for validation artifacts and RDF property type information
- **utils.py**: Helper functions for:
    - Temporary directory management (`get_temp_directory()`, `clean_up_temp_directory()`)
    - IRI reformatting for user-friendly display
    - Validation file cleanup and organization
- **mappers.py**: Data transformation utilities for converting between different data representations

### Validation Flow

```text
XML file → ParsedResource → RDF-like data → RDF Graph
                                              ↓
Project ontology → SHACL shapes ← ← ← ← ← ← ← ← 
                     ↓
           Docker SHACL CLI → Validation Report → User Messages
```

## Architecture Patterns

### Four-Stage Validation Pipeline

The validation process follows a strict sequential pipeline:

1. **Unknown Classes Check** (`validation/check_for_unknown_classes.py`): 
   - Ensures all classes used in data are defined in the ontology
   - If unknown classes are found, validation terminates with an error
2. **Ontology Validation** (`validation/validate_ontology.py`): 
   - Validates the ontology itself for correctness
   - If ontology errors are found, validation terminates with an error
3. **Duplicate File Check** (`validation/check_duplicate_files.py`):
   - Checks for duplicate file references in the data
   - Generates warnings which will be added to potential warnings from the SHACL validation
4. **SHACL Validation** (`validation/get_validation_report.py`):
   - Performs comprehensive SHACL validation using Docker CLI
   - Validates both cardinality constraints and content validation
   - Generates detailed validation reports

### Docker-Based Validation Architecture

- **Containerized SHACL**: Uses a Docker container for SHACL validation to ensure consistency
- **File-based Communication**: Writes RDF files to temporary directories for Docker processing
- **Error Handling**: Robust error handling for Docker communication failures
- **Temporary File Management**: Automatic cleanup of temporary validation files

### Modular Data Processing Pipeline

- **Data Preparation** (`prepare_data/`): Converts XML to RDF-ready data structures
- **Validation Execution** (`validation/`): Performs validation checks in sequence
- **Report Processing** (`process_validation_report/`): Converts validation results to user messages
- **Clear Separation**: Each stage has dedicated modules with well-defined interfaces

### Problem Categorization and Severity Levels

Validation results are categorized into:

- **Violations**: Critical errors that prevent xmlupload (always displayed)
- **Warnings**: Issues that block upload on production servers (displayed based on severity setting)
- **Info**: Potential problems that don't block upload (displayed only with INFO severity)
- **Unexpected**: Unknown SHACL violations requiring dev team attention (always displayed)

## Key Dependencies

- **rdflib**: RDF graph manipulation and SPARQL queries
- **Docker**: Required for containerized SHACL validation
- **subprocess**: For executing Docker commands
- **pandas**: For handling large validation result datasets
- **yaml**: For parsing Docker configuration files
- **loguru**: Structured logging throughout validation process

## Testing Strategy

- **Unit tests**: Test individual validation components
- **Integration tests**: Test API client interactions
- **E2E tests**: Test complete validation workflows with testcontainers

## Important Notes

- **Docker Requirement**: Validation requires Docker Desktop to be running for SHACL validation
- **Local SHACL Validation**: Validation is performed locally using a Docker container, not server-side
- **Temporary File Management**: Creates temporary files for Docker communication, automatically cleaned up
- **Graph Saving**: Optional graph saving functionality for debugging complex validation failures  
- **Production Behavior**: Production servers treat warnings as blockers, preventing upload
- **Dual Interface**: Supports both direct XML file validation and pre-parsed resource validation (for xmlupload integration)
- **Configuration Support**: Uses ValidateDataConfig for controlling validation behavior and output options
- **CSV Output**: Large validation results are saved as CSV files for better handling
- **Severity Levels**: Configurable severity levels control which validation messages are displayed
