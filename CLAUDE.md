# CLAUDE.md

Orientation for Claude Code in this repository.
This file gives the overview. The files under "Where to read next" hold the detail.

## What is DSP-TOOLS?

DSP-TOOLS is a CLI tool and a Python library for the DaSCH Service Platform (DSP).
It talks to a DSP server: a remote or local machine that runs [DSP-API](https://github.com/dasch-swiss/dsp-api).
It serves two main tasks:

- Create a project and its data models on a DSP server, from a JSON project file.
- Upload data, described in an XML file, to a project on a DSP server whose data model matches.

The CLI commands (user docs: `docs/index.md` and the pages it links to):

| Command                                                             | What it does                                                                       |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `create`                                                            | Creates a project and its data models on a server, from a JSON file.               |
| `get`                                                               | Reads a project from a server and writes it into a JSON file.                      |
| `validate-data`                                                     | Validates an XML data file against the ontology on the server (SHACL).             |
| `xmlupload`                                                         | Uploads the data and the multimedia files of an XML file to a server.              |
| `upload-files`, `ingest-files`, `ingest-xmlupload`                  | The same as `xmlupload`, split into three steps.                                   |
| `resume-xmlupload`                                                  | Resumes an interrupted `xmlupload` or `ingest-xmlupload`.                          |
| `excel2json`, `excel2lists`, `excel2resources`, `excel2properties`  | Create a JSON project file, or one of its sections, from Excel files.              |
| `old-excel2json`, `old-excel2lists`                                 | The same as `excel2json` and `excel2lists`, with an older Excel format for lists.  |
| `id2iri`                                                            | Replaces internal IDs in an XML file with IRIs, from a JSON mapping file.          |
| `update-legal`                                                      | Moves legal metadata in an XML file into `<bitstream>` attributes.                 |
| `start-stack`, `stop-stack`                                         | Run a DSP stack on the local machine.                                              |
| `mapping config`, `mapping update`                                  | Replace the external mappings of an ontology on a server, from an Excel file.      |
| `migration config`, `complete`, `export`, `import`, `clean-up`      | Migrate a project from one DSP server to another.                                  |

Two Python modules are public API:

- `xmllib` (`src/dsp_tools/xmllib/`) helps scripts convert tabular data into an XML data file.
- `excel2xml` does the same, but is deprecated in favour of `xmllib`.

## Where to read next

- `CONVENTIONS.md`: coding, testing, test-data and commit conventions (work phase).
  It also holds the "dsp-tools subsystem inventory".
  Before feature work, walk that inventory with the `change-blast-radius` skill,
  so that no subsystem is silently missed.
- `REVIEW.md`: the code-review checklist (review phase).
- `ARCH-MAP.md`: components, public interfaces and the dependency direction. Load it for boundary questions.
- `CONTEXT.md`: the domain vocabulary.
- `docs/adr/`: architectural decision records.
- `docs/developers/architecture/error-handling.md`: the exception hierarchy, and when to catch or fail.
- The per-module `CLAUDE.md` files under `src/dsp_tools/`, for example `utils/CLAUDE.md` for what goes into utils.

## Development Commands

### Setup

- Install the dependencies and create the virtual environment: `uv sync --all-extras --dev`
- Activate the virtual environment: `source .venv/bin/activate`
- Install the pre-commit hooks: `pre-commit install`
- Make `git blame` skip the reformat commits: `git config blame.ignoreRevsFile .git-blame-ignore-revs`
- Add a dependency: `uv add <package>` (or `uv add --dev <package>`)

### Code quality

- All linters in parallel: `just lint`
- Format the code: `just format`
- Type checking: `just mypy` (run `dmypy restart` if mypy behaves unexpectedly)
- Dead code: `just vulture`
- Single linters: `just ruff-check`, `just ruff-format-check`, `just yamllint`, `just markdownlint` (runs in Docker)

### Tests

- Unit tests: `just unittests`
- Integration tests: `just integration-tests`
- E2E tests (testcontainers start the DSP stack): `just e2e-tests`
- Legacy E2E tests (need a running DSP stack): `just legacy-e2e-tests`
- One test: `pytest test/path/to/test.py::TestClass::test_method`

### Other

- Start a local DSP stack: `dsp-tools start-stack`
- Serve the documentation: `mkdocs serve`
- Remove build artifacts: `just clean`

## Architecture Overview

- `src/dsp_tools/cli/`: the entry point (`entry_point.py`), the argument parsers (`create_parsers.py`),
  and the dispatch to the command handlers (`call_action.py`).
- `src/dsp_tools/clients/`: HTTP clients that several commands use. They are generic and contain no retry logic.
- `src/dsp_tools/commands/`: one subdirectory (or one file) per CLI command. Some commands share a subdirectory.
- `src/dsp_tools/xmllib/`: the public library to create XML data files.
- `src/dsp_tools/utils/`: shared, stateless helpers. `utils/CLAUDE.md` says which helper serves which purpose.

The XML data goes through a pipeline:

1. Parsing: raw XML → etree root → XSD validation → `ParsedResource`
2. Processing: `ParsedResource` → resolved permissions and IRIs → `ProcessedResource`
3. Upload or validation: `ProcessedResource` → API calls, or SHACL validation

Configuration lives in `pyproject.toml` (metadata, dependencies, tool settings),
the `justfile` (task runner), and `.pre-commit-config.yaml` (local hooks).
