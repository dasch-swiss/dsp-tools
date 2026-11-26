---
status: accepted
date: 2026-11-24
---

# ingest-xmlupload sends one bulk data import

[ADR 0003](0003-split-xmlupload-workflow.md) split an xmlupload into `upload-files`, `ingest-files` and
`ingest-xmlupload`. That `ingest-xmlupload` created the resources one request at a time, like `xmlupload`.
As of November 2026 (DSP-API v41.0.0), DSP-API has a bulk data import: one JSON-LD payload creates all
resources, values and files of a project as one task
([API docs](https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v3/project-data-import/)).

`ingest-xmlupload` replaces the one-request-at-a-time upload completely:

- DSP-TOOLS creates the IRIs of all resources and values before it sends the data. A preset IRI or ARK is kept
  and must belong to the project. The IRI lookup is complete before the payload is written, so no stash is needed.
- DSP-TOOLS streams the whole project into one JSON-LD file, and sends this file as one bulk data import.
- DSP-TOOLS follows the task until it ends. If the task completes, DSP-TOOLS writes the mapping of internal IDs
  to IRIs and removes its files. If the task fails, DSP-TOOLS writes the error message to a file and deletes the
  task. If the command is interrupted or loses the connection, the task stays on the server, and
  `delete-data-import` removes it.
- `ingest-xmlupload` requires `--on-behalf-of-user`. Only a system admin can start a bulk data import.
  Without an on-behalf-of user, DSP-API attaches all data (`attachedToUser`) to that system admin, a DaSCH account,
  and not to a person of the project. The on-behalf-of user must not be a system admin: DSP-API treats a system admin
  as a project admin when it resolves the default object access permissions, so the project-admin permissions
  would win, and the data would again belong to a DaSCH account. DSP-API rejects such a user
  ([API docs](https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v3/project-data-import/)).
- `ingest-xmlupload` imports from `commands/xmlupload/` (preparation, graph building, copyright holders).
  This is accepted: `ingest-xmlupload` is the bulk variant of `xmlupload`, and both must produce the same data.

Consequences:

- Only system admins can run `ingest-xmlupload` and `delete-data-import`. The data belongs to the user given
  with `--on-behalf-of-user`.
- The project must hold no data except list nodes. There is no incremental upload.
- There is no resume: `resume-xmlupload` resumes only `xmlupload`. After a failure, the user runs the command
  again.

Enforced by: none (docs-only)
