# CLAUDE.md for dsp-vre-lib

`dsp-vre-lib` is the Python package for all interaction with a DSP server.
The decisions about its interface are in `../dsp-tools/docs/dsp-tools-split/ADR-dsp-vre-lib.md`.

## Rules

- `dsp_vre_lib` never imports `dsp_tools`. The dependency goes in one direction only.
  The ruff rule `TID251` (banned-api in `pyproject.toml`) enforces this.
- The package has no file formats: no parsing or writing of JSON project files, XML data files or Excel files.
  Input and output are Python objects.

## Commands

Run the commands from the repository root:

- Unit tests: `just vre-lib-unittests`
- Type checking: `just mypy-vre-lib`
- Paths in this package are relative to `packages/dsp-vre-lib/`. The tests run with this folder as the working directory.
