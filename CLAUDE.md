# CLAUDE.md

Orientation for Claude Code in this repository.
This file gives the overview. The files under "Where to read next" hold the detail.

## What is DSP-TOOLS?

DSP-TOOLS is a CLI tool and a Python library for the DaSCH Service Platform (DSP).
It talks to a DSP server: a remote or local machine that runs [DSP-API](https://github.com/dasch-swiss/dsp-api).
It serves two main tasks:

- Create a project and its data models on a DSP server, from a JSON project file.
- Upload data, described in an XML file, to a project on a DSP server whose data model matches.

The CLI commands (user docs: `packages/dsp-tools/docs/index.md` and the pages it links to):

| Command                                                             | What it does                                                                       |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `create`                                                            | Creates a project and its data models on a server, from a JSON file.               |
| `get`                                                               | Reads a project from a server and writes it into a JSON file.                      |
| `validate-data`                                                     | Validates an XML data file against the ontology on the server (SHACL).             |
| `xmlupload`                                                         | Uploads the data and the multimedia files of an XML file to a server.              |
| `upload-files`, `ingest-files`, `ingest-xmlupload`                  | The same as `xmlupload`, in three steps. The last one is a bulk data import.       |
| `delete-data-import`                                                | Deletes a bulk data import task that `ingest-xmlupload` left on a server.          |
| `resume-xmlupload`                                                  | Resumes an interrupted `xmlupload`.                                                |
| `excel2json`, `excel2lists`, `excel2resources`, `excel2properties`  | Create a JSON project file, or one of its sections, from Excel files.              |
| `old-excel2json`, `old-excel2lists`                                 | The same as `excel2json` and `excel2lists`, with an older Excel format for lists.  |
| `id2iri`                                                            | Replaces internal IDs in an XML file with IRIs, from a JSON mapping file.          |
| `update-legal`                                                      | Moves legal metadata in an XML file into `<bitstream>` attributes.                 |
| `start-stack`, `stop-stack`                                         | Run a DSP stack on the local machine.                                              |
| `mapping config`, `mapping update`                                  | Replace the external mappings of an ontology on a server, from an Excel file.      |
| `migration config`, `complete`, `export`, `import`, `clean-up`      | Migrate a project from one DSP server to another.                                  |

Two Python modules are public API:

- `xmllib` (`packages/dsp-tools/src/dsp_tools/xmllib/`) helps scripts convert tabular data into an XML data file.
- `excel2xml` does the same, but is deprecated in favour of `xmllib`.

## Where to read next

- `CONVENTIONS.md`: coding, testing, test-data and commit conventions (work phase).
  It also holds the "dsp-tools subsystem inventory".
  Before feature work, walk that inventory with the `change-blast-radius` skill,
  so that no subsystem is silently missed.
- `REVIEW.md`: the code-review checklist (review phase).
- `ARCH-MAP.md`: components, public interfaces and the dependency direction. Load it for boundary questions.
- `CONTEXT.md`: the domain vocabulary.
- `docs/adr/`: architectural decision records for the whole repository.
- `packages/dsp-tools/docs/developers/architecture/error-handling.md`: the exception hierarchy, and when to catch or
  fail.
- The per-module `CLAUDE.md` files under `packages/dsp-tools/src/dsp_tools/`, for example `utils/CLAUDE.md` for what
  goes into utils.

## Development Commands

### Setup

- Install the dependencies and create the virtual environment: `uv sync --all-packages --all-extras --dev`
- Activate the virtual environment: `source .venv/bin/activate`
- Install the pre-commit hooks: `pre-commit install`
- Make `git blame` skip the reformat commits: `git config blame.ignoreRevsFile .git-blame-ignore-revs`
- Add a runtime dependency: `uv add --package dsp-tools <package>`. Add a dev dependency: `uv add --dev <package>`
  (root `pyproject.toml`, shared by all packages).

### Code quality

- All linters in parallel: `just lint`
- Format the code: `just format`
- Type checking: `just mypy` (run `dmypy restart` if mypy behaves unexpectedly). It runs `just mypy-dsp-tools`,
  `just mypy-vre` and `just mypy-scripts`, which also work alone.
- Dead code: `just vulture` (runs `vulture-dsp-tools` and `vulture-vre`)
- Single linters: `just ruff-check`, `just ruff-format-check`, `just yamllint`, `just markdownlint` (runs in Docker)

### Tests

- Unit tests: `just unittests`
- Integration tests: `just integration-tests`
- E2E tests (testcontainers start the DSP stack): `just e2e-tests`
- Legacy E2E tests (need a running DSP stack): `just legacy-e2e-tests`
- One test: `just dsp-tools-pytest packages/dsp-tools/test/path/to/test.py::TestClass::test_method`
- Tests of the repository tooling in `scripts/`: `just scripts-tests`
- Unit tests of `dsp-vre`: `just vre-unittests`. One test: `just vre-pytest packages/dsp-vre/test/<path>`

### Other

- Start a local DSP stack: `dsp-tools start-stack`
- Serve the documentation: `mkdocs serve`
- Remove build artifacts: `just clean`
- After a change to a schema file: `just sync-schema-copy` (CI runs `just check-schema-copy`)

## Architecture Overview

- `packages/dsp-tools/src/dsp_tools/cli/`: the entry point (`entry_point.py`), the argument parsers
  (`create_parsers.py`),
  and the dispatch to the command handlers (`call_action.py`).
- `packages/dsp-vre/src/dsp_vre/clients`: HTTP clients that several commands use. They are generic and contain no
  retry logic.
- `packages/dsp-tools/src/dsp_tools/commands/`: one subdirectory (or one file) per CLI command. Some commands share a
  subdirectory.
- `packages/dsp-tools/src/dsp_tools/xmllib/`: the public library to create XML data files.
- `packages/dsp-vre/`: the Python client library for the DSP-API of a DSP server. Its public interface is not
  designed yet (`packages/dsp-vre/docs/adr/0001-public-interface.md`).
  `dsp_vre.clients` re-exports the client names that dsp-tools uses. It never imports `dsp_tools`.
  See `packages/dsp-vre/CLAUDE.md`.
- `packages/dsp-tools/src/dsp_tools/utils/`: shared, stateless helpers. `utils/CLAUDE.md` says which helper serves which
  purpose.

The XML data goes through a pipeline:

1. Parsing: raw XML → etree root → XSD validation → `ParsedResource`
2. Processing: `ParsedResource` → resolved permissions and IRIs → `ProcessedResource`
3. Upload or validation: `ProcessedResource` → API calls, or SHACL validation

The repository is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/).
Each package is in `packages/`. The plan for the split into packages is in
`docs/dsp-tools-split/dsp-tools-split-package-setup.md`.

- The root `pyproject.toml` holds the workspace definition, the dev dependencies, the shared ruff configuration,
  and the pytest and mypy configuration for `scripts/`.
- The root `.python-version` pins the interpreter of the shared `.venv`, locally and in CI.
  `requires-python` of each package stays the lower bound.
- `packages/dsp-tools/pyproject.toml` holds the metadata, the dependencies, and the pytest, mypy and vulture
  configuration.
- The tests run with `packages/dsp-tools/` as the working directory, because their paths (for example `testdata/...`)
  are relative to it. The `just` recipes do this.
- Paths in files under `packages/dsp-tools/` (for example the per-module `CLAUDE.md` files)
  are relative to `packages/dsp-tools/`. Paths in the files at the repository root are relative to the root.
- `src/dsp_tools/resources/schema/` at the root is a copy of the schema files that keeps old URLs valid.
  Do not edit it. Write it with `just sync-schema-copy`. `just check-schema-copy` checks it.

The `justfile` is the task runner, and `.pre-commit-config.yaml` holds the local hooks.
