# CLAUDE.md for dsp-vre-lib

`dsp-vre-lib` is the Python client library for the DSP-API of a DSP server.
The decisions about its interface are in `docs/adr/` of this package, the interface of `create` in
`docs/create-interface.md`.

## Rules

- `dsp_vre_lib` never imports `dsp_tools`. The dependency goes in one direction only.
  The ruff rule `TID251` (banned-api in `pyproject.toml`) enforces this.
- The package has no file formats: no parsing or writing of JSON project files, XML data files or Excel files.
  Input and output are Python objects.

## Commands

Run the commands from the repository root:

- Unit tests: `just vre-lib-unittests`
- Type checking: `just mypy-vre-lib`
- Dead code: `just vulture-vre-lib`. A name that only dsp-tools or a Protocol uses goes into `.vulture_whitelist.py`.
- Paths in this package are relative to `packages/dsp-vre-lib/`. The tests run with this folder as the working directory.
