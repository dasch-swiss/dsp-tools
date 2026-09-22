---
status: accepted
date: 2026-09-22
---

# Split xmlupload into upload-files, ingest-files, ingest-xmlupload, and resume-xmlupload

Uploading raw files, server-side ingest processing, and resource creation can each be slow or fail
independently. Splitting them into separate commands lets a user resume just the failed phase instead of
restarting the entire upload, rather than treating the whole pipeline as one atomic `xmlupload` run.

Enforced by: none (docs-only)
