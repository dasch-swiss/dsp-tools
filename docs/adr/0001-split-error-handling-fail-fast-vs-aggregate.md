---
status: accepted
date: 2026-09-22
---

# Split error handling into fail-fast Group A and aggregate-all Group B

Commands that run in a controlled environment before production use (`create`, `get`, `xmlupload`,
`upload-files`, `ingest-files`, `ingest-xmlupload`, `resume-xmlupload`) may fail fast with a full traceback,
since a developer is present to interpret it. Commands that run directly against a user's own files
(the `excel2json` family, `validate-data`, `xmllib`, `update-legal`, `id2iri`, `start-stack`/`stop-stack`)
must instead aggregate every problem into one user-friendly report, since the person running them typically
cannot interpret a raw traceback.

Enforced by: none (docs-only) — stated in `docs/developers/architecture/error-handling.md`.
