---
dune_map: true
schema_version: 1
last_verified_commit: 96157d8f97d9f54e50c94f098f77c645fbb483d4
date: 2026-09-22
---

# ARCH-MAP.md

## Overview

DSP-TOOLS is a CLI (`dsp-tools`) that creates a DSP project's data model on a server and bulk-imports
data into it, plus a standalone `xmllib` library for programmatic XML-data-file authoring. `cli/` parses
arguments and dispatches each subcommand to its own module under `commands/`; commands share HTTP clients
(`clients/`), stateless helpers (`utils/`), static schema/shape assets (`resources/`), and a common
exception hierarchy (`error/`). The two largest workflows are `create`/`get` (JSON project file ↔ server)
and `xmlupload`/`ingest-xmlupload` (XML data file → server, either in one pass or via a resumable,
ingest-first pipeline). See `CONTEXT.md` for vocabulary once it exists. Several CLAUDE.md files state that
commands must not import each other and that `utils`/`clients`/`xmllib` must not import from `commands` —
this map found confirmed violations of both rules; see Conventions and each component's Boundary rules.

## Components

### cli

- **Paths**: `src/dsp_tools/cli/**`
- **Purpose**: Parses CLI arguments and dispatches each subcommand to its `commands/` implementation. Sole
  console-script entry point (`dsp-tools`).
- **Key entities**: `main`, `run`, `make_parser`, `call_action`, `call_action_files_only`,
  `call_action_with_network`, `ServerCredentials`
- **Public interface**: `entry_point.main()`/`run()`; the `cli.args` dataclasses (`ServerCredentials`,
  `ValidationSeverity`, `ValidateDataConfig`, `PathDependencies`, `NetworkRequirements`), imported directly
  by ~15 files under `commands/*`.
- **Local-context kit**: `entry_point.py`, `create_parsers.py`, `call_action.py`,
  `call_action_files_only.py`, `call_action_with_network.py`, `args.py`, `CLAUDE.md`
- **Depends on**: every `commands/*` component, `error`, `setup`, `utils` (interactive, xml_parsing)
- **Used by**: the `dsp-tools` executable (external); `commands/*` import `cli.args` back (see Boundary rules)
- **Boundary rules**:
    - A new command touches three wiring points: `create_parsers.py` (argparse), `call_action.py` (dispatch),
    and either `call_action_files_only.py` or `call_action_with_network.py` depending on whether it needs
    network/Docker access. CONVENTIONS.md names only the first of the pair — both are equally load-bearing.
    (enforcement: review)
    - `commands/*` importing `cli.args` back is an inverted dependency (the callee layer reaching into the
    caller layer for shared types); tolerated today, not to be extended. (enforcement: docs-only)
- **Durable state**: none — validates paths, then delegates writes to `commands/*`.

### clients

- **Paths**: `src/dsp_tools/clients/**`
- **Purpose**: Generic HTTP clients (a `Protocol` + a `*Live` implementation per domain) for DSP-API and
  DSP-INGEST endpoints: auth, connection, project, resource, value, list, ontology, permissions, group/user,
  legal-info, mapping, migration, metadata, ingest.
- **Key entities**: `AuthenticationClient`/`AuthenticationClientLive`, `Connection`/`ConnectionLive`,
  `ResourceClient`/`ResourceClientLive`, `OntologyGetClient`/`OntologyCreateClient`, `LegalInfoClient`,
  `BulkIngestClient`, `DspIngestClientLive`
- **Public interface**: each domain's `Protocol` plus its `*Live` class, imported and instantiated directly
  by the command that needs it — no factory or registry.
- **Local-context kit**: `CLAUDE.md`, `connection_live.py`, `authentication_client_live.py`,
  `resource_client.py`, `resource_client_live.py`
- **Depends on**: `utils` (request_utils, rdf_constants), `error`, `setup`; also `ingest.py` and
  `bulk_ingest_client.py` import from `commands/xmlupload` and `commands/ingest_xmlupload` (see Boundary rules)
- **Used by**: `create`, `get`, `validate-data`, `xmlupload`, `ingest-xmlupload`, `other-commands` (mapping,
  migration)
- **Boundary rules**:
    - `clients/` is documented as generic and reusable, but `ingest.py` and `bulk_ingest_client.py` import
    model/exception types from `commands/xmlupload` and `commands/ingest_xmlupload` — an inverted, two-way
    coupling. (enforcement: docs-only; candidate for a `dune-grill` ADR)
    - A new client is added by dropping a `<domain>_client.py` (Protocol) + `<domain>_client_live.py` (Live)
    pair into `clients/`, per `CLAUDE.md`'s naming convention — no registry.
- **Durable state**: `AuthenticationClientLive._token` (bearer-token cache, single writer `_get_token()`);
  `ConnectionLive.session` (a `requests.Session`, single writer `_renew_session()`). Both are per-instance.

### create

- **Paths**: `src/dsp_tools/commands/create/**`
- **Purpose**: Reads a JSON project-definition file and creates the project (ontologies, lists, groups,
  users, permissions, legal metadata) on a DSP server. Pipeline: `parsing/` → `models/` → `serialisation/` →
  `create_on_server/`.
- **Key entities**: `create()`, `parse_and_validate_project()`, `parse_project()`, `parse_ontology()`,
  `ParsedProject`, `ParsedOntology`, `serialise_ontology_graph_for_request()`, `create_project()`,
  `create_all_classes()`, `add_all_cardinalities()`
- **Public interface**: `create.create()`, `project_validate.validate_project_only()` /
  `parse_and_validate_project()`, `lists_only.create_lists_only()` — called from
  `cli/call_action_with_network.py`.
- **Local-context kit**: `CLAUDE.md`, `docs/developers/architecture/create-command.md`, `create.py`,
  `project_validate.py`, `parsing/parse_project.py`, `create_on_server/classes.py`
- **Depends on**: `clients` (Ontology/Group/User/Permissions/List/Project/LegalInfo), `resources`
  (schema/project.json), `utils`, `error`, `setup`
- **Used by**: `validate-data` (imports `create.models.create_problems.CardinalitiesThatMayCreateAProblematicCircle`
  directly — a reach-in)
- **Boundary rules**:
    - `validate-data` imports `create`'s internal `models/create_problems.py` directly, bypassing `create.py`'s
    public interface. (enforcement: docs-only; one instance of the repo-wide pattern in Conventions)
    - A new pipeline stage means adding a `parsing/parse_*.py` function, a `models/` model, and a
    `create_on_server/*.py` module, then wiring each in by hand into `create.py`'s `_execute_create()` and
    `project_validate.py`'s `_complex_parsed_project_validation()` — no reserved-path auto-discovery.
- **Durable state**: writes only to the DSP server (project, lists, groups, users, ontologies, classes,
  properties, cardinalities, DOAPs, legal-info) — one dedicated `create_on_server/*.py` module per resource
  type, sequenced for dependencies (single writer per type). No local file writes besides reading the input.

### get

- **Paths**: `src/dsp_tools/commands/get/**`
- **Purpose**: Reads a project (ontologies, permissions) from a DSP server and writes it back out as a JSON
  project-definition file — the read-side counterpart to `create`. **No CLAUDE.md exists here** (flagged
  below as a gap).
- **Key entities**: `get_project()`, `get_default_permissions()`, `Project`, `Group`, `Ontology` (in this
  component's own `legacy_models/` subfolder)
- **Public interface**: `get.get_project()` — the only function called from outside
  (`cli/call_action_with_network.py`).
- **Local-context kit**: `get.py`, `get_permissions.py`, `get_permissions_legacy.py`,
  `legacy_models/project.py`, `models/permissions_models.py`
- **Depends on**: `clients` (Connection, Authentication, Permissions), `error`, top-level `legacy_models`
  (LangString, DateTimeStamp), `utils` (iri_util, request_utils), `cli.args`
- **Used by**: none externally; but this component's own `legacy_models/` subfolder is reached into from
  outside (see Boundary rules)
- **Boundary rules**:
    - Two confirmed reach-ins into this component's internal `legacy_models/` subfolder, bypassing `get.py`:
    top-level `legacy_models/projectContext.py` imports `Group`/`Project` directly; `utils/request_utils.py`
    imports `Context`/`OntoIri` directly. (enforcement: docs-only)
    - Tests reach past `get_project()` into private helpers (`_categorize_doaps`,
    `_parse_project_member_perms`) and import `legacy_models.project.Project` directly.
- **Durable state**: reads DSP server state; writes exactly one local JSON file at the user-given
  `outfile_path` (single writer: `get.py`'s `json.dump` call).
- **Note**: good candidate for its own `CLAUDE.md` — real internal complexity, two confirmed reach-ins, and
  tests that dip into internals. Not written here; left for a future change.

### excel2json

- **Paths**: `src/dsp_tools/commands/excel2json/**`
- **Purpose**: Converts a folder of Excel files into a JSON project-definition file, or just its
  lists/resources/properties section. Six CLI entry points: `excel2json`, `old-excel2json`, `excel2lists`,
  `old-excel2lists`, `excel2resources`, `excel2properties`.
- **Key entities**: `excel2json()`, `old_excel2json()`, `excel2lists()`, `excel2resources()`,
  `excel2properties()`, `_sort_project_dict()`, `ordered_keys`
- **Public interface**: one top-level function per file (`project.excel2json`/`old_excel2json`,
  `lists/make_lists.excel2lists`, `old_lists.old_excel2lists`, `resources.excel2resources`,
  `properties.excel2properties`).
- **Local-context kit**: `CLAUDE.md`, `project.py`, `json_header.py`, `resources.py`, `lists/make_lists.py`
- **Depends on**: `utils` (data_formats, json_parsing), `resources/schema` (properties/resources-only.json),
  `error`
- **Used by**: `mapping/parse_excel.py` (reach-in, see Boundary rules), `cli`
- **Boundary rules**:
    - `mapping/parse_excel.py` imports `excel2json.exceptions.InvalidFileFormatError` and `excel2json.utils`
    helpers directly — a cross-command import violating the "commands never import other commands" rule
    stated in `utils/CLAUDE.md` and `CONVENTIONS.md`. (enforcement: docs-only)
    - New top-level JSON field: `_sort_project_dict()` in `project.py` raises `UnreachableCodeError` on any key
    absent from its `ordered_keys` list — a new field must be added there or the run errors at runtime (the
    trap that caused `data_license` to be missed once). (enforcement: static-analysis, at runtime)
    - New section (lists/resources/properties): its own module producing a `(section_list,
    permissions_overrules, success)` tuple, wired by hand into `_create_project_json()` and `ordered_keys`.
- **Durable state**: reads `.xlsx` files from a user folder; writes one JSON project file via `json.dump`
  (single writer).

### validate-data

- **Paths**: `src/dsp_tools/commands/validate_data/**`
- **Purpose**: SHACL-validates parsed resources against the project's ontology before upload — standalone
  (`validate-data`) or called from within `xmlupload`/`ingest-xmlupload`.
- **Key entities**: `validate_data()`, `validate_parsed_resources()`, `ShaclCliValidator`,
  `CardinalitiesThatMayCreateAProblematicCircle` (reused from `create`)
- **Public interface**: `validate_data.validate_data()` (standalone CLI) and
  `validate_data.validate_parsed_resources()` (called from `xmlupload`/`ingest_xmlupload`).
- **Local-context kit**: `CLAUDE.md`, `validate_data.py`, `prepare_data/prepare_data.py`,
  `shacl_cli_validator.py`, `sparql/cardinality_shacl.py`
- **Depends on**: `clients` (Ontology/List/Metadata/LegalInfo/Authentication), `create.models.create_problems`
  (reach-in), `resources/validate_data` (SHACL shapes), `utils`, `error`, `setup`
- **Used by**: `xmlupload`, `ingest-xmlupload` (both call `validate_parsed_resources`)
- **Boundary rules**:
    - Imports `create.models.create_problems.CardinalitiesThatMayCreateAProblematicCircle` and
    `create.communicate_problems` directly from `create` — a reach-in in the opposite direction from
    `create`'s own Boundary-rules note. (enforcement: docs-only)
    - Two-way coupling with `xmlupload`: `validate_data/constants.py` and `mappers.py` import
    `xmlupload.models.rdf_models.RDFPropTypeInfo` and `make_rdf_graph/constants.py`, while `xmlupload` calls
    back into `validate_data.validate_parsed_resources()`. (enforcement: docs-only)
    - New SHACL shape/constraint: use the `add-shacl-shape` skill; `CLAUDE.md`'s "Test-data conventions"
    section is a hard requirement regardless (testdata fixtures, e2e `expected_*`/`report_*`/`extracted_*`
    pairs).
- **Durable state**: reads SHACL shape files (`resources/validate_data/*.ttl`), ontology/lists/metadata/
  legal-info fetched from the server, the local XML input; writes temporary RDF/CSV files for Docker
  communication (auto-cleaned, not durable).

### xmlupload

- **Paths**: `src/dsp_tools/commands/xmlupload/**` (excludes `ingest_xmlupload/` and `resume_xmlupload/`,
  which form their own component)
- **Purpose**: Uploads resources described in an XML file to a DSP server in one pass. Pipeline: XML →
  `ParsedResource` (XSD-validated) → `ProcessedResource` → RDF graph → API calls.
- **Key entities**: `xmlupload()`, `execute_upload()`, `UploadConfig`, `ProcessedResource`,
  `TYPE_TRANSFORMER_MAPPER`, `RDFPropTypeInfo`
- **Public interface**: `xmlupload.xmlupload()` (CLI entry), plus `execute_upload.execute_upload()` and
  `upload_config.UploadConfig`, which `ingest-xmlupload` and `resume-xmlupload` call directly (see Boundary
  rules).
- **Local-context kit**: `CLAUDE.md`, `xmlupload.py`, `execute_upload.py`,
  `prepare_xml_input/prepare_xml_input.py`, `make_rdf_graph/make_values.py`, `models/processed/values.py`
- **Depends on**: `clients`, `utils`, `error`, `setup`, top-level `legacy_models`, `validate-data`
  (`validate_parsed_resources`)
- **Used by**: `ingest-xmlupload` and `resume-xmlupload` (heavy reach-in, see Boundary rules); `validate-data`
  (two-way, see that entry)
- **Boundary rules**:
    - `resume_xmlupload` and `ingest_xmlupload` bypass the `xmlupload()` entry point entirely and call
    `execute_upload()` and internal `models/`/`prepare_xml_input/` modules directly — the two components are
    really one tightly-coupled upload pipeline split across two CLI surfaces. (enforcement: docs-only; strong
    candidate for a `dune-grill` ADR — either merge the map entries or promote `execute_upload()`/
    `upload_config.py` to a documented shared interface)
    - New value/property type: add a `KnoraValueType` entry to `TYPE_TRANSFORMER_MAPPER`
    (`prepare_xml_input/get_processed_resources.py`) plus a new `Processed*` dataclass
    (`models/processed/values.py`) and an `RDFPropTypeInfo` (`make_rdf_graph/constants.py`).
- **Durable state**: reads the XML input file; writes resources to the DSP server; writes a resumable-state
  pickle at `~/.dsp-tools/xmluploads/<server>/resumable/latest.pkl` (single writer: `execute_upload`, read by
  `resume_xmlupload`); writes an ID→IRI diagnostic JSON and a warnings log on error.

### ingest-xmlupload

- **Paths**: `src/dsp_tools/commands/ingest_xmlupload/**`, `src/dsp_tools/commands/resume_xmlupload/**`
- **Purpose**: The split, resumable upload workflow: `upload-files` → `ingest-files` → `ingest-xmlupload`,
  with `resume-xmlupload` able to resume either an interrupted `xmlupload` or `ingest-xmlupload`.
- **Key entities**: `upload_files()`, `ingest_files()`, `ingest_xmlupload()`, `resume_xmlupload()`
- **Public interface**: one function per CLI subcommand (`upload_files.upload_files`,
  `ingest_files.ingest_files`, `create_resources.upload_xml.ingest_xmlupload`,
  `resume_xmlupload.resume_xmlupload.resume_xmlupload`).
- **Local-context kit**: `upload_files/CLAUDE.md`, `upload_files/upload_files.py`,
  `ingest_files/ingest_files.py`, `create_resources/upload_xml.py`, `resume_xmlupload/resume_xmlupload.py`
- **Depends on**: `clients` (BulkIngestClient, DspIngestClientLive), `xmlupload` (execute_upload, models,
  prepare_xml_input, upload_config — heavy reuse), `validate-data`, `utils`, `error`
- **Used by**: none externally
- **Boundary rules**:
    - `clients/bulk_ingest_client.py` imports exception types from this component's `exceptions.py` and
    `upload_files/upload_failures.py` — an inversion mirroring the one noted under `clients`.
    (enforcement: docs-only)
    - New ingest step: add a module under the relevant subpackage exposing one public function, wire it into
    `cli/create_parsers.py` + `cli/call_action_with_network.py`, and reuse `commands/xmlupload`'s
    `UploadState`/`UploadClients`/`execute_upload` rather than duplicating upload logic.
- **Durable state**: writes uploaded bitstreams to the dsp-ingest server; writes/reads
  `mapping-<shortcode>.csv` in the working directory (rotated on rewrite); reads the resumable pickle that
  `commands/xmlupload`'s `execute_upload` wrote; writes optional failure-report CSVs past a threshold.

### other-commands

- **Paths**: `src/dsp_tools/commands/id2iri.py`, `update_legal/**`, `mapping/**`, `start_stack/**`,
  `migration/**`, `excel2xml/**`
- **Purpose**: Six small, largely independent commands bundled into one entry: `id2iri` (ID→IRI replacement
  in XML), `update-legal` (migrates legal metadata to bitstream attributes), `mapping config`/`update`
  (replaces an ontology's external mappings from Excel), `start-stack`/`stop-stack` (local DSP stack via
  Docker), `migration` (all-in-one export/import), and `excel2xml` (deprecated library, superseded by
  `xmllib`).
- **Key entities**: `id2iri()`, `update_legal_metadata()`, `mapping_update()`, `StackHandler`, `migration()`
- **Public interface**: one function/class per command; `excel2xml` additionally exposes ~30 `make_*_prop`
  helpers as a library surface (no CLI subcommand of its own).
- **Local-context kit**: `update_legal/CLAUDE.md`, `docs/developers/architecture/migration-command.md`, plus
  one main module per command — treated as six small kits rather than one shared budget, since the six share
  no code with each other.
- **Depends on**: `utils`, `error`, `xmllib` (update_legal, excel2xml), `clients` (mapping, migration,
  start_stack), Docker/subprocess (start_stack)
- **Used by**: `src/dsp_tools/__init__.py` imports `excel2xml` unconditionally at package init;
  `utils/data_formats/shared.py` imports `excel2xml.propertyelement.PropertyElement` (reach-in)
- **Boundary rules**:
    - `mapping/parse_excel.py` imports from `excel2json` (see that entry) — the one cross-import among these
    six.
    - `utils/data_formats/shared.py` importing `commands.excel2xml.propertyelement.PropertyElement` is an
    inverted reach-in (utils depending on a command). (enforcement: docs-only)
    - Not a reserved "small command" slot: a new small command is wired exactly like any other command
    (`create_parsers.py` + `call_action.py` + `call_action_files_only.py`/`call_action_with_network.py`).
    `excel2xml` is the one exception, with no CLI wiring at all (deprecated, library-only).
- **Durable state**: `update_legal` (reads/writes CSV + XML files), `mapping` (reads Excel, writes ontology
  mappings to the server), `start_stack` (reads/writes docker-compose files, manages containers), `migration`
  (zip export/import), `id2iri` (reads XML + JSON mapping file, writes XML), `excel2xml` (none — pure
  library).

### xmllib

- **Paths**: `src/dsp_tools/xmllib/**`
- **Purpose**: Public API library for programmatic XML-data-file creation, meant for user scripts and the
  external `0854-daschland-scripts` repo, independent of the rest of dsp-tools.
- **Key entities**: `Resource`, `XMLRoot`, `AudioSegmentResource`, `LinkResource`, `RegionResource`,
  `VideoSegmentResource`, `LicenseRecommended`/`LicenseOther`, value checkers/converters
- **Public interface**: everything explicitly re-exported (`as`-aliased) in `xmllib/__init__.py` — general
  helpers, config/enum types, resource models, license classes, value checkers/converters.
- **Local-context kit**: `CLAUDE.md`, `__init__.py`, `models/root.py`, `internal/serialise_resource.py`,
  `general_functions.py`
- **Depends on**: `lxml`, `pandas`, `regex`, `loguru` (true-external); `dsp_tools.error`, `dsp_tools.setup`,
  `dsp_tools.utils` (in-process — see Boundary rules)
- **Used by**: `other-commands` (excel2xml, update_legal), `setup/warnings_config.py` (reach-in), external
  user scripts, the `0854-daschland-scripts` repo
- **Boundary rules**:
    - **Stated rule violated**: `CLAUDE.md` and the root `CLAUDE.md` both say "xmllib must not import
    dsp-tools internals," but 8 files import from `dsp_tools.error`, `dsp_tools.setup`, or `dsp_tools.utils`
    (e.g. `xmllib/internal/exceptions.py`, `xmllib/models/root.py`, `xmllib/internal/serialise_resource.py`).
    (enforcement: docs-only today; strong candidate for a `dune-grill` ADR — either fix the imports or
    update the stated rule to match reality)
    - `setup/warnings_config.py`, `commands/excel2xml/excel2xml_lib.py`, and `commands/update_legal/*` all
    import from `xmllib.internal`/`xmllib.general_functions` directly, bypassing `__init__.py`.
    - New helper: add to `general_functions.py`/`value_checkers.py`/`value_converters.py` or a new `models/`
    class, then explicitly re-export it via `from .module import X as X` in `__init__.py`.
- **Durable state**: none — stateless library, serialises in-memory objects to XML files on demand.

### utils

- **Paths**: `src/dsp_tools/utils/**`
- **Purpose**: Shared, stateless helpers used by every command: HTTP (`request_utils.py`), XML parsing
  (`xml_parsing/`), data-format checks (`data_formats/`), JSON parsing, interactive prompts, RDF constants.
- **Key entities**: `request_utils` (retry/backoff HTTP), `parse_clean_validate_xml`, `get_parsed_resources`,
  `replace_id_with_iri`, `rdf_constants`
- **Public interface**: every file is directly importable; there is no `__init__.py` gate.
- **Local-context kit**: `CLAUDE.md`, `request_utils.py`, `xml_parsing/parse_clean_validate_xml.py`,
  `data_formats/shared.py`
- **Depends on**: `error`, `setup`, `clients.fuseki_metrics`, top-level `legacy_models` (correctly
  directioned); `commands/get`, `commands/excel2xml`, `commands/xmlupload`, `commands/validate_data` (see
  Boundary rules — incorrectly directioned)
- **Used by**: every component in this map (`cli`, `clients`, every command, `xmllib`)
- **Boundary rules**:
    - **`utils` importing from `commands/` is a structural inversion** — 5 files, 9 import sites:
    `request_utils.py` (`commands.get.legacy_models`), `data_formats/shared.py`
    (`commands.excel2xml.propertyelement`), `replace_id_with_iri.py` (`commands.xmlupload.iri_resolver`,
    `richtext_id2iri`), `xml_parsing/get_lookups.py` (`commands.xmlupload.models.permission`,
    `permissions_parsed`), `xml_parsing/get_parsed_resources.py` (`commands.validate_data.mappers`). Since
    every command also imports `utils`, this is a real circular-dependency risk today, only avoided because
    Python resolves imports lazily. (enforcement: docs-only; the single highest-value finding in this map for
    a `dune-grill` ADR — move these types into `utils/` itself or a neutral shared module)
    - One instance of a repo-wide pattern — see the banned-constructs table in Conventions.
    - New shared helper: drop a file into `utils/` or a subpackage; no registration needed.
- **Durable state**: none — `request_utils.py`'s retry/backoff settings and `fuseki_bloating.py`'s thresholds
  are static, not runtime-mutable.

### resources

- **Paths**: `src/dsp_tools/resources/**`
- **Purpose**: Static, non-Python assets: the project-definition JSON Schema family, SHACL shapes for
  validate-data, and start-stack's Docker Compose/config templates. No code of its own.
- **Key entities**: `project.json`, `properties-only.json`, `resources-only.json`, `lists-only.json`,
  `api-shapes.ttl`, `docker-compose.yml`
- **Public interface**: the files themselves are the contract (JSON Schema, SHACL shapes, Compose/template
  files).
- **Local-context kit**: `schema/project.json`, `validate_data/api-shapes.ttl`, `start-stack/docker-compose.yml`
- **Depends on**: none
- **Used by**: `create`, `excel2json` (schema family); `validate-data` (SHACL shapes); `xmlupload`/`create`
  (`data.xsd`, via `utils/xml_parsing`); `start_stack` (Compose/template files)
- **Boundary rules**:
    - Read-only at runtime; the single writer is a human editing the file directly via PR. `start_stack.py`
    only writes *copies* into the user's `~/.dsp-tools/start-stack`, never back into this tree.
    (enforcement: review)
    - Always loaded via `importlib.resources` (never a relative `open()` path), required for correct behavior
    when installed from a wheel — enforced by `test/distribution/test_cli_deps_resources.py`.
    (enforcement: static-analysis)
    - New schema/shape/template: add the file under the matching subfolder and wire it into the consuming
    module by hand (`start_stack`'s directory copy-loop picks up new plain files automatically; `.j2`
    templates need explicit render logic).
- **Durable state**: these files ARE the durable state; no runtime writer.

### docs

- **Paths**: `docs/**`, `mkdocs.yml`
- **Purpose**: The mkdocs-served, user-facing documentation site — distinct from the agent-facing
  `CLAUDE.md`/`CONVENTIONS.md`/`REVIEW.md` at the repo root, which this component does not include.
- **Key entities**: mkdocs nav sections — Overview, User Guides, Running a Local Stack, Data Modelling, Data
  for Mass-Upload, Advanced Workflows, Information for developers, Changelog
- **Public interface**: the rendered site's nav tree, defined in `mkdocs.yml`.
- **Local-context kit**: `mkdocs.yml`, `docs/developers/architecture/error-handling.md`,
  `docs/data-model/json-project/`, `docs/xmllib-docs/`
- **Depends on**: `xmllib` (mkdocstrings pulls its docstrings for the API reference)
- **Used by**: developers and agents reading it; whether/where to update it on a given change is gated by the
  `update-docs` skill
- **Boundary rules**:
    - A new page must be added to `mkdocs.yml`'s `nav:` tree by hand — `validation.omitted_files` only warns,
    it doesn't fail, so an unregistered page silently never appears on the site. (enforcement: docs-only)
    - Internal links and nav completeness are enforced by `mkdocs build --strict` (the required `check-docs`
    CI check); external links are checked weekly, non-blocking, via `lychee.toml`.
- **Durable state**: none in this repo — the combined site is published from the separate
  `dasch-swiss/dsp-docs` repo, which dsp-tools' release workflow notifies on release.

### tests

- **Paths**: `test/**`, `testdata/**`
- **Purpose**: The four-tier test suite (unittests, integration, e2e via testcontainers, legacy_e2e against
  a running stack) and its fixture data.
- **Key entities**: `pytest_sessionstart` (`test/conftest.py`), `USED_SHORTCODE_SHORTNAMES.md`,
  `systematic-project-4123.json`/`test-data-systematic-4123.xml`
- **Public interface**: none — this component consumes the rest of the map.
- **Local-context kit**: `test/conftest.py`, CONVENTIONS.md's Testing Conventions section,
  `testdata/USED_SHORTCODE_SHORTNAMES.md`
- **Depends on**: every component in this map (it's what's under test), plus pytest/pytest-xdist/
  testcontainers (true-external)
- **Used by**: CI (`just` recipes), developers
- **Boundary rules**:
    - Reaching into a module's private (`_`-prefixed) names is the accepted norm in unit tests (~30% of test
    files do it) and occurs occasionally in integration tests; e2e and legacy_e2e stay black-box (CLI-level)
    by convention. (enforcement: review)
    - E2E three-place wiring: a test dir under `test/e2e/commands/<command>/`, a `just e2e-test-<command>`
    recipe, and a matching job in `.github/workflows/tests-e2e.yml` — a test not registered in all three
    silently never runs in CI. (enforcement: docs-only; verified consistent for xmlupload)
- **Durable state**: `testdata/USED_SHORTCODE_SHORTNAMES.md` is a human-maintained register (single writer:
  whoever adds a shortcode, reviewed via PR diff); `test/e2e`'s testcontainers spin up ephemeral Docker
  state, discarded after the run.

### repo-tooling

- **Paths**: `pyproject.toml`, `justfile`, `uv.lock`, `.github/**`, `scripts/**`, `k6/**`,
  `.pre-commit-config.yaml`, `.editorconfig`, `.gitignore`, `.markdownlint.yml`, `.yamllint.yml`,
  `.yamlfmt.yml`, `.kodus-readiness.yml`, `codecov.yml`, `lychee.toml`, `CHANGELOG.md`, `LICENSE`,
  `README.md`, `.vulture_whitelist.py`, `CLAUDE.md`, `CONVENTIONS.md`, `REVIEW.md`, `ARCH-MAP.md`,
  `src/dsp_tools/__init__.py`, `src/dsp_tools/py.typed`, `src/dsp_tools/commands/__init__.py`, `.claude/**`
- **Purpose**: Repo-level build, lint, and CI tooling — everything a developer or CI runs that isn't
  application code, docs, or tests.
- **Key entities**: `just` recipes (lint, mypy, vulture, unittests, integration-tests, e2e-tests,
  legacy-e2e-tests), release-please, `bump_version.py`
- **Public interface**: the justfile's recipe names, and any `.github/workflows/*.yml` (auto-discovered by
  GitHub Actions).
- **Local-context kit**: `justfile`, `pyproject.toml`, `README.md` (dev-onboarding lives here; no
  CONTRIBUTING.md exists)
- **Depends on**: ruff, mypy, pytest, vulture, markdownlint-cli, yamllint, pre-commit, release-please
  (true-external); `scripts/validate_xmllib_docstring_links.py` imports `dsp_tools.setup.ansi_colors` (the
  one in-process dependency)
- **Used by**: CI, developers running `just <recipe>`, pre-commit git hooks
- **Boundary rules**:
    - `.github/workflows/*.yml` is reserved-path/auto-discovered by GitHub Actions; the justfile is one flat
    file with no such convention — a new recipe added to `lint`'s parallel dispatcher must be wired in by
    hand to run under `just lint`. (enforcement: structure for workflows, docs-only for the justfile)
    - `k6/` is fully standalone (its own justfile), not referenced from the root justfile or any CI workflow.
- **Durable state**: `CHANGELOG.md` and `pyproject.toml`'s version field are written by the release-please
  GitHub Action, not by hand; `uv.lock` has a single writer path (`uv sync`/`uv add`).

## Cross-cutting concerns

### error/ (`src/dsp_tools/error/**`)

Two-branch exception hierarchy: `BaseError` → `UserError` (user can fix it) / `InternalError` (needs a
developer; auto-appends contact info and the log path). `custom_warnings.py` mirrors this for warnings;
`problems.py` defines the `Problem` protocol used by Group B's aggregated-error pattern. Per
`docs/developers/architecture/error-handling.md`: catch only recoverable external failures and let your own
bugs crash; Group A commands (`create`, `xmlupload`, `get`, …) fail fast, Group B commands (`excel2json`,
`validate-data`, `xmllib`, …) collect every `Problem` into one aggregated `UserError`. Ten command modules
define their own `exceptions.py` subclassing from here. Imported by 86 files repo-wide. No durable state.

### setup/ (`src/dsp_tools/setup/**`)

Process-startup wiring, not a component with request-level dependents: `logger_config()` (loguru sinks) and
`initialize_warnings()` (routes `DspToolsWarning` through custom formatting) are each called once, in
`cli/entry_point.py` (and once per session in `test/conftest.py`'s `pytest_sessionstart`). `dotenv.py` loads
a local `.env`; `ansi_colors.py` is terminal color constants. Imported by 36 files. Durable state is the
one-shot loguru sink registry, written once at process start.

### legacy_models/ (`src/dsp_tools/legacy_models/**` — top-level; distinct from `commands/get/legacy_models/`)

Three shared, effectively-immutable value types: `LangString` (language-tagged string), `DateTimeStamp`
(validated `xsd:dateTimeStamp`), `ProjectContext` (a one-shot snapshot of a project's shortcode/group/user
lookups, built once from server data). Imported by `get`, `excel2xml`, `validate-data`, `xmlupload`, and
`utils`. Still raises `BaseError` directly rather than `UserError`/`InternalError` — a known legacy exemption
per the error-handling doc. No durable state beyond each instance's own value.

## Conventions

- **Module granularity budget**: local-context kit ≤7 files per component (no component in this repo needed
  more).
- **One-way top-level dependency direction** (as designed; violated today in several places — see below):
  `cli` → `commands/*` → `utils`/`clients`/`xmllib`/`resources` → `error`/`setup`/`legacy_models`. Nothing
  below a layer should import from above it.
- **Commands never import from other commands** (stated in `utils/CLAUDE.md` and `CONVENTIONS.md`;
  enforcement: docs-only; currently violated): `mapping`→`excel2json`, `validate-data`↔`create`,
  `validate-data`↔`xmlupload`, `ingest-xmlupload`/`resume-xmlupload`→`xmlupload`. Shared logic belongs in
  `utils/` instead.
- **Wiring convention**: a new CLI command touches three files — `cli/create_parsers.py`,
  `cli/call_action.py`, and either `cli/call_action_files_only.py` or `cli/call_action_with_network.py`
  depending on whether it needs network/Docker access.
- **Colocated-doc expectation**: most command directories carry a `CLAUDE.md`; `commands/get/` is the one
  confirmed gap.
- **Banned constructs**:

| Pattern | Why it couples globally | Alternative | Enforcement |
| --- | --- | --- | --- |
| A command imports directly from another command's package | Spreads blast radius silently; contradicts the stated rule | Move the shared logic into `utils/` or a new neutral module | docs-only (violated: `mapping`→`excel2json`, `validate-data`↔`create`, `validate-data`↔`xmlupload`, `ingest-xmlupload`/`resume-xmlupload`→`xmlupload`) |
| `utils/` importing from `commands/` | Inverts `utils`' leaf-dependency role; real circular-import risk since every command also imports `utils` | Move the shared type/constant into `utils/` itself | docs-only (violated: 5 files / 9 import sites — see the `utils` entry) |
| `clients/` importing from `commands/` | `clients/` is documented as generic/reusable; a command-specific import defeats that and risks circular imports | Define the shared type in `clients/` or `utils/` instead | docs-only (violated: `clients/ingest.py`, `clients/bulk_ingest_client.py`) |
| `xmllib` importing `dsp_tools.error`/`setup`/`utils` | `xmllib`'s own `CLAUDE.md` and the root `CLAUDE.md` both require it to stay free of dsp-tools internals, so it works as a standalone library | Vendor the helper into `xmllib/internal/`, or update the stated rule to match reality | docs-only (violated: 8 files) |
