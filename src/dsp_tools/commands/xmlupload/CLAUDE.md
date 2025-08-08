# CLAUDE.md - xmlupload command

This file provides guidance to Claude Code when working with the `xmlupload` command in DSP-TOOLS.

## Module Overview

The `xmlupload` package implements the core functionality for uploading XML data files to a DSP server. 
It handles the complete workflow from XML parsing and validation to resource creation on the DSP server, including:

- XML file parsing and validation
- Resource processing and transformation
- Circular reference resolution via stashing
- Upload of multimedia files referenced in the XML file, and ingest management
- RDF graph generation for DSP-API
- Error handling and recovery mechanisms

## Architecture

### Core Entry Point

- **xmlupload.py**: Main entry point containing the `xmlupload()` function and workflow orchestration
- **upload_config.py**: Configuration management for upload operations

### Key Workflow Stages

1. **XML Input Processing** (`prepare_xml_input/`)
   - Parse and validate XML files
   - Transform input values to processed format
   - Resolve ARKs to IRIs
   - Validate IIIF URIs and check if bitstreams (i.e. referenced multimedia files) exist

2. **Resource Processing** (`models/processed/`)
   - Transform parsed resources to processed format
   - Handle permissions and metadata
   - Manage file values and IIIF URIs

3. **Circular Reference Handling** (`stash/`)
   - Detect circular references between resources
   - Create stash for problematic references
   - Generate upload order to resolve dependencies

4. **RDF Graph Generation** (`make_rdf_graph/`)
   - Convert processed resources to RDF graphs
   - Handle file values and metadata
   - Generate JSON-LD for DSP API consumption

5. **Resource Creation**
   - Upload resources to DSP server via API calls
   - Handle file ingestion process
   - Manage upload state and recovery

### Key Components

#### prepare_xml_input/

- **prepare_xml_input.py**: Main orchestration for XML processing pipeline
- **read_validate_xml_file.py**: XML file reading and validation logic
- **get_processed_resources.py**: Transform parsed resources to processed format
- **transform_input_values.py**: Value transformation utilities
- **ark2iri.py**: ARK to IRI resolution
- **iiif_uri_validator.py**: IIIF URI validation
- **list_client.py**: Client for list node lookups

#### models/

- **processed/**: Data models for processed resources and values
    - **res.py**: `ProcessedResource` and `MigrationMetadata` models
    - **values.py**: Various processed value types
    - **file_values.py**: Value models for Files
- **lookup_models.py**: Lookup tables for IRIs and XML references
- **upload_state.py**: State management for upload operations
- **upload_clients.py**: Client collection for various services
- **ingest.py**: File ingest process models
- **permission.py**: Permission handling models
- **bitstream_info.py**: Bitstream metadata models
- **input_problems.py**: Input validation problem tracking

#### stash/

- **stash_models.py**: Data models for stashing circular references
    - `StandoffStash`: Manages stashed RichtextValue with standoff markup
    - `StandoffStashItem`: Individual stashed RichtextValue
    - `LinkObjStash`: Manages stashed LinkValue references
- **stash_circular_references.py**: Logic for detecting and stashing circular references
- **analyse_circular_reference_graph.py**: Graph analysis for upload ordering
- **create_info_for_graph.py**: Graph information extraction
- **upload_stashed_resptr_props.py**: Upload stashed resource pointer properties
- **upload_stashed_xml_texts.py**: Upload stashed XML text values

#### make_rdf_graph/

- **make_resource_and_values.py**: Main RDF graph creation logic, creates resources and calls other functionalities
- **make_values.py**: RDF generation for various value types
- **make_file_value.py**: File value RDF generation
- **jsonld_utils.py**: JSON-LD serialization utilities
- **constants.py**: RDF-related constants and mappings

#### Client Classes

- **resource_create_client.py**: `ResourceCreateClient` for creating resources via DSP API
- **project_client.py**: `ProjectClient` for project-related operations
- **iri_resolver.py**: IRI resolution utilities

#### Utilities

- **write_diagnostic_info.py**: Generates JSON files mapping XML resource IDs to DSP server IRIs 
  for troubleshooting and post-upload reference

## Key Data Models

### ProcessedResource

The central data model representing a fully processed resource ready for upload:
The class `ProcessedResource` in `models/processed/res.py`

The `ProcessedResource` is created from the `ParsedResources`

### Stash Models

For handling circular references:

- **StandoffStash**: Manages stashed Richtext values with standoff markup
- **LinkObjStash**: Manages stashed resource pointer properties

### Upload Configuration

- **UploadConfig**: Central configuration management
- **UploadState**: Tracks upload progress and enables resumption

## Workflow

### Standard XMLUpload Flow

1. **Initialization**: Load configuration, authenticate, set up clients
2. **XML Processing**: Parse XML, validate structure, transform to processed resources
3. **Dependency Analysis**: Detect circular references, create stashes
4. **Upload Order Generation**: Determine optimal upload sequence
5. **Resource Creation**: Upload resources individually, handle file ingestion
6. **Stash Resolution**: Upload previously stashed references
7. **Cleanup**: Write diagnostic info, clean up temporary files

### File Handling

- Supports both local file uploads and IIIF URI references
- Integrates with DSP ingest service for file processing
- Handles various media types (images, audio, video, documents, archives)

### Error Handling

- Comprehensive error tracking and reporting
- Support for resuming interrupted uploads
- Validation at multiple stages (XML, values, permissions)
- Comprehensive diagnostic output including ID-to-IRI mappings and upload state persistence

## Diagnostic Output and Troubleshooting

### ID-to-IRI Mapping Files

The xmlupload process automatically generates diagnostic files containing mappings of internal XML IDs to DSP IRIs:

#### File Generation (`write_diagnostic_info.py`)

- **Function**: `write_id2iri_mapping(id2iri_mapping, shortcode, diagnostics)`
- **Purpose**: Creates JSON files mapping XML resource IDs to their corresponding DSP server IRIs
- **Timing**: Generated at the end of successful uploads (called in `xmlupload.py`)

#### State Management

- **Save Location**: Configurable via `DiagnosticsConfig.save_location`
- **Default Path**: `~/.dsp-tools/xmluploads/`
- **Cleanup**: State files are automatically removed after successful completion
- **Persistence**: Used for resuming interrupted uploads with `resume-xmlupload`

#### Upload State Contents

The saved state includes:

- Progress tracking for resource uploads
- Failed upload information
- Pending stash items (circular references)
- IRI resolver lookup table
- Upload configuration parameters

### Troubleshooting Workflow

#### 1. Upload Interruption Handling

When an upload fails or is interrupted:

- Upload state is preserved in `~/.dsp-tools/xmluploads/`
- ID-to-IRI mappings are written for successfully uploaded resources
- Use `dsp-tools resume-xmlupload` to continue from the last checkpoint

#### 2. Diagnostic File Analysis

- **Check ID mappings**: Verify which resources were successfully created
- **Cross-reference with XML**: Compare XML IDs with generated IRIs
- **State inspection**: Examine saved upload state for failure points

#### 3. Error Recovery

- Failed uploads are tracked in the upload state
- Stash failures prevent completion but preserve progress
- State cleanup occurs only after full success confirmation

## Important Design Patterns

### Client Abstraction


- Separate client classes for different DSP-API endpoints
- Live implementations for actual server communication
- Interface-based design for testing and mocking

### Pipeline Processing


- Multi-stage transformation pipeline from XML to RDF
- Clear separation between parsing, processing, and uploading
- Intermediate data models at each stage

### Stashing Strategy


- Sophisticated circular reference detection and resolution
- Two-phase upload process (resources first, then stashed references)
- Graph analysis for optimal upload ordering


## Testing Considerations

- Unit tests should focus on individual transformation functions
- Integration tests should verify the full pipeline with sample data
- Mock clients for testing without server dependencies
- Test circular reference scenarios thoroughly
- Validate error handling and recovery mechanisms

## Common Issues and Solutions

### Circular References

- Handled automatically via stashing mechanism
- Resources uploaded first, then cross-references added
- Graph analysis determines optimal upload order

### File Upload

- Separate file upload from data upload

### Performance Optimization

- Batch processing for large datasets
- Progress tracking with tqdm
- Memory-efficient streaming for large files

## Development Guidelines

- Follow existing patterns for client implementations
- Use dataclasses for model definitions
- Implement comprehensive error handling
- Add type hints for all new code
- Write descriptive docstrings for public functions and classes
- Use dependency injection for testability

## Key Files to Reference

When working on xmlupload functionality, these are the most important files to understand:

- `xmlupload.py` - Main upload workflow orchestration
- `prepare_xml_input/prepare_xml_input.py` - XML processing pipeline
- `models/processed/res.py` - Core ProcessedResource model
- `stash/stash_circular_references.py` - Circular reference handling
- `make_rdf_graph/make_resource_and_values.py` - RDF generation
- `resource_create_client.py` - DSP-API resource creation

## Module Dependencies

The xmlupload package depends on:

- Core DSP-TOOLS utilities (`utils/xml_parsing/`, `utils/data_formats/`)
- Client libraries (`clients/`)
- Legacy models (`legacy_models/`)
- Configuration and CLI args (`cli/args.py`)
- External libraries: `lxml`, `rdflib`, `tqdm`, `loguru`

## Integration Points

- **CLI Integration**: Called from `dsp-tools xmlupload` command
- **Validation Integration**: Uses `validate_data` module for SHACL validation
- **File Services**: Integrates with DSP ingest service for file processing
- **Authentication**: Uses authentication clients for server access
- **Logging**: Comprehensive logging throughout the pipeline
