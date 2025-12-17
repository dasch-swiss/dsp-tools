# CLAUDE.md - create command

This file provides guidance to Claude Code when working with the `create` command in DSP-TOOLS.

## What is the create command?

The `create` command creates a complete project with its data models (ontologies) on a DSP server from a JSON project
definition file. It handles:

- Project metadata creation
- List hierarchies (controlled vocabularies)
- User groups and users
- Ontologies (classes, properties, cardinalities)
- Default permissions (DOAPs)

This is one of the two main tasks DSP-TOOLS serves (the other being `xmlupload` for data upload).

## Architecture Overview

### Core Entry Point

- **create.py**: Main entry point containing `create()` function and workflow orchestration
    - Calls validation/parsing
    - Executes creation in strict sequential order
    - Collects and reports problems

### Key Workflow Stages

The create command follows a strict sequential pipeline:

```text
JSON file → JSON Schema validation → Parse to models → Complex validation
                                                              ↓
                                                        ParsedProject
                                                              ↓
                    Sequential creation on server:
                    1. Project metadata
                    2. Lists
                    3. Groups
                    4. Users (with group memberships)
                    5. Ontologies (ontology → classes → properties → cardinalities)
                    6. Default permissions (DOAPs)
```

### Directory Structure

- **parsing/**: JSON parsing and transformation to typed models
- **models/**: Data models (parsed project, parsed ontology, problems, server info, RDF ontology)
- **serialisation/**: RDF/JSON-LD serialization for DSP-API (ontology.py, project.py)
- **create_on_server/**: API calls to create entities on server (includes mappers.py for cardinality mapping)
- **project_validate.py**: Validation orchestration (JSON Schema + complex validations)
- **create.py**: Main workflow orchestration
- **communicate_problems.py**: User-facing error reporting
- **exceptions.py**: Custom exceptions
- **lists_only.py**: Standalone list creation workflow

## Validation Architecture

### Three-Phase Validation

The validation process happens in three distinct phases:

#### Phase 1: JSON Schema Validation (`project_validate.py`)

- **Function**: `_validate_with_json_schema()`
- **Purpose**: Structural validation against JSON schema
- **Schema Location**: `src/dsp_tools/resources/schema/project.json`
- **Validates**:
    - Required fields presence
    - Field types and formats
    - Basic structure compliance

#### Phase 2: IRI Resolution During `parsing/`

During the parsing the prefixes are resolved to absolute IRIs.
If a prefix is not defined, the prefix and a `InputProblem` is returned.
After all the objects are parsed, either `ParsedProject` or `list[CollectedProblems]` is returned.
In case of the `list[CollectedProblems]` further validations are not possible,
therefore the code stops and the user is informed.

#### Phase 3: Complex Validation (`project_validate.py`)

After parsing to typed models, complex semantic validations are performed in `_complex_parsed_project_validation()`:

- **Duplicate class names** within one ontology
- **Duplicate property names** within one ontology
- **Undefined super classes** (references to non-existent classes)
- **Undefined super properties** (references to non-existent properties)
- **Undefined properties in cardinalities**
- **Circular references in mandatory property cardinalities**
    - Detects cycles using `rustworkx` graph analysis
    - Warns if mandatory (`1` or `1-n`) cardinalities exist in cycles
    - Required because circular data needs temporary property removal during upload
- **Duplicate list names**
- **Duplicate node names** across all lists
- **Invalid default_permissions_overrule** (`_check_for_invalid_default_permissions_overrule()`):
    - Skipped when `default_permissions` is `private` (cannot be overruled)
    - For `overrule_private`: validates all referenced IRIs exist in the ontology (properties or classes)
    - For `overrule_limited_view`:
        - If selection mode: validates that all referenced IRIs exist and are `StillImageRepresentation` subclasses
        - If `ALL` or `NONE`: no validation needed
    - Still image class detection traverses the complete inheritance chain from `knora-api:StillImageRepresentation`

### Problem Collection Pattern

Instead of failing fast, the create command collects all problems:

- **Models**: `CollectedProblems` groups related problems with a message
- **Problem Types**: `InputProblem`, `CreateProblem` for different error sources
- **Display**: `communicate_problems.py` formats problems for user display
- **Return Type**: Functions return `ParsedProject | list[CollectedProblems]`
- **Benefit**: Users see all issues at once, not just the first error

## Parsing Pipeline (`parsing/`)

### parse_project.py

Main orchestrator for parsing the complete JSON project:

- **Entry**: `parse_project()` - takes raw JSON dict, returns `ParsedProject` or problems
- **Creates prefix lookup**: Maps ontology names to full IRI prefixes
- **Parses sections**:
    - Project metadata (shortcode, shortname, longname, descriptions, keywords, licenses)
    - Permissions (default permissions + overrule settings)
    - Groups (name + multilingual descriptions)
    - Users (credentials, project admin status, group memberships)
    - Lists (hierarchical controlled vocabularies)
    - Ontologies (classes, properties, cardinalities)

### parse_ontology.py

Parses individual ontologies:

- **Entry**: `parse_ontology()` - parses one ontology from JSON
- **Parses**:
    - Properties: name, labels, comments, supers, object type, GUI element, subject restrictions, list references
    - Classes: name, labels, comments, supers
    - Cardinalities: property references, cardinality values (`0-1`, `1`, `0-n`, `1-n`), GUI order
- **IRI Resolution**: Converts prefixed references (`:ClassName`, `otheronto:PropName`) to absolute IRIs
- **Validation**: Checks that all prefix references can be resolved

### parse_lists.py

Parses hierarchical list structures:

- **Entry**: `parse_list_section()` - parses all lists
- **Handles**: Recursive node structures with multilingual labels

### parsing_utils.py

Shared parsing utilities:

- **Prefix lookup creation**: `create_prefix_lookup()` builds ontology name → IRI mapping
- **IRI resolution**: `resolve_to_absolute_iri()` and `resolve_all_to_absolute_iri()`
    - Handles `:localRef` (same ontology)
    - Handles `prefix:Ref` (other ontology)
    - Handles absolute IRIs (pass through)

## Creation on Server (`create_on_server/`)

All creation follows strict sequential order because of dependencies.

### Sequential Creation Order

**1. Project** (`project.py: create_project()`)

- Creates project metadata on server
- Returns project IRI for subsequent operations
- Handles `exit_if_exists` flag

**2. Lists** (`lists.py: create_lists()`)

- Creates hierarchical list structures
- Returns mapping of list names → list IRIs
- Needed before properties (for `ListValue` properties)
- If no lists in JSON, fetches existing lists from server

**3. Groups** (`group_users.py: create_groups()`)

- Creates user groups
- Returns group name → IRI lookup
- Fetches existing groups first to avoid duplicates

**4. Users** (`group_users.py: create_users()`)

- Creates users with credentials
- Assigns project admin status
- Assigns group memberships (requires group IRIs from step 3)

**5. Ontologies** (`complete_ontologies.py: create_ontologies()`)

The order is important because the ontology must exist before information can be added to it.
Classes may be referenced by link properties (as `object` or `subject`).
As cardinalities reference both classes and properties, they must come last.

It is not possible to upload all classes / properties of one ontology and then move to the next,
as there may be inter-ontology references. Therefore, all are put together and a topological sorting is done.

A challenge here is the `lastModificationDate` of the ontology. It must always be provided in the API request.
As we have to mix the ontologies in the call, it is important to keep track of the dates.
In order not to stop a creation unnecessarily,
we try to recover from a wrong modification date by repeating the API call once.

So that we have the highest safety, we create a lookup of the modification dates before `create_all_properties()`
and before `create_all_classes()`.
Cardinalities can be sorted by ontology, as they do not have any inter-ontology dependencies.

- Sequential sub-stages:
    - a. Create a ontology (`ontology.py: create_all_ontologies()`)
    - b. Create all classes (`classes.py: create_all_classes()`)
    - c. Create all properties (`properties.py: create_all_properties()`)
    - d. Add cardinalities to classes (`cardinalities.py: add_all_cardinalities()`)
- Returns `CreatedIriCollection` with all created IRIs

**6. Default Permissions** (`default_permissions.py: create_default_permissions()`)

- Creates DOAP (Default Object Access Permission) settings
- Uses created IRIs from ontology creation

### Why This Order Matters

- **Lists before Properties**: Properties with `ListValue` object need list IRIs
- **Classes before Properties**: Some properties have `subject` restrictions requiring class IRIs
- **Properties before Cardinalities**: Cardinalities reference properties by IRI
- **Groups before Users**: User memberships need group IRIs
- **Ontologies before Permissions**: DOAPs reference ontology entity IRIs

### Handling Existing Entities

- **Ontologies**: Checks if ontology exists, only creates new ones
- **Lists**: If no lists in JSON, fetches existing from server
- **Groups**: Fetches existing groups before creating new ones
- **Result**: Can add to existing project without conflicts

## Serialization (`serialisation/`)

Converts parsed models to JSON or RDF/JSON-LD for DSP-API consumption.

### project.py

Serialization functions for project-level entities:

- **`serialise_project()`**: Project metadata to JSON
- **`serialise_one_group()`**: Group with descriptions to JSON
- **`serialise_one_user_for_creation()`**: User credentials to JSON

### ontology.py

Core serialization functions using `rdflib`:

- **`serialise_ontology_graph_for_request()`**: Ontology metadata
- **`serialise_class_graph_for_request()`**: Class with labels, comments, supers
- **`serialise_property_graph_for_request()`**: Property with all attributes
- **`serialise_cardinality_graph_for_request()`**: Cardinality restrictions

### RDF Structure

All entity requests contain:

- Base ontology graph with `lastModificationDate`
- Entity graph with RDF triples
- JSON-LD serialization for DSP-API

### Cardinality Mapping (`create_on_server/mappers.py`)

Maps parsed cardinality values to OWL restrictions:

- `1` → `owl:cardinality 1`
- `0-1` → `owl:maxCardinality 1`
- `1-n` → `owl:minCardinality 1`
- `0-n` → `owl:minCardinality 0`

## Data Models (`models/`)

### parsed_project.py

- **`ParsedProject`**: Complete project with all sections
- **`ParsedProjectMetadata`**: Project info (shortcode, names, descriptions)
- **`ParsedPermissions`**: Default permissions + overrule settings
- **`ParsedGroup`**: Group with multilingual descriptions
- **`ParsedUser`**: User credentials and info
- **`ParsedList`**: Hierarchical list with nodes

### parsed_ontology.py

- **`ParsedOntology`**: Complete ontology (classes, properties, cardinalities)
- **`ParsedClass`**: Class with labels, comments, supers
- **`ParsedProperty`**: Property with object type, GUI element, supers
- **`ParsedClassCardinalities`**: Cardinalities for one class
- **`ParsedPropertyCardinality`**: Single cardinality (property + value + GUI order)
- **Enums**: `Cardinality`, `GuiElement`, `KnoraObjectType`

### create_problems.py

- **`CollectedProblems`**: Group of related problems with message
- **`InputProblem`**: User input validation error
- **`CreateProblem`**: Server creation error
- **`InputProblemType`**: Enum of all problem types

### server_project_info.py

- **`ProjectIriLookup`**: Maps ontology names to IRIs
- **`ListNameToIriLookup`**: Maps list names to IRIs
- **`CreatedIriCollection`**: Tracks all created entity IRIs

### rdf_ontology.py

- **`RdfCardinalityRestriction`**: RDF representation of cardinality restrictions for OWL serialization

## Error Handling and Problem Reporting

### Generic HTTP Error Handling

API calls can fail in unpredictable ways. Current handling:

- **Approach**: Generic error handling for HTTP failures
- **Limitation**: Not all error types are known in advance
- **Future**: Specific error handling may be added as patterns emerge

### Problem Communication

**`communicate_problems.py`** formats problems for user display:

- **`print_problem_collection()`**: Single problem group
- **`print_all_problem_collections()`**: Multiple problem groups
- **Format**: Clear, structured output with problem types and locations

### Success Reporting

After successful creation:

- Logs success message with project info
- Or logs warning if some problems occurred but project was created

## Utility Modules

### onto_utils.py

- **`get_project_iri_lookup()`**: Fetches existing ontologies from server
- Used to check which ontologies already exist before creation

### exceptions.py

- **`ProjectJsonSchemaValidationError`**: JSON Schema validation failures

## Client Usage

The create command uses several clients (detailed in `src/dsp_tools/clients/CLAUDE.md`):

- **`AuthenticationClient`**: Authentication and token management
- **`OntologyCreateClient`**: Create ontologies, classes, properties, cardinalities
- **`GroupClient`**: Create and fetch groups
- **`PermissionsClient`**: Create default permissions
- **List clients**: Fetch and create lists

## Important Notes

### API Call Reliability

While extensive validation happens before API calls, HTTP requests can still fail:

- API errors may be unpredictable
- Currently handled generically
- Specific error handling may be added as patterns emerge

### Validation Coverage

The command validates extensively:

- Structural correctness (JSON Schema)
- Semantic correctness (references, duplicates, cycles)
- But cannot guarantee server acceptance (server may have additional rules)

### Problem Collection vs. Fail-Fast

The command prefers showing all problems at once:

- Validation collects all problems before stopping
- Creation continues even if some entities fail (where possible)
- Final report shows overall success and all issues

### Prefix Resolution

All entity references use prefix resolution:

- `:localName` → resolved to current ontology
- `prefix:Name` → resolved to other ontology
- Absolute IRIs → used as-is
- Invalid references → collected as problems

## Testing Considerations

- Unit tests focus on parsing and validation logic
- Integration tests verify the full workflow
- E2E tests use testcontainers for complete server interaction
- Mock clients for testing without server dependencies
