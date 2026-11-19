# CLAUDE.md for the dsp-tools package

This folder is the package `dsp-tools` of the uv workspace.
The overview, the commands and the conventions are in the `CLAUDE.md` and `CONVENTIONS.md` at the repository root.

- Paths in the files under `packages/dsp-tools/` (for example the per-module `CLAUDE.md` files and the docs)
  are relative to `packages/dsp-tools/`. `src/dsp_tools/...` means `packages/dsp-tools/src/dsp_tools/...`.
- The tests run with `packages/dsp-tools/` as the working directory.
  From the repository root, use `just dsp-tools-pytest packages/dsp-tools/test/<path>`.
