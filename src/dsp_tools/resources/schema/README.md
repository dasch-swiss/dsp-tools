# Copy of the Schema Files at the Old URL Path

This folder holds a copy of the schema files of `dsp-tools`.
The source is `packages/dsp-tools/src/dsp_tools/resources/schema/`.

XML data files and JSON project files that were made before the uv workspace
refer to the schema files with URLs to this path, for example
`https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/data.xsd`.
The copy keeps these URLs valid.

- Do not edit the files in this folder. Edit the source, then run `just sync-schema-copy`.
- `just check-schema-copy` (in CI: `lint-code.yml`) fails if the copy is not equal to the source.
- This folder is deprecated. It will be removed after a deprecation period.
