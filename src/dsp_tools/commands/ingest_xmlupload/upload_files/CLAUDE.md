# upload-files — Quick Reference

Implements `dsp-tools upload-files`: upload the multimedia files referenced in an XML data file to the
DSP ingest server. No processing or ingesting — upload only. It is step 1 of the split xmlupload
workflow (`upload-files` → `ingest-files` → `ingest-xmlupload`).

## Entry point

`upload_files(xml_file, creds, imgdir)` in `upload_files.py`. Flow:

1. `parse_and_clean_xml_file` (utils) → cleaned, XSD-validated root.
2. `get_parsed_resources(root, creds.server)` (utils) → `list[ParsedResource]`.
3. `_get_validated_paths(resources)` → the set of real bitstream file paths.
4. `check_files` (`filechecker.py`) → existence and extension check.
5. Upload each path via `BulkIngestClient.upload_file`, then aggregate failures.

## Files

- `upload_files.py` — command entry point plus the private path extraction.
- `filechecker.py` — `check_files(paths)`: local existence and supported-extension check.
- `input_error.py` — `FileProblems`: pre-upload local validation errors.
- `upload_failures.py` — `UploadFailure` / `UploadFailures`: per-file failures from the ingest server.

## Conventions

- The bitstream contract lives in `get_parsed_resources` (utils), not here. Do not re-parse
  `<bitstream>` with xpath. Extract file paths from `ParsedResource` and filter by type
  (`ParsedFileBitstream`). Placeholder and `<iiif-uri>` values are then excluded by type.
  A duplicated xpath parser caused the placeholder crash in DEV-7255.
- Two-level design: `upload_files` takes the XML file and runs standalone. `_get_validated_paths`
  takes a `list[ParsedResource]` and returns the real bitstream file paths.
- Two distinct error types: `FileProblems` for local problems before upload (missing or unsupported
  files). `UploadFailures` for files the ingest server rejects. Both expose `execute_error_protocol()`,
  which prints the list or writes a CSV past `maximum_prints`.
- `creds.server` is the DSP-API URL (passed to `get_parsed_resources`). `creds.dsp_ingest_url` is the
  ingest server (passed to `BulkIngestClient`).

## Tests

Unit: `test/unittests/commands/ingest_xmlupload/`. E2e: `test/e2e/commands/ingest_xmlupload/`.
