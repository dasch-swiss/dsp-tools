---
status: accepted
date: 2026-07
---

# xmllib does not import dsp-tools internals

`xmllib` avoids importing `dsp_tools.error`, `dsp_tools.setup`, and `dsp_tools.utils`, keeping it
conceptually independent of the rest of dsp-tools. This is an architectural boundary, not a technical
requirement for external use: `xmllib` ships as part of the same dsp-tools PyPI package, so anyone using it
already has dsp-tools installed — no separate, dsp-tools-free installation of `xmllib` exists or is needed.

Currently violated (see `ARCH-MAP.md`'s xmllib entry for the current file count) — recorded here so the
drift is visible rather than assumed away.

Enforced by: none (docs-only)
