---
dune_map: true
schema_version: 2
date: 2026-11-04
---

# ARCH-MAP.md

## Overview

DSP-TOOLS is a CLI (`dsp-tools`) that creates a DSP project's data model on a server and bulk-imports
data into it, plus a standalone `xmllib` library for programmatic XML-data-file authoring. `cli/` parses
arguments and dispatches each subcommand to its own module under `commands/`; commands share HTTP clients
(`clients/`), stateless helpers (`utils/`), static schema/shape assets (`resources/`), and a common
exception hierarchy (`error/`). The two largest workflows are `create`/`get` (JSON project file ↔ server)
and `xmlupload`/`ingest-xmlupload` (XML data file → server, either in one pass or via a resumable,
ingest-first pipeline). See `CONTEXT.md` for vocabulary. Several CLAUDE.md files state that
commands must not import each other and that `utils`/`clients`/`xmllib` must not import from `commands` —
this map found confirmed violations of both rules; see Conventions and each component's Boundary rules.

## Components

### cli

- **Paths**: `src/dsp_tools/cli/**`
- **Purpose**: Parses CLI arguments and dispatches each subcommand to its `commands/` implementation. Sole
  console-script entry point (`dsp-tools`).
- **Key entities**: `main`, `run`, `make_parser`, `call_requested_action`, `check_input_dependencies`,
  `ServerCredentials`; handler modules `call_action_files_only` and `call_action_with_network`
- **Public interface**: `entry_point.main()`/`run()`; the `cli.args` types `ServerCredentials`,
  `ValidationSeverity`, `ValidateDataConfig`, imported directly by 14 files under `commands/*`;
  `cli.utils.get_canonical_server_and_dsp_ingest_url`, imported by `commands/mapping/config_file.py`.
  `PathDependencies`, `ProhibitedPaths` and `NetworkRequirements` are used only inside `cli`.
- **Local-context kit**: `entry_point.py`, `create_parsers.py`, `call_action.py`,
  `call_action_files_only.py`, `call_action_with_network.py`, `args.py`, `CLAUDE.md`
- **Depends on**: every `commands/*` component except `excel2xml` (which has no CLI wiring), `error`,
  `setup` (ansi_colors, logger_config, warnings_config), `utils` (interactive, xml_parsing); true-external:
  the PyPI JSON API (version check), the DSP-API/ingest health endpoints, `docker`/`pip` subprocesses
- **Used by**: the `dsp-tools` executable (external); `commands/*` import `cli.args` back, and
  `mapping/config_file.py` imports `cli.utils` (see Boundary rules)
- **Boundary rules**:
    - A new command touches three wiring points: `create_parsers.py` (argparse), `call_action.py` (dispatch),
    and either `call_action_files_only.py` or `call_action_with_network.py` depending on whether it needs
    network/Docker access. CONVENTIONS.md names only the first of the pair — both are equally load-bearing.
    (enforcement: review)
    - `commands/*` importing `cli.args` (14 files) and `mapping/config_file.py` importing `cli.utils` is an
    inverted dependency (the callee layer reaching into the caller layer); tolerated today, not to be
    extended. (enforcement: docs-only; an import-linter contract could make it static-analysis)
- **Durable state**: none — validates paths, then delegates writes to `commands/*`.
- **Fingerprint**: `e36e518124ba`

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
- **Used by**: `create`, `get`, `validate-data`, `xmlupload`, `ingest-xmlupload` (incl. resume),
  `other-commands` (mapping, migration), `legacy_models` (`projectContext.py` imports `Connection`)
- **Boundary rules**:
    - `clients/` is documented as generic and reusable (root `CLAUDE.md`), but `ingest.py` imports from
    `commands/xmlupload` and `bulk_ingest_client.py` imports from `commands/ingest_xmlupload` — an inverted
    coupling. It is already a module cycle: `commands/xmlupload/exceptions.py` imports
    `clients.exceptions`, while `clients/ingest.py` imports `commands.xmlupload.exceptions`.
    (enforcement: docs-only; candidate for a `dune-grill` ADR)
    - A new client is added by dropping a `<domain>_client.py` (Protocol) + `<domain>_client_live.py` (Live)
    pair into `clients/`, per `clients/CLAUDE.md`'s naming convention — no registry. Older files
    (`ingest.py`, `bulk_ingest_client.py`, `group_user_clients.py`, `migration_clients.py`,
    `ontology_clients.py`) do not follow the pattern. (enforcement: docs-only)
    - DSP-INGEST answers 401 (not 403) for missing write access, so the ingest clients map both 401 and 403
    to `BadCredentialsError`; every other client handles 401 only in the authentication client.
    (enforcement: docs-only, `clients/CLAUDE.md`)
- **Durable state**: `AuthenticationClientLive._token` (bearer-token cache, single writer `_get_token()`,
  per-instance). `ConnectionLive.session` is a class-level default `Session()` that all instances share
  until `_renew_session()` replaces it per instance; `__post_init__` and `_renew_session()` both write its
  headers — two writers on a shared mutable default.
- **Fingerprint**: `f42ddda0a45e`

### create

- **Paths**: `src/dsp_tools/commands/create/**`
- **Purpose**: Reads a JSON project-definition file and creates the project (ontologies, lists, groups,
  users, permissions, legal metadata) on a DSP server. Pipeline: `parsing/` → `models/` → `serialisation/` →
  `create_on_server/`. After parsing, `admin_account_check.py` checks that the file defines
  `<shortname>@admin.dasch.swiss` with project-admin rights: it raises on prod-like servers and warns
  elsewhere.
- **Key entities**: `create()`, `parse_and_validate_project()`, `parse_project()`, `parse_ontology()`,
  `ParsedProject`, `ParsedOntology`, `serialise_ontology_graph_for_request()`, `create_project()`,
  `create_all_classes()`, `add_all_cardinalities()`, `check_dsp_admin_account_exists()`
- **Public interface**: `create.create()`, `project_validate.validate_project_only()`,
  `lists_only.create_lists_only()` — called from `cli/call_action_with_network.py`.
- **Local-context kit**: `CLAUDE.md`, `docs/developers/architecture/create-command.md`, `create.py`,
  `project_validate.py`, `parsing/parse_project.py`, `create_on_server/classes.py`, `admin_account_check.py`
- **Depends on**: `clients` (Authentication/Ontology/Group/User/Permissions/List/Project/LegalInfo),
  `resources` (schema/project.json), `utils` (incl. `dsp_user_account_check`, `data_formats.uri_util`),
  `error`, `setup`, `cli` (`cli.args.ServerCredentials` — inverted, see the `cli` entry)
- **Used by**: `cli` (the three public functions); `validate-data` (reaches into
  `create.models.create_problems` and `create.communicate_problems` — see Boundary rules)
- **Boundary rules**:
    - `validate-data` imports `create`'s internal `models/create_problems.py` (4 files) and
    `communicate_problems.py` directly, bypassing `create.py`'s public interface. (enforcement: docs-only;
    one instance of the repo-wide pattern in Conventions)
    - A new pipeline stage means adding a `parsing/parse_*.py` function, a `models/` model, and a
    `create_on_server/*.py` module, then wiring each in by hand into `create.py`'s `_execute_create()` and
    `project_validate.py`'s `_complex_parsed_project_validation()` — no reserved-path auto-discovery.
    (enforcement: review)
    - Every entry point that consumes a `ParsedProject` calls `check_dsp_admin_account_exists()` itself
    (today `create()` and `validate_project_only()`; `--lists-only` parses no users and skips it). The check
    stays outside `parse_and_validate_project()` because it depends on the server and fails fast instead of
    collecting problems. (enforcement: docs-only, `create/CLAUDE.md`; tests cover the function, not the
    wiring)
- **Durable state**: writes only to the DSP server (project, lists, groups, users, ontologies, classes,
  properties, cardinalities, DOAPs, legal-info) — one dedicated `create_on_server/*.py` module per resource
  type, sequenced for dependencies (single writer per type). No local file writes besides reading the input.
- **Fingerprint**: `4cf510d775f9`

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
  (LangString, DateTimeStamp), `utils` (iri_util, request_utils), `cli` (`cli.args` — inverted, see the
  `cli` entry)
- **Used by**: `cli` (calls `get.get_project()`); `utils/request_utils.py` and top-level
  `legacy_models/projectContext.py` reach into this component's `legacy_models/` subfolder (see Boundary
  rules); test-only: `test/unittests/commands/create/test_admin_account_check.py` imports
  `get.legacy_models.user.User`
- **Boundary rules**:
    - Two confirmed reach-ins into this component's internal `legacy_models/` subfolder, bypassing `get.py`:
    top-level `legacy_models/projectContext.py` imports `Group`/`Project` directly; `utils/request_utils.py`
    imports `Context`/`OntoIri` directly. (enforcement: docs-only)
    - Tests reach past `get_project()` into private helpers (`_categorize_doaps`,
    `_parse_project_member_perms`) and import `legacy_models.project.Project` directly. (enforcement: review)
    - The `users` section that `get` writes is read back by `create`'s `_parse_one_user`
    (`legacy_models/user.py` says so), and `create`'s tests check that `get`'s output passes the
    admin-account check. This is a get→create file-format contract, not an import. (enforcement: docs-only)
- **Durable state**: reads DSP server state; writes exactly one local JSON file at the user-given
  `outfile_path` (single writer: `get.py`'s `json.dump` call).
- **Note**: good candidate for its own `CLAUDE.md` — real internal complexity, two confirmed reach-ins, and
  tests that dip into internals. Not written here; left for a future change.
- **Fingerprint**: `d84e178b78bc`

### excel2json

- **Paths**: `src/dsp_tools/commands/excel2json/**`
- **Purpose**: Converts a folder of Excel files into a JSON project-definition file, or just its
  lists/resources/properties section. Six CLI entry points: `excel2json`, `old-excel2json`, `excel2lists`,
  `old-excel2lists`, `excel2resources`, `excel2properties`.
- **Key entities**: `excel2json()`, `old_excel2json()`, `excel2lists()`, `excel2resources()`,
  `excel2properties()`, `_sort_project_dict()`, `ordered_keys`
- **Public interface**: one top-level function per file (`project.excel2json`/`old_excel2json`,
  `lists/make_lists.excel2lists`, `old_lists.old_excel2lists`, `resources.excel2resources`,
  `properties.excel2properties`), plus `old_lists.validate_lists_section_from_project`, which `cli` calls for
  `create --lists-only --validate-only`.
- **Local-context kit**: `CLAUDE.md`, `project.py`, `json_header.py`, `resources.py`, `lists/make_lists.py`
- **Depends on**: `utils` (data_formats, json_parsing), `resources/schema` (properties-only.json,
  resources-only.json, lists-only.json), `error`. No `cli` and no other command.
- **Used by**: `mapping/parse_excel.py` (reach-in, see Boundary rules), `cli`
- **Boundary rules**:
    - `mapping/parse_excel.py` imports `excel2json.exceptions.InvalidFileFormatError` and `excel2json.utils`
    helpers directly — a cross-command import violating the "commands never import other commands" rule
    stated in `utils/CLAUDE.md` and `CONVENTIONS.md`. (enforcement: docs-only)
    - New top-level JSON field: `_sort_project_dict()` in `project.py` raises `UnreachableCodeError` on any key
    absent from its `ordered_keys` list — a new field must be added there or the run errors at runtime (the
    trap that caused `data_license` to be missed once). Nothing lints or tests `ordered_keys` against the
    schema today, so this only catches a miss when the code path actually runs. (enforcement: review)
    - New section: its own module returning `(section, success)`, or `(section, overrules, success)` if it
    carries permission overrules (as resources and properties do). It is wired by hand into
    `_create_project_json()` and `_old_create_project_json()`, and its key goes into `ordered_keys`.
    (enforcement: review)
- **Durable state**: reads `.xlsx` files from a user folder; each CLI entry point writes its own JSON output
  file at the path the user gives (one writer per output file, no shared state).
- **Fingerprint**: `373241579908`

### validate-data

- **Paths**: `src/dsp_tools/commands/validate_data/**`
- **Purpose**: SHACL-validates parsed resources against the project's ontology before upload — standalone
  (`validate-data`) or called from within `xmlupload`/`ingest-xmlupload`.
- **Key entities**: `validate_data()`, `validate_parsed_resources()`, `ShaclCliValidator`,
  `ShaclValidationOutOfMemoryError`, `CardinalitiesThatMayCreateAProblematicCircle` (reused from `create`)
- **Public interface**: `validate_data.validate_data()` (standalone CLI) and
  `validate_data.validate_parsed_resources()` (called from `xmlupload`/`ingest_xmlupload`).
- **Local-context kit**: `CLAUDE.md`, `validate_data.py`, `prepare_data/prepare_data.py`,
  `shacl_cli_validator.py`, `sparql/cardinality_shacl.py`
- **Depends on**: `clients` (Ontology/List/Metadata/LegalInfo/Authentication/Project), `create`
  (`models.create_problems`, `communicate_problems` — reach-in), `xmlupload` (`models.rdf_models`,
  `make_rdf_graph.constants` — reach-in), `cli` (`cli.args` — inverted), `resources/validate_data` (SHACL
  shapes, `shacl-cli-image.yml`), `utils`, `error`, `setup`, top-level `legacy_models`
- **Used by**: `cli` (calls `validate_data.validate_data()`); `xmlupload`, `ingest-xmlupload` (both call
  `validate_parsed_resources`); `utils/xml_parsing/get_parsed_resources.py` reaches into `mappers.py` (see
  Boundary rules)
- **Boundary rules**:
    - Imports `create.models.create_problems.CardinalitiesThatMayCreateAProblematicCircle` and
    `create.communicate_problems` directly from `create` — a reach-in in the opposite direction from
    `create`'s own Boundary-rules note. (enforcement: docs-only)
    - Two-way coupling with `xmlupload`: `validate_data/constants.py` and `mappers.py` import
    `xmlupload.models.rdf_models.RDFPropTypeInfo` and `make_rdf_graph/constants.py`, while `xmlupload` calls
    back into `validate_data.validate_parsed_resources()`. (enforcement: docs-only)
    - `utils/xml_parsing/get_parsed_resources.py` reaches into `mappers.py` (`XML_TAG_TO_VALUE_TYPE_MAPPER`,
    `PLACEHOLDER_TYPE_TO_FILE_TYPE_MAPPER`), so the shared XML parser depends on a command's internals: a
    new XML value tag added in `mappers.py` changes parsing for every command. (enforcement: docs-only)
    - New SHACL shape/constraint: use the `add-shacl-shape` skill; `CLAUDE.md`'s "Test-data conventions"
    section is a hard requirement regardless (testdata fixtures, e2e `expected_*`/`report_*`/`extracted_*`
    pairs). (enforcement: review)
- **Durable state**: reads SHACL shape files (`resources/validate_data/*.ttl`) and
  `resources/validate_data/shacl-cli-image.yml`, ontology/lists/metadata/legal-info fetched from the
  server, and the local XML input; writes temporary RDF files for Docker communication (auto-cleaned).
  Writes user-visible output next to the XML file, one writer each: `<stem>_validation_<severity>.csv`
  when there are many problems, `<timestamp>_validation_result.ttl`/`_shacl.ttl`/`_data.ttl` on unexpected
  results, and a `graphs/` directory when `save_graphs` is set.
- **Fingerprint**: `5e199e99fd57`

### xmlupload

- **Paths**: `src/dsp_tools/commands/xmlupload/**`
- **Purpose**: Uploads resources described in an XML file to a DSP server in one pass. Pipeline: XML →
  `ParsedResource` (XSD-validated) → `ProcessedResource` → RDF graph → API calls.
- **Key entities**: `xmlupload()`, `execute_upload()`, `UploadConfig`, `ProcessedResource`,
  `TYPE_TRANSFORMER_MAPPER`, `RDFPropTypeInfo`
- **Public interface**: `xmlupload.xmlupload()` (CLI entry), plus `execute_upload.execute_upload()` and
  `upload_config.UploadConfig`, which `ingest-xmlupload` and `resume-xmlupload` call directly (see Boundary
  rules).
- **Local-context kit**: `CLAUDE.md`, `xmlupload.py`, `execute_upload.py`, `upload_config.py`,
  `prepare_xml_input/prepare_xml_input.py`, `make_rdf_graph/make_values.py`, `models/processed/values.py`
- **Depends on**: `clients`, `utils` (incl. `dsp_user_account_check`, `data_formats.geolocation_util`),
  `error`, `setup`, top-level `legacy_models`, `validate-data` (`validate_parsed_resources`), `cli`
  (`cli.args` — inverted, see the `cli` entry)
- **Used by**: `cli` (calls `xmlupload.xmlupload()`); `clients` (`ingest.py` imports from this component — a
  reach-in, see `clients`' Boundary rules); `utils` (`replace_id_with_iri.py`, `xml_parsing/get_lookups.py`
  reach into this component's internals — see the `utils` entry); `ingest-xmlupload` (heavy reach-in, see
  Boundary rules); `validate-data` (two-way, see that entry)
- **Boundary rules**:
    - `ingest_xmlupload` and `resume_xmlupload` bypass the `xmlupload()` entry point and call
    `execute_upload()` and internal modules directly: ingest uses `models/` and `prepare_xml_input/`, resume
    uses `models/` (upload_clients, upload_state). The two components are really one tightly-coupled upload
    pipeline split across two CLI surfaces. (enforcement: docs-only; strong candidate for a `dune-grill`
    ADR — either merge the map entries or promote `execute_upload()`/`upload_config.py` to a documented
    shared interface)
    - New value/property type touches six places: a `KnoraValueType` member
    (`utils/xml_parsing/models/parsed_resource.py`, outside this component), a `TYPE_TRANSFORMER_MAPPER`
    entry (`prepare_xml_input/get_processed_resources.py`), usually a transformer function in
    `prepare_xml_input/transform_input_values.py` (widen `InputTypes` for a new parsed shape), a
    `Processed*` dataclass (`models/processed/values.py`), an `RDFPropTypeInfo` constant plus an
    `RDF_LITERAL_PROP_TYPE_MAPPER` entry (`make_rdf_graph/constants.py`), and a case in
    `_make_one_value_graph` (`make_rdf_graph/make_values.py`). (enforcement: docs-only)
- **Durable state**: reads the XML input file; writes resources to the DSP server; writes a resumable-state
  pickle at `~/.dsp-tools/xmluploads/<server>/resumable/latest.pkl` only while a stash is pending, deleted
  on success (single writer: `handle_errors.save_upload_state`, called from `execute_upload`; read by
  `resume_xmlupload`). On every run, writes an ID→IRI mapping JSON twice: `./id2iri_<shortcode>_<server>_<ts>.json`
  and `~/.dsp-tools/id2iri/id2iri_<ts>_<shortcode>_<server>.json`.
- **Fingerprint**: `e1182f6d651a`

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
- **Depends on**: `clients` (BulkIngestClient, BulkIngestedAssetClient, DspIngestClientLive,
  ProjectClientLive, LegalInfo/List clients), `xmlupload` (execute_upload, models, prepare_xml_input,
  upload_config — heavy reuse), `validate-data`, `cli` (`cli.args` — inverted, see the `cli` entry), `utils`
  (incl. `dsp_user_account_check`), `setup` (ansi_colors), `error`
- **Used by**: `cli` (calls each CLI subcommand's function); `clients` (`bulk_ingest_client.py` reaches into
  this component's internals — see Boundary rules)
- **Boundary rules**:
    - `clients/bulk_ingest_client.py` imports exception types from this component's `exceptions.py` and
    `upload_files/upload_failures.py` — an inversion mirroring the one noted under `clients`.
    (enforcement: docs-only)
    - New ingest step: add a module under the relevant subpackage exposing one public function, wire it into
    `cli/create_parsers.py` + `cli/call_action_with_network.py`, and reuse `commands/xmlupload`'s
    `UploadState`/`UploadClients`/`execute_upload` rather than duplicating upload logic. (enforcement: review)
- **Durable state**: writes uploaded bitstreams to the dsp-ingest server; writes/reads
  `mapping-<shortcode>.csv` in the working directory (rotated on rewrite); reads the resumable pickle that
  `commands/xmlupload`'s `execute_upload` wrote; writes optional failure-report CSVs past a threshold.
- **Fingerprint**: `de4586a6c7c5`

### other-commands

- **Paths**: `src/dsp_tools/commands/id2iri.py`, `update_legal/**`, `mapping/**`, `start_stack/**`,
  `migration/**`, `excel2xml/**`
- **Purpose**: Six small, largely independent commands bundled into one entry: `id2iri` (ID→IRI replacement
  in XML), `update-legal` (migrates legal metadata to bitstream attributes), `mapping config`/`update`
  (replaces an ontology's external mappings from Excel), `start-stack`/`stop-stack` (local DSP stack via
  Docker), `migration` (all-in-one export/import), and `excel2xml` (deprecated library, superseded by
  `xmllib`).
- **Key entities**: `id2iri()`, `update_legal_metadata()`, `mapping_update()`, `StackHandler`, `migration()`
- **Public interface**: one function/class per command; `excel2xml` additionally exposes ~20 `make_*prop`
  helpers as a library surface (no CLI subcommand of its own). `excel2xml/excel2xml_cli.py`'s `excel2xml()`
  is referenced by nothing (dead code; vulture excludes the directory).
- **Local-context kit**: `update_legal/CLAUDE.md`, `docs/developers/architecture/migration-command.md`, plus
  one main module per command — treated as six small kits rather than one shared budget, since the six share
  no code with each other.
- **Depends on**: `utils`, `error`, `setup` (ansi_colors: mapping, migration), `cli` (mapping:
  `cli.args.ServerCredentials` and `cli.utils` — inverted, see the `cli` entry), `xmllib` (update_legal,
  excel2xml), top-level `legacy_models` (excel2xml), `clients` (mapping, migration), `resources` (start_stack
  Compose/template files), `excel2json` (`mapping/parse_excel.py` reach-in, see Boundary rules),
  Docker/subprocess (start_stack)
- **Used by**: `cli` (each of the five CLI-wired commands); `src/dsp_tools/__init__.py` imports `excel2xml`
  unconditionally at package init; `utils/data_formats/shared.py` imports
  `excel2xml.propertyelement.PropertyElement` (reach-in)
- **Boundary rules**:
    - `mapping/parse_excel.py` imports from `excel2json` (see that entry) — the one cross-import among these
    six. (enforcement: docs-only)
    - `utils/data_formats/shared.py` importing `commands.excel2xml.propertyelement.PropertyElement` is an
    inverted reach-in (utils depending on a command). (enforcement: docs-only)
    - Not a reserved "small command" slot: a new small command is wired exactly like any other command
    (`create_parsers.py` + `call_action.py` + `call_action_files_only.py`/`call_action_with_network.py`).
    `excel2xml` is the one exception, with no CLI wiring at all (deprecated, library-only).
    (enforcement: review)
- **Durable state**: `update_legal` (reads XML, writes `*_updated` XML and a problems CSV), `mapping` (reads
  Excel, writes ontology mappings to the server; `config` writes a config template), `start_stack` (copies
  resources into `~/.dsp-tools/start-stack`, renders templates there, manages containers), `migration`
  (writes `export-<shortcode>.zip` and `migration-references-<shortcode>.json` under
  `~/.dsp-tools/migration/` by default, plus a config template), `id2iri` (reads XML + JSON mapping file,
  writes XML), `excel2xml` (none — pure library).
- **Fingerprint**: `5b7702e157f5`

### xmllib

- **Paths**: `src/dsp_tools/xmllib/**`
- **Purpose**: Public API library for programmatic XML-data-file creation, meant for user scripts and the
  external `0854-daschland-scripts` repo, independent of the rest of dsp-tools.
- **Key entities**: `Resource`, `XMLRoot`, `AudioSegmentResource`, `LinkResource`, `RegionResource`,
  `VideoSegmentResource`, `LicenseRecommended`/`LicenseOther`, `GeolocationCoordinates`
  (`GeographicCRS84`/`ProjectedLV95`/`ProjectedLV03`), `SourceProvenance`, value checkers/converters
- **Public interface**: everything explicitly re-exported (`as`-aliased) in `xmllib/__init__.py` — general
  helpers, config/enum types, resource models, license classes, geolocation coordinate classes,
  `SourceProvenance`, value checkers/converters.
- **Local-context kit**: `CLAUDE.md`, `__init__.py`, `models/root.py`, `models/res.py`,
  `internal/serialise_resource.py`, `general_functions.py`
- **Depends on**: `lxml`, `pandas`, `regex`, `loguru`, `typing_extensions` (true-external);
  `dsp_tools.error`, `dsp_tools.setup`, `dsp_tools.utils.data_formats` (geolocation_util, uri_util),
  `dsp_tools.utils.xml_parsing` (in-process — see Boundary rules)
- **Used by**: `other-commands` (excel2xml, update_legal), `setup/warnings_config.py` (reach-in),
  `src/dsp_tools/__init__.py`, `docs` (mkdocstrings), external user scripts, the `0854-daschland-scripts`
  repo
- **Boundary rules**:
    - xmllib does not import dsp-tools internals (ADR 0002). The only exception: shared constants and
    data-format utilities from `dsp_tools.utils` (today `utils/data_formats/geolocation_util.py` and
    `utils/data_formats/uri_util.py`; `utils/geolocation_constants.py` only transitively).
    - **Stated rule violated**: 7 files import from `dsp_tools.error`, `dsp_tools.setup`, or
    `dsp_tools.utils.xml_parsing`: `internal/{exceptions,serialise_resource,serialise_values,
    xmllib_warnings,xmllib_warnings_util}.py`, `models/internal/file_values.py`, `models/root.py`.
    (enforcement: docs-only; ruff `TID` is on, but no `banned-api` config exists)
    - Callers that bypass `__init__.py`: `setup/warnings_config.py` (`internal.xmllib_warnings`),
    `commands/excel2xml/excel2xml_lib.py` (`internal.input_converters`, `general_functions`), and
    `commands/update_legal/{models,xml_operations}.py` (`general_functions`,
    `models.licenses.recommended.License`). (enforcement: docs-only)
    - New helper: add to `general_functions.py`/`value_checkers.py`/`value_converters.py` or a new `models/`
    class, then explicitly re-export it via `from .module import X as X` in `__init__.py`.
    (enforcement: review)
- **Durable state**: none persistent — writes XML files on demand (`models/root.py`) and, if
  `XMLLIB_WARNINGS_CSV_SAVEPATH` is set, a warnings CSV (single writer: `internal/xmllib_warnings_util.py`).
- **Fingerprint**: `f80eb2c2f66e`

### utils

- **Paths**: `src/dsp_tools/utils/**`
- **Purpose**: Shared, stateless helpers used by every command: HTTP (`request_utils.py`), XML parsing
  (`xml_parsing/`), data-format checks (`data_formats/`), JSON parsing, interactive prompts, RDF constants,
  the geolocation CRS table and checks (`geolocation_constants.py`, `data_formats/geolocation_util.py`), and
  the project-admin-account check (`dsp_user_account_check.py`).
- **Key entities**: `request_utils` (retry/backoff HTTP), `parse_clean_validate_xml`, `get_parsed_resources`,
  `replace_id_with_iri`, `rdf_constants`, `geolocation_constants`, `get_geolocation_problem`,
  `dsp_admin_account_email`, `check_for_dsp_admin_account_email_for_data_upload`
- **Public interface**: every file is directly importable; there is no `__init__.py` gate.
- **Local-context kit**: `CLAUDE.md`, `request_utils.py`, `xml_parsing/parse_clean_validate_xml.py`,
  `data_formats/shared.py`, `geolocation_constants.py`
- **Depends on**: `error`, `setup`, top-level `legacy_models` (correctly
  directioned); `commands/get`, `commands/excel2xml`, `commands/xmlupload`, `commands/validate_data` (see
  Boundary rules — incorrectly directioned)
- **Used by**: `cli`, `clients`, every command (incl. `excel2xml`), `xmllib`. `error`, `setup`,
  `legacy_models` and `resources` do not import `utils`.
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
    (enforcement: structure)
    - `geolocation_constants.py` is mirrored by `resources/validate_data/api-shapes.ttl`; a unit test
    (`test_api_shapes_geolocation.py`) keeps the two equal. (enforcement: static-analysis)
- **Durable state**: none — `request_utils.py`'s retry/backoff settings are static, not runtime-mutable.
  The only file write is the user-facing `xsd_validation_errors.csv` (`parse_clean_validate_xml.py`, more
  than 50 XSD errors).
- **Fingerprint**: `ebb76f804523`

### resources

- **Paths**: `src/dsp_tools/resources/**`
- **Purpose**: Static, non-Python assets: the project-definition JSON Schema family and the XML data-file
  XSD, SHACL shapes for validate-data, start-stack's Docker Compose/config templates, the pinned stack image
  versions (`versions.env`), and the SHACL-CLI image pin (`shacl-cli-image.yml`). No code of its own.
- **Key entities**: `project.json`, `properties-only.json`, `resources-only.json`, `lists-only.json`,
  `data.xsd`, `api-shapes.ttl`, `docker-compose.yml`, `versions.env`, `shacl-cli-image.yml`
- **Public interface**: the files themselves are the contract (JSON Schema, XSD, SHACL shapes,
  Compose/template files). The GitHub raw `main` URLs of `schema/project.json` and `schema/data.xsd` are
  hard-coded as `$schema`/schemaLocation in `get.py`, `excel2json/models/json_header.py`,
  `xmllib/models/root.py` and `excel2xml_lib.py`, so renaming or moving them breaks user files.
- **Local-context kit**: `schema/project.json`, `schema/data.xsd`, `validate_data/api-shapes.ttl`,
  `start-stack/docker-compose.yml`, `start-stack/versions.env`, `test/distribution/test_cli_deps_resources.py`
- **Depends on**: none (no code); `api-shapes.ttl`'s CRS table mirrors `utils/geolocation_constants.py`
- **Used by**: `create` (`project.json`); `excel2json` (`properties-only.json`, `resources-only.json`,
  `lists-only.json`); `validate-data` (SHACL shapes, `shacl-cli-image.yml`); `utils` (`data.xsd`, loaded by
  `xml_parsing` for `xmlupload`, `ingest-xmlupload`, `validate-data`, `cli`, `id2iri`, `excel2xml` and
  `xmllib`); `start_stack` (all of `start-stack/`); `tests`
  (`versions.env`, `data.xsd`, `api-shapes.ttl`); `repo-tooling` (`bump_stack_versions.py` writes
  `versions.env`, `publish-release-to-pypi.yml` reads it)
- **Boundary rules**:
    - Read-only at runtime. Single writer per file: a human via PR, except `versions.env`, whose only writer
    is `scripts/bump_stack_versions.py` via a bot PR from `bump-stack-versions.yml` (the file says "Do not
    edit by hand"). `start_stack.py` only writes *copies* into the user's `~/.dsp-tools/start-stack`, never
    back into this tree. (enforcement: review)
    - Runtime code (`src/`) loads these files via `importlib.resources` (never a relative `open()` path), as
    required for correct behavior when installed from a wheel. Tests and scripts use repo-relative paths.
    `test/distribution/test_cli_deps_resources.py` smoke-tests the installed wheel for the `schema/` files
    only; nothing checks the loading style or `start-stack/`/`validate_data/`. (enforcement: review)
    - `api-shapes.ttl` must stay equal to `utils/geolocation_constants.py`; `test_api_shapes_geolocation.py`
    asserts this. (enforcement: static-analysis)
    - New schema/shape/template: add the file under the matching subfolder and wire it into the consuming
    module by hand (`start_stack`'s directory copy-loop picks up new plain files automatically; `.j2`
    templates need explicit render logic). (enforcement: review)
- **Durable state**: these files ARE the durable state; no runtime writer (`versions.env` is bot-written, see
  Boundary rules).
- **Fingerprint**: `3267eab72200`

### docs

- **Paths**: `docs/**`, `mkdocs.yml`
- **Purpose**: The mkdocs-served, user-facing documentation site — distinct from the agent-facing
  `CLAUDE.md`/`CONVENTIONS.md`/`REVIEW.md` at the repo root, which this component does not include.
  `docs/adr/` is the one exception inside `docs/**`: it is excluded from the published site (`not_in_nav`
  in `mkdocs.yml`) because ADRs are a lightweight, git-native decision log, not a site page. The five ADRs
  (0001–0005) have no index page; `CONVENTIONS.md` and `REVIEW.md` reference them.
- **Key entities**: mkdocs nav sections — Overview, User Guides, Running a Local Stack, Data Modelling, Data
  for Mass-Upload, Advanced Workflows, Information for developers, Changelog
- **Public interface**: the rendered site's nav tree, defined in `mkdocs.yml`, and its page/anchor URLs on
  docs.dasch.swiss, which xmllib docstrings link to.
- **Local-context kit**: `mkdocs.yml`, `docs/developers/mkdocs.md`, `.github/workflows/check-docs.yml`,
  `scripts/validate_xmllib_docstring_links.py`, `docs/xmllib-docs/`, `docs/data-model/json-project/`,
  `docs/developers/architecture/error-handling.md`
- **Depends on**: `xmllib` (mkdocstrings pulls its docstrings for the API reference); `repo-tooling`
  (`docs/changelog.md` includes the root `CHANGELOG.md` via include-markdown)
- **Used by**: developers and agents reading it; `xmllib` (docstrings hard-code page/anchor URLs); a few
  unchecked links from `commands/excel2xml/excel2xml_lib.py` and `commands/update_legal/exceptions.py`; the
  `dasch-swiss/dsp-docs` site. Whether/where to update it on a given change is gated by the `update-docs`
  skill.
- **Boundary rules**:
    - A new page must be added to `mkdocs.yml`'s `nav:` tree by hand — `validation.omitted_files: warn`
    becomes a build-failing error under the `--strict` flag the required `check-docs` CI check runs (see
    `mkdocs.yml`'s own comment above its `validation:` block), so an unregistered page fails CI, it does not
    silently disappear. (enforcement: static-analysis)
    - `docs/adr/**` is carved out of this rule via `not_in_nav` in `mkdocs.yml`, since ADRs are never meant
    to get a nav entry. (enforcement: structure)
    - Renaming or moving a page or heading that an xmllib docstring links to fails
    `just check-xmllib-docstring-links` in `check-docs`. The script scans only `xmllib/`, so links from
    other code are not checked. (enforcement: static-analysis)
    - External http(s) links are checked by lychee on every pull request (`check-external-links.yml`,
    config `lychee.toml`), deliberately not a required check. (enforcement: static-analysis, non-gating)
- **Durable state**: none in this repo — the combined site is published from the separate
  `dasch-swiss/dsp-docs` repo, which dsp-tools' release workflow notifies on release.
- **Fingerprint**: `73541aa55265`

### tests

- **Paths**: `test/**`, `testdata/**`
- **Purpose**: The six-tier test suite (unittests, integration, e2e via testcontainers, legacy_e2e against
  a running stack, distribution against an installed wheel plus `start-stack`, benchmarking) and its
  fixture data.
- **Key entities**: `pytest_sessionstart` (`test/conftest.py`), `USED_SHORTCODE_SHORTNAMES.md`,
  `systematic-project-4123.json`/`test-data-systematic-4123.xml`, `_get_image_versions`
  (`test/e2e/setup_testcontainers/setup.py`)
- **Public interface**: none — this component consumes the rest of the map.
- **Local-context kit**: `test/conftest.py`, CONVENTIONS.md's Testing Conventions section,
  `testdata/USED_SHORTCODE_SHORTNAMES.md`, `test/e2e/setup_testcontainers/setup.py`
- **Depends on**: every component in this map (it's what's under test), including `repo-tooling`'s
  `scripts/` (`test/unittests/scripts/`); testcontainers read image versions from
  `resources/start-stack/versions.env`; pytest/pytest-xdist/testcontainers and the DSP Docker images
  (true-external)
- **Used by**: CI — `tests.yml` (unittests and integration via `just`; benchmarking and distribution via
  raw `pytest`), `tests-e2e.yml` (via `just e2e-test-*` and `just legacy-e2e-tests`); developers
- **Boundary rules**:
    - Reaching into private (`_`-prefixed) names is the norm in unit tests (about half of the files, incl.
    the `scripts/` tests) and occurs in integration tests (7 of 22) and in the e2e `validate_data` tests
    (`_validate_data`, 4 of 15 e2e files). Only legacy_e2e stays strictly black-box (CLI-level).
    (enforcement: review)
    - E2E three-place wiring: a test dir or file under `test/e2e/commands/`, a `just e2e-test-<name>`
    recipe, and a matching job in `.github/workflows/tests-e2e.yml` — a test not registered in all three
    silently never runs in CI. (enforcement: docs-only; verified consistent for all six e2e targets)
- **Durable state**: `testdata/USED_SHORTCODE_SHORTNAMES.md` is a human-maintained register (single writer:
  whoever adds a shortcode, reviewed via PR diff); the e2e testcontainers and the distribution tier's
  `start-stack` spin up ephemeral Docker state, discarded after the run.
- **Fingerprint**: `c1e12a0a6c55`

### repo-tooling

- **Paths**: `pyproject.toml`, `justfile`, `uv.lock`, `.github/**`, `scripts/**`, `k6/**`,
  `.pre-commit-config.yaml`, `.editorconfig`, `.gitignore`, `.markdownlint.yml`, `.yamllint.yml`,
  `.yamlfmt.yml`, `.kodus-readiness.yml`, `codecov.yml`, `lychee.toml`, `CHANGELOG.md`, `LICENSE`,
  `README.md`, `.vulture_whitelist.py`, `CLAUDE.md`, `CONVENTIONS.md`, `REVIEW.md`,
  `CONTEXT.md`, `eng.yaml`, `src/dsp_tools/__init__.py`, `src/dsp_tools/py.typed`,
  `src/dsp_tools/commands/__init__.py`, `.claude/**`
- **Purpose**: Repo-level build, lint, and CI tooling — everything a developer or CI runs that isn't
  application code, docs, or tests.
- **Key entities**: `just` recipes (lint, mypy, vulture, unittests, integration-tests, e2e-tests,
  legacy-e2e-tests), release-please, `scripts/bump_version.py` (dev-release `.postN`),
  `scripts/bump_stack_versions.py` (start-stack version-bump PR), `scripts/merge_pr_when_green.py` and the
  composite action `.github/actions/merge-pr-when-green` (bot-PR auto-merge), `readiness.yml`
- **Public interface**: the justfile's recipe names, any `.github/workflows/*.yml` (auto-discovered by
  GitHub Actions), and the local composite actions `.github/actions/*/action.yml`.
- **Local-context kit**: `justfile`, `pyproject.toml`, `README.md` (dev-onboarding lives here; no
  CONTRIBUTING.md exists)
- **Depends on**: ruff, mypy, pytest, vulture, markdownlint-cli, yamllint, yamlfmt, lychee, pre-commit,
  release-please, `gh` CLI (true-external); the dasch-specs `assessments/regression-check` action, fetched
  at `main` by `readiness.yml` (remote-owned); `scripts/validate_xmllib_docstring_links.py` imports
  `dsp_tools.setup.ansi_colors` (the one in-process import); `scripts/bump_stack_versions.py` writes
  `resources/start-stack/versions.env`
- **Used by**: CI, developers running `just <recipe>`, pre-commit git hooks; `tests`
  (`test/unittests/scripts/` imports `scripts.*`, incl. private names); `docs` (includes `CHANGELOG.md`)
- **Boundary rules**:
    - `.github/workflows/*.yml` is reserved-path/auto-discovered by GitHub Actions; the justfile is one flat
    file with no such convention. CI does not run `just lint`: `lint-code.yml` and `check-docs.yml` call
    each lint recipe one by one. So a new lint recipe is wired by hand in two places: `lint`'s parallel
    dispatcher and a CI workflow. (enforcement: structure for workflows, docs-only for the justfile/CI
    wiring)
    - `k6/` is fully standalone (its own justfile), not referenced from the root justfile or any CI workflow.
    (enforcement: structure)
    - `scripts/bump_stack_versions.py` writes `resources/start-stack/versions.env` through a bot PR
    (`bump-stack-versions.yml`). (enforcement: review)
- **Durable state**: `CHANGELOG.md` and `pyproject.toml`'s version field are written by the release-please
  GitHub Action, not by hand; `scripts/bump_version.py` also rewrites the version to `X.Y.Z.postN`, but only
  inside the CI checkout of `publish-dev-release-to-pypi.yml` (never committed). `uv.lock` has three
  writers, all through the uv resolver: developers (`uv sync`/`uv add`), `release-please.yml` (`uv lock`
  plus commit), and dependabot.
- **Fingerprint**: `6c870c4e5a2a`

## Cross-cutting concerns

### error/ (`src/dsp_tools/error/**`)

Two-branch exception hierarchy: `BaseError` → `UserError` (user can fix it) / `InternalError` (needs a
developer; auto-appends contact info and the log path). `custom_warnings.py` mirrors this for warnings;
`problems.py` defines the `Problem` protocol used by Group B's aggregated-error pattern. It also holds the
DSP-admin-account error and warnings (`DspAdminAccountNotUsedForUploadError`,
`DspAdminAccountNotUsedForUploadWarning`, `DspAdminAccountNotInProjectFileWarning`): an error on prod-like
servers, a warning elsewhere. Per `docs/developers/architecture/error-handling.md`: catch only recoverable
external failures and let your own bugs crash; Group A commands (`create`, `xmlupload`, `get`, …) fail
fast, Group B commands (`excel2json`, `validate-data`, `xmllib`, …) collect every `Problem` into one
aggregated `UserError`. Ten command modules define their own `exceptions.py` subclassing from here (so do
`cli/`, `clients/`, `utils/` and `xmllib/internal/`). Imported by 88 files in `src/`, 127 including tests.
No durable state.

- **Fingerprint**: `e302615efb18`

### setup/ (`src/dsp_tools/setup/**`)

Process-startup wiring, not a component with request-level dependents: `logger_config()` (loguru sinks) and
`initialize_warnings()` (routes `DspToolsWarning` through custom formatting) are each called once, in
`cli/entry_point.py` (and once per session in `test/conftest.py`'s `pytest_sessionstart`). `dotenv.py` loads
a local `.env`; `ansi_colors.py` is terminal color constants. Imported by 36 files. Durable state is the
one-shot loguru sink registry, written once at process start.

- **Fingerprint**: `14a3a91c42d8`

### legacy_models/ (`src/dsp_tools/legacy_models/**` — top-level; distinct from `commands/get/legacy_models/`)

Three shared, effectively-immutable value types: `LangString` (language-tagged string), `DateTimeStamp`
(validated `xsd:dateTimeStamp`), `ProjectContext` (a one-shot snapshot of a project's shortcode/group/user
lookups, built once from server data). Imported by `get`, `excel2xml`, `validate-data`, `xmlupload`, and
`utils`. Still raises `BaseError` directly rather than `UserError`/`InternalError` — a known legacy exemption
per the error-handling doc. No durable state beyond each instance's own value.

- **Fingerprint**: `7e054e7179fd`

## Conventions

- **Module granularity budget**: local-context kit ≤7 files per component (no component in this repo needed
  more). (enforcement: review)
- **One-way top-level dependency direction** (as designed; violated today in several places — see below):
  `cli` → `commands/*` → `utils`/`clients`/`xmllib`/`resources` → `error`/`setup`/`legacy_models`. Nothing
  below a layer should import from above it. Besides the banned constructs below, top-level
  `legacy_models/projectContext.py` imports `clients.connection` and `commands/get/legacy_models`.
  (enforcement: docs-only; no import-linter contract exists)
- **Commands never import from other commands** (stated in `utils/CLAUDE.md` and `CONVENTIONS.md`;
  enforcement: docs-only; currently violated): `mapping`→`excel2json`, `validate-data`↔`create`,
  `validate-data`↔`xmlupload`, `ingest-xmlupload`/`resume-xmlupload`→`xmlupload`. Shared logic belongs in
  `utils/` instead.
- **Wiring convention**: a new CLI command touches three files — `cli/create_parsers.py`,
  `cli/call_action.py`, and either `cli/call_action_files_only.py` or `cli/call_action_with_network.py`
  depending on whether it needs network/Docker access. (enforcement: review)
- **Colocated-doc expectation**: most command directories carry a `CLAUDE.md`; `commands/get/` is the one
  confirmed gap. (enforcement: docs-only)
- **Banned constructs**:

| Pattern | Why it couples globally | Alternative | Enforcement |
| --- | --- | --- | --- |
| A command imports directly from another command's package | Spreads blast radius silently; contradicts the stated rule | Move the shared logic into `utils/` or a new neutral module | docs-only (violated: `mapping`→`excel2json`, `validate-data`↔`create`, `validate-data`↔`xmlupload`, `ingest-xmlupload`/`resume-xmlupload`→`xmlupload`) |
| A command imports from `cli/` | Inverts the `cli` → `commands/*` direction; CLI-argument types leak into command code | Define the shared argument type outside `cli/` (for example in `utils/`) and let `cli` build it | docs-only (violated: 14 files import `cli.args`, `mapping/config_file.py` imports `cli.utils` — see the `cli` entry) |
| `utils/` importing from `commands/` | Inverts `utils`' leaf-dependency role; real circular-import risk since every command also imports `utils` | Move the shared type/constant into `utils/` itself | docs-only (violated: 5 files / 9 import sites — see the `utils` entry) |
| `clients/` importing from `commands/` | `clients/` is documented as generic/reusable; a command-specific import defeats that and already forms a module cycle with `commands/xmlupload/exceptions.py` | Define the shared type in `clients/` or `utils/` instead | docs-only (violated: `clients/ingest.py`, `clients/bulk_ingest_client.py`) |
| `xmllib` importing `dsp_tools.error`/`setup`, or `utils` outside shared constants and data-format utilities | ADR 0002 keeps `xmllib` conceptually independent of the rest of dsp-tools | Vendor the helper into `xmllib/internal/`. Shared constants and data-format utilities go in `utils/` and xmllib imports them from there (ADR 0002 exception) | docs-only (violated: 7 files — see the `xmllib` entry) |
