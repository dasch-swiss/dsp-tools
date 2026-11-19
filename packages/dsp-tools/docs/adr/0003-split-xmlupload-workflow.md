---
status: accepted
date: 2024-07-22
---

# Offer a multi-step workflow as an alternative to xmlupload

In July 2024, dsp-tools added a second way to do an xmlupload, for big uploads. This workflow has 3 separate
steps: `upload-files` uploads the multimedia files without processing, `ingest-files` starts the server-side
ingest and retrieves the mapping CSV, and `ingest-xmlupload` creates the resources with that mapping.
The user runs each step separately, so a slow or failed step does not block the other steps.

`xmlupload` stays as the one-step way to do the same upload. There is no plan to split or deprecate it.

Source: [PR #1067](https://github.com/dasch-swiss/dsp-tools/pull/1067). The PR added `upload-files` and
`ingest-files`, and combined them with the existing `ingest-xmlupload` command.

Enforced by: none (docs-only)
