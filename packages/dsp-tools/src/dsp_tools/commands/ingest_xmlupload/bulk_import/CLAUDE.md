# CLAUDE.md for the bulk data import of `ingest-xmlupload`

`ingest-xmlupload` sends the whole project to the bulk data import of DSP-API as one JSON-LD file.
The decision and its consequences are in ADR 0006 (`docs/adr/0006-ingest-xmlupload-uses-bulk-data-import.md`
at the repository root).

- `mint_iris.py` is the only place that creates resource and value IRIs.
- `write_payload.py` is the only writer of the payload file. It streams one resource at a time.
- `payload_files.py` owns the folder `~/.dsp-tools/data-imports/<server>/` and the file names in it.
  Other modules take a `PayloadFiles` and do not build paths themselves.
- `run_import.py` owns the task lifecycle: post, poll, and the handling of `completed` and `failed`.
  `../delete_data_import.py` deletes a task that a run left on the server.
- There is no resume and no incremental import. A new run creates new IRIs.
