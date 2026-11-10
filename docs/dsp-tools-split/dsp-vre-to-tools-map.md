# Map: `dsp-vre` Domains in `dsp-tools`

This document shows which `dsp-tools` command needs which `dsp-vre` domain.
The domains and capabilities are in the [ADR for `dsp-vre`](ADR-dsp-vre.md).
The column "Client modules today" names the modules in `src/dsp_tools/clients/` that `dsp-vre` replaces.

## Commands with Server Interaction

All commands below need the domain Connection (`authentication_client`, `connection`).
The table does not repeat it.

| Command                                            | Domain       | Capability                                      | Client modules today                                                          |
|----------------------------------------------------|--------------|-------------------------------------------------|-------------------------------------------------------------------------------|
| `create`                                           | Projects     | Project with metadata, legal info               | `project_client`, `legal_info_client`                                         |
|                                                    | Access       | Users, groups, memberships, default permissions | `group_user_clients`, `permissions_client`                                    |
|                                                    | Data model   | Ontologies, classes, properties, cardinalities  | `ontology_clients`, `ontology_create_client_live`, `ontology_get_client_live` |
|                                                    | Vocabularies | Lists and nodes                                 | `list_client`                                                                 |
| `get`                                              | Projects     | Read project with metadata                      | `connection` (legacy models)                                                  |
|                                                    | Access       | Read users, groups, default permissions         | `connection` (legacy models), `permissions_client`                            |
|                                                    | Data model   | Read ontologies                                 | `connection` (legacy models)                                                  |
|                                                    | Vocabularies | Read lists                                      | `connection` (legacy models)                                                  |
| `xmlupload`, `resume-xmlupload`                    | Data         | Create data, continuation state                 | `resource_client`, `value_client`, `ingest`                                   |
|                                                    | Projects     | Read project, read legal info                   | `project_client`, `legal_info_client`                                         |
|                                                    | Vocabularies | Read lists                                      | `list_client`                                                                 |
| `upload-files`, `ingest-files`, `ingest-xmlupload` | Data         | Create data (bulk ingest strategy)              | `bulk_ingest_client`, `ingest`                                                |
|                                                    | Projects     | Read project, read legal info                   | `project_client`, `legal_info_client`                                         |
|                                                    | Vocabularies | Read lists                                      | `list_client`                                                                 |
| `validate-data`                                    | Data         | Validate data                                   | `metadata_client`                                                             |
|                                                    | Data model   | Read ontologies                                 | `ontology_clients`, `ontology_get_client_live`                                |
|                                                    | Projects     | Read project, read legal info                   | `project_client`, `legal_info_client`                                         |
|                                                    | Vocabularies | Read lists                                      | `list_client`                                                                 |
| `mapping config`, `mapping update`                 | Data model   | External mappings                               | `mapping_client`, `ontology_get_client_live`                                  |
|                                                    | Projects     | Read project                                    | `project_client`                                                              |
| `migration`                                        | Migration    | Export and import of a project                  | `migration_clients`, `project_client`                                         |

Notes:

- With `dsp-vre`, the four commands `xmlupload`, `upload-files`, `ingest-files` and `ingest-xmlupload`
  call one capability: create data. `dsp-vre` selects the ingest strategy.
- Each command that changes the server needs the Access capability
  "operations that the current user can do", to check the rights before it starts.

## Commands without Server Interaction

These commands do not use `dsp-vre`:

- `excel2json`, `excel2lists`, `excel2resources`, `excel2properties`
- `old-excel2json`, `old-excel2lists`
- `excel2xml` and `xmllib`
- `id2iri`
- `update-legal`
- `start-stack`, `stop-stack`

## Worked Example: `dsp-tools create`

`dsp-tools create` is the use case for the open decision in
[Progress & Reporting](ADR-dsp-vre.md#progress--reporting).
The command reads the JSON project file, converts it into `dsp-vre` dataclasses, and then does these steps:

1. Connect to the server (Connection).
2. Check that the current user can create a project (Access).
3. Create the project with its metadata and legal info (Projects).
4. Create the lists (Vocabularies).
5. Create the groups (Access).
6. Create the users and their memberships (Access).
7. Create the ontologies with classes, properties and cardinalities (Data model).
8. Create the default permissions of the project (Access).

Each step returns created items and failures (principle 6).
The progress options get compared on these questions:

- How does `dsp-tools` show one progress bar across the steps?
- How does `dsp-tools` write the failures of each step to its log file?
- What does the user do after an interruption in step 7?
