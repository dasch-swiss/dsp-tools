# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is validate_data?

The `validate_data` module is a CLI command that validates XML data files against ontologies stored on a DSP server. 
It performs comprehensive validation using SHACL (Shapes Constraint Language) 
to ensure data conforms to ontological constraints before upload.

## Key Components

### Core Entry Points

- **validate_data.py**: Main validation orchestrator with two public functions:
    - `validate_data()`: Validates XML files from filesystem
    - `validate_parsed_resources()`: Validates pre-parsed resources (used by the CLI commands `xmlupload` and `ingest-xmlupload`)

### API Clients (`api_clients.py`)

- **OntologyClient**: Fetches project ontologies and knora-api ontology from DSP server
- **ListClient**: Retrieves and reformats project lists for validation
- **ShaclValidator**: Sends RDF data to DSP server's SHACL validation endpoint

### Data Processing Pipeline

1. **XML Parsing**: XML → ParsedResource objects
2. **RDF Conversion**: ParsedResource → RDF-like data → RDF Graph
3. **SHACL Generation**: Project ontology → SHACL shapes graphs
4. **Validation**: RDF data + SHACL shapes → Validation report

### Models

- **models/validation.py**: Core data structures for RDF graphs and validation results
- **models/api_responses.py**: API response models for ontologies, lists, and validation reports
- **models/input_problems.py**: User-facing error/warning message structures
- **models/rdf_like_data.py**: Intermediate data structures for RDF conversion

### SPARQL Queries (`sparql/`)

- **construct_shacl.py**: Main SHACL shape construction coordinator
- **cardinality_shacl.py**: Generates cardinality constraint shapes
- **value_shacl.py**: Generates value content validation shapes
- **legal_info_shacl.py**: Generates license validation shapes

### Validation Flow

```text
XML file → ParsedResource → RDF-like data → RDF Graph
                                              ↓
Project ontology → SHACL shapes ← ← ← ← ← ← ← ← 
                     ↓
           SHACL Validation → Validation Report → User Messages
```

## Architecture Patterns

### Four-Stage Validation

1. **Unknown Classes**: Ensure that no classes are used in the data that are not defined in the ontology. 
   If unknown classes are found, the validation process ends with an error message to the user.
2. **Ontology Validation**: Validate that the ontology itself is correct.
   If errors are found, the validation process ends with an error message to the user.
3. **Cardinality Validation**: Checks min/max cardinality constraints
4. **Content Validation**: Validates actual values, types, and patterns

### Client-Server Architecture

- API clients handle all server communication
- Validation logic is separated from network concerns
- Proper error handling and logging for failed requests

### Data Pipeline Pattern

- Clear transformation steps: XML → ParsedResource → RDF-like → RDF Graph
- Each step has dedicated mappers and converters
- Immutable data structures where possible

### Problem Categorization

Validation results are categorized into:

- **Violations**: Critical errors that prevent xmlupload
- **Warnings**: Issues that block upload on production servers
- **Info**: Potential problems that don't block upload
- **Unexpected**: Unknown SHACL violations requiring dev team attention

## Key Dependencies

- **rdflib**: RDF graph manipulation and SPARQL queries
- **requests**: HTTP communication with DSP server
- **loguru**: Structured logging throughout validation process

## Testing Strategy

- **Unit tests**: Test individual validation components
- **Integration tests**: Test API client interactions
- **E2E tests**: Test complete validation workflows with testcontainers

## Important Notes

- Validation is performed server-side using DSP's SHACL validation endpoint
- All RDF serialization uses Turtle format for server communication
- Graph saving functionality exists for debugging complex validation failures
- Production servers have stricter validation (warnings become blockers)
- The module handles both direct XML file validation and pre-parsed resource validation (for xmlupload integration)
