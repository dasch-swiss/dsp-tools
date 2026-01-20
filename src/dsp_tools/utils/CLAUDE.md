# Utils Module - Quick Reference

This directory contains reusable utility functions organized by use case.
All utilities follow functional programming patterns (stateless functions, no classes with behavior).

These utilities are shared by code not to form interdependencies between the commands,
but because the input / output or interaction with outside services are shared.

If the interaction is for a specific HTTP route then add the functionality to the `src/dsp_tools/clients/`.

## API Communication & Request Handling

**`request_utils.py`**

- HTTP request helpers with retry logic and exponential backoff
- Request/response logging with sensitive data sanitization, ensures that logging is consistent
- Error handling for timeouts, server errors, and connection issues
- Used throughout: All commands that interact with DSP-API (create, xmlupload, get, etc.)

## Data Format Validation & Parsing

**`data_formats/date_util.py`**

- Parse and validate DSP date strings (calendar:era:yyyy-mm-dd:era:yyyy-mm-dd)
- Used in: XML upload workflows, date value validation

**`data_formats/iri_util.py`**

- Validate IRIs and resource IRIs
- Convert between DSP IRIs and prefixed IRIs
- Check if IRI belongs to a DSP project
- Generate DSP ontology prefixes
- Used in: All resource and ontology operations

**`data_formats/uri_util.py`**

- Validate generic URIs
- Validate IIIF URIs (for image resources)
- Check if server is production-like
- Used in: XML upload for multimedia resources, server configuration

**`data_formats/shared.py`**

- Simplify names for use as node names (normalize unicode, handle special chars)
- Check if values are usable for data archiving (not NA/None/empty)
- Used in: Excel to JSON/XML conversions, data cleaning

## XML Processing

**`xml_parsing/parse_clean_validate_xml.py`**

- Parse XML files with error handling
- Remove comments and processing instructions
- Validate against XSD schema
- Transform to localnames
- Acts as an anti-corruption layer for the input XML
- Used in: All XML-based commands (xmlupload, validate-data, id2iri)

**`xml_parsing/get_parsed_resources.py`**

- Transform validated XML etree into `ParsedResource` models
- Convert local names to absolute IRIs using ontology mapping
- Parse different resource types (resource, region, link, audio/video segments)
- Extract resource values, file metadata, and migration metadata
- Core transformation in XML processing pipeline: validated XML → Python models
- Used in: XML upload and validation workflows

**`xml_parsing/get_lookups.py`**

- Extract authorship information from XML
- Extract permissions definitions from XML
- Used in: XML upload workflows for resource metadata

**`xml_parsing/models/parsed_resource.py`**

- Data models for parsed XML resources and values
- Type definitions for Knora value types
- Pyton abstraction of the data XML forms the base for work with the XML
- Used in: XML processing pipeline

**`xsd_validation_error_msg.py`**

- Format XSD validation error messages
- Bundle line number, element, attribute, and message
- Used in: XML validation error reporting

**`replace_id_with_iri.py`**

- Replace internal XML IDs with IRIs using id2iri mapping
- Handle link values and richtext references
- Detect duplicate IDs between mapping and new data
- Used in: id2iri command for incremental uploads

## JSON Processing

**`json_parsing.py`**

- Parse JSON files with comprehensive error handling
- Raise user-friendly errors for malformed JSON
- Acts as an anti-corruption layer for the JSON
- Used in: All commands that read JSON config files (create, get, id2iri)

## RDF/Semantic Web

**`rdf_constants.py`**

- DSP/Knora RDF namespace constants and prefixes
- Type aliases for rdflib nodes
- Namespace mappings for ontology operations
- Used in: validate-data command, ontology operations

**`rdflib_utils.py`**

- Serialize RDF graphs to JSON-LD
- Used in: validate-data command for SHACL validation

## Database & Server Monitoring

**`fuseki_bloating.py`**

- Calculate database size growth during upload
- Warn/alert when database bloating exceeds thresholds (10GB warning, 20GB critical)
- Communicate disk space concerns to users
- Used in: XML upload workflows on test servers

## Error Handling

**`exceptions.py`**

- Custom exception classes for user errors and system errors
- Used throughout: All modules for consistent error handling

## Architecture Principles: Utils vs. Commands

### The Core Principle: Commands Don't Import From Each Other

**Commands should NEVER import from other commands.**
If two commands need the same functionality, that functionality belongs in utils.

This architecture prevents tight coupling and makes commands independent, testable, and maintainable.

```
✅ GOOD: Commands import from utils
commands/xmlupload/ ──→ utils/request_utils.py
commands/create/    ──→ utils/request_utils.py

❌ BAD: Commands import from each other
commands/xmlupload/ ──→ commands/create/some_helper.py
```

### When to Put Code in Utils

Code belongs in utils when:

1. **Multiple commands need it** - If 2+ commands use the same logic for API calls, parsing, or validation
2. **It handles shared input/output** - Processing files, user input, or API responses that multiple commands deal with
3. **It interacts with external services** - HTTP requests, database operations, file I/O that's used across commands
4. **It's a reusable transformation** - Date parsing, IRI validation, XML cleaning that's needed in multiple contexts

Code does NOT belong in utils when:

- It's specific to one command's business logic
- It orchestrates a workflow unique to that command
- It contains command-specific configuration or state
- It's only used once and unlikely to be reused

### Avoiding Interdependencies While Reducing Redundancy

The utils layer acts as a **shared foundation** that enables code reuse without creating dependencies between commands:

```
Command Layer (independent):
  xmlupload/     validate-data/     create/     id2iri/

Utils Layer (shared foundation):
  request_utils.py   xml_parsing/   data_formats/   json_parsing.py
```

**Key Rules:**

1. **Utilities are stateless** - No classes with behavior, only pure functions and data classes
2. **Utilities have clear contracts** - Well-defined inputs/outputs, consistent error handling
3. **Utilities are self-contained** - Don't depend on command-specific context or state
4. **Commands own their orchestration** - Utils provide building blocks, commands combine them into workflows

## General Guidelines for Reuse

**Validation Functions:**
- All validation functions return boolean or raise exceptions (no silent failures)
- Compose validation functions before sending data to API
- Use `data_formats/` validators for all user input

**Parsing Functions:**
- All parsing functions raise user-friendly errors with context
- Act as anti-corruption layers between external data and internal models
- Always use `json_parsing.py` and `xml_parsing/` instead of raw parsing

**Request Functions:**
- Never make direct HTTP requests without `request_utils.py`
- Ensures consistent logging, error handling, and retry logic

**XML Processing:**
- XML parsing utilities are pipeline-oriented - use in sequence:
  1. `parse_clean_validate_xml.py` - Parse and validate
  2. `get_parsed_resources.py` - Transform to models
  3. `get_lookups.py` - Extract metadata
- Each stage has clear input/output contracts

## Pattern Summary

**When you see code duplication across commands:**

1. Extract the shared logic to an appropriate utils module
2. Make it stateless and self-contained
3. Give it a clear, single-purpose function
4. Update all commands to use the new utility
5. Both commands now share the implementation without depending on each other
