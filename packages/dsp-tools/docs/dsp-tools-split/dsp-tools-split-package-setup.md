# Set-Up for the `dsp-tools` Split into an Own PyPI Package

This document shows how the package `dsp-vre-lib` splits from `dsp-tools` on a technical level,
and how `dsp-vre-lib` gets to PyPI.
The document is a timeline in two steps.
The public interface of `dsp-vre-lib` is in the [ADR](ADR-dsp-vre-lib.md).

## Step One: uv Workspace in the `dsp-tools` Repository

The `dsp-tools` repository becomes a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)
with two packages.

### File Tree

```text
dsp-tools/                          # repository root, virtual workspace root
├── pyproject.toml                  # [tool.uv.workspace] members = ["packages/*"], dev dependencies, ruff config
├── uv.lock                         # one lock file for both packages
├── justfile
├── mkdocs.yml                      # docs_dir: packages/dsp-tools/docs
├── .github/workflows/
├── scripts/                        # repository tooling, with its tests in scripts/test/
├── src/dsp_tools/resources/schema/ # copy of the schema files, keeps the old schema URLs valid
└── packages/
    ├── dsp-tools/
    │   ├── CHANGELOG.md
    │   ├── docs/
    │   ├── pyproject.toml          # name = "dsp-tools", CLI entry point, pytest, mypy and vulture config
    │   ├── src/dsp_tools/
    │   ├── test/
    │   └── testdata/
    └── dsp-vre-lib/
        ├── CHANGELOG.md            # written by release-please
        ├── docs/
        ├── pyproject.toml          # name = "dsp-vre-lib", pytest and mypy config
        ├── src/dsp_vre_lib/
        └── test/
```

The root `pyproject.toml` has no `[project]` table.
It holds the workspace definition, the dev dependencies and the shared ruff configuration.
The `pyproject.toml` of each package extends the ruff configuration with `extend = "../../pyproject.toml"`.

The pytest and mypy configuration is in each package, not at the root:

- The tests use paths relative to the working directory, for example `testdata/...`.
  Thus the tests of each package run with the package folder as the working directory.
  The `just` recipes do this.
- Two `test/` folders in one mypy run give the error "Duplicate module named test".
  Thus mypy runs once for each package.

The old schema URLs (`.../main/src/dsp_tools/resources/schema/...`) are in files of users.
The copy at the old path keeps these URLs valid. `just check-schema-copy` checks that the copy is equal.

### Dependency

`dsp-tools` declares `dsp-vre-lib` as a normal dependency, from the first import of `dsp_vre_lib`.
In the workspace, uv resolves it to the local source.
During the versions 0.x, the range is `>=0.1,<0.2`. From version 1.0, the range is `>=1.0,<2.0`:

```toml
# packages/dsp-tools/pyproject.toml
[project]
dependencies = ["dsp-vre-lib>=0.1,<0.2"]

[tool.uv.sources]
dsp-vre-lib = { workspace = true }
```

The dependency goes in one direction only: `dsp_vre_lib` never imports `dsp_tools`.
The ruff rule `TID251` (banned-api) in the `dsp-vre-lib` ruff configuration bans imports of `dsp_tools`.
The rule bans the module and all its submodules.
CI runs ruff, thus a violation blocks the merge.

### CI

CI keeps the current fine-grained jobs.
Each package gets its own jobs (unit, integration, e2e).

### Content of Each Package

`dsp-vre-lib` gets:

- The server clients from `src/dsp_tools/clients/`.
- The data validation against the server data model.
- The dataclasses of the public interface.

`dsp-tools` keeps:

- The CLI.
- The file formats: JSON project file, XML data file, Excel files.
- `xmllib` and `excel2xml`.
- `start-stack` and `stop-stack`.

### Release

- `dsp-vre-lib` has its own semantic version in step one and in step two.
- The first version is 0.1.0. Version 1.0.0 comes when the interface is stable.
- `dsp-vre-lib` states the `dsp-api` versions that it supports. It checks the server version when it connects.
- `dsp-vre-lib` has its own release-please component and its own PyPI workflow (`publish-dsp-vre-lib-to-pypi.yml`).
  The workflow uses PyPI trusted publishing.
- release-please opens one release PR for each package.
  The tags are `vX.Y.Z` for `dsp-tools` and `dsp-vre-lib-vX.Y.Z` for `dsp-vre-lib`.
  Only the `dsp-tools` release PR takes part in the automatic merge of the release train.
- A merge of the `dsp-vre-lib` release PR publishes the package.
  The first release comes when the package has content.
- A commit that changes only files outside `packages/` makes no release.
- `dsp-tools` pins a compatible range of `dsp-vre-lib`.

## Step Two: Move `dsp-vre-lib` into `dsp-api`

1. Move `packages/dsp-vre-lib/` into the `dsp-api` repository.
2. Publish `dsp-vre-lib` to PyPI from `dsp-api`.
   The `dsp-vre-lib` version stays independent of the `dsp-api` release number.
3. Remove `dsp-vre-lib` from the workspace in the `dsp-tools` repository.
   `dsp-tools` then gets `dsp-vre-lib` from PyPI.

The `dsp-tools` repository keeps the `packages/` layout.
The layout gives space for more packages later.

## Open Questions

- Do the tests that need a DSP stack (testcontainers) move with `dsp-vre-lib`?
- Step two: how do we build and publish `dsp-vre-lib` with Bazel in `dsp-api`?
  `dsp-api` uses `rules_python` only for internal tooling scripts,
  without third-party Python dependencies and without wheels.
  Python packaging and publishing are thus new in `dsp-api`.
- Step two: do we copy the git history of `packages/dsp-vre-lib/` into `dsp-api`?
  `git filter-repo` can extract the history of the folder, incl. the old paths before the move.
  `dsp-api` then merges it as unrelated history. `dsp-tools` keeps its full history in all cases.
  Trade-off: `dsp-api` gets many commits from another repository.
