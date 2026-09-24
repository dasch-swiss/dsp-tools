---
status: accepted
date: 2026-02
---

# Split error handling into fail-fast Group A and aggregate-all Group B

The two groups differ in the workflow in which users run the commands.

Group A commands (`create`, `get`, `xmlupload`, `upload-files`, `ingest-files`, `ingest-xmlupload`,
`resume-xmlupload`) run first on localhost or on a test server, before the run goes to production.
If something fails there, the user can consult the developers or infra before the production run.
Thus, these commands may fail fast with a full traceback.

Group B commands (the `excel2json` family, `validate-data`, `xmllib`, `update-legal`, `id2iri`,
`start-stack`/`stop-stack`) are part of the user's own daily workflow. Their users expect a higher
user-friendliness, because they do not want to interrupt their workflow to consult a developer.
Thus, these commands aggregate every problem into one user-friendly report, which lets the user fix all
problems without help.

Enforced by: none (docs-only) — stated in `docs/developers/architecture/error-handling.md`.
