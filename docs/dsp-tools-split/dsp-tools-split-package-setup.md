# Set-Up for the `dsp-tools` Split into an Own PyPI Package

This document shows how the package `dsp-vre` splits from `dsp-tools` on a technical level,
and how `dsp-vre` gets to PyPI.
The document is a timeline in two steps.
The public interface of `dsp-vre` is in the [ADR](ADR-dsp-vre.md).

## Step One: uv Workspace in the `dsp-tools` Repository

The `dsp-tools` repository becomes a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)
with two packages.

### File Tree

```text
dsp-tools/                          # repository root, virtual workspace root
├── pyproject.toml                  # [tool.uv.workspace] members = ["packages/*"], shared tool config
├── uv.lock                         # one lock file for both packages
├── justfile
├── .github/workflows/
└── packages/
    ├── dsp-tools/
    │   ├── docs/
    │   ├── pyproject.toml          # name = "dsp-tools", CLI entry point
    │   ├── src/dsp_tools/
    │   └── test/
    └── dsp-vre/
        ├── docs/
        ├── pyproject.toml          # name = "dsp-vre"
        ├── src/dsp_vre/
        └── test/
```

The root `pyproject.toml` has no `[project]` table.
It holds the workspace definition and the shared configuration for ruff, mypy and pytest.

### Dependency

`dsp-tools` declares `dsp-vre` as a normal dependency.
In the workspace, uv resolves it to the local source:

```toml
# packages/dsp-tools/pyproject.toml
[project]
dependencies = ["dsp-vre>=1.0,<2.0"]

[tool.uv.sources]
dsp-vre = { workspace = true }
```

The dependency goes in one direction only: `dsp_vre` never imports `dsp_tools`.

### Content of Each Package

`dsp-vre` gets:

- The server clients from `src/dsp_tools/clients/`.
- The data validation against the server data model.
- The dataclasses of the public interface.

`dsp-tools` keeps:

- The CLI.
- The file formats: JSON project file, XML data file, Excel files.
- `xmllib` and `excel2xml`.
- `start-stack` and `stop-stack`.

### Release

- `dsp-vre` has its own semantic version.
- `dsp-vre` has its own release-please component and its own PyPI workflow.
- `dsp-tools` pins a compatible range of `dsp-vre`.

## Step Two: Move `dsp-vre` into `dsp-api`

1. Move `packages/dsp-vre/` into the `dsp-api` repository.
2. Publish `dsp-vre` to PyPI from `dsp-api`.
   The `dsp-vre` version is the same as the `dsp-api` release number.
3. Remove `dsp-vre` from the workspace in the `dsp-tools` repository.
   `dsp-tools` then gets `dsp-vre` from PyPI.

The `dsp-tools` repository keeps the `packages/` layout.
The layout gives space for more packages later.

## Open Questions

- How do we enforce that `dsp_vre` never imports `dsp_tools`? Options: import-linter, a ruff rule, a CI check.
- CI: one shared test job or one job per package?
- Do the tests that need a DSP stack (testcontainers) move with `dsp-vre`?
- Step two: how does the Python build fit into the Bazel and sbt build of `dsp-api`?
- Step two: do we keep the git history of `packages/dsp-vre/` when it moves?
- Step two: which first version does `dsp-vre` get in lockstep, and how do we map the step-one versions?
