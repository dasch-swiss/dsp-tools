# Map: `dsp-vre-lib` Domains in `dsp-tools`

This document shows which `dsp-tools` command needs which `dsp-vre-lib` domain.
The domains and capabilities are in the [ADR for `dsp-vre-lib`](../../packages/dsp-vre-lib/docs/adr/0001-public-interface.md).
The column "Client modules today" names the modules in `src/dsp_tools/clients/` that `dsp-vre-lib` replaces.

## Commands with Server Interaction

All commands below need the domain Connection (`authentication_client`, `connection`).
The table does not repeat it.

| Command                                            | Domain       | Capability                                       | Client modules today                                                          |
|----------------------------------------------------|--------------|--------------------------------------------------|-------------------------------------------------------------------------------|
| `create`                                           | Projects     | Project with metadata, legal info                | `project_client`, `legal_info_client`                                         |
|                                                    | Permissions  | Users, project roles, groups                     | `group_user_clients`, `permissions_client`                                    |
|                                                    | Data model   | Ontologies, classes, properties, cardinalities   | `ontology_clients`, `ontology_create_client_live`, `ontology_get_client_live` |
|                                                    | Vocabularies | Lists and nodes                                  | `list_client`                                                                 |
| `get`                                              | Projects     | Read project with metadata                       | `connection` (legacy models)                                                  |
|                                                    | Permissions  | Read users, project roles, groups                | `connection` (legacy models), `permissions_client`                            |
|                                                    | Data model   | Read ontologies                                  | `connection` (legacy models)                                                  |
|                                                    | Vocabularies | Read lists                                       | `connection` (legacy models)                                                  |
| `xmlupload`, `resume-xmlupload`                    | Data         | Create data, continuation state                  | `resource_client`, `value_client`, `ingest`                                   |
|                                                    | Projects     | Read project, read legal info                    | `project_client`, `legal_info_client`                                         |
|                                                    | Vocabularies | Read lists                                       | `list_client`                                                                 |
| `upload-files`, `ingest-files`, `ingest-xmlupload` | Data         | Create data (bulk ingest strategy)               | `bulk_ingest_client`, `ingest`                                                |
|                                                    | Projects     | Read project, read legal info                    | `project_client`, `legal_info_client`                                         |
|                                                    | Vocabularies | Read lists                                       | `list_client`                                                                 |
| `validate-data`                                    | Data         | Validate data                                    | `metadata_client`                                                             |
|                                                    | Data model   | Read ontologies                                  | `ontology_clients`, `ontology_get_client_live`                                |
|                                                    | Projects     | Read project, read legal info                    | `project_client`, `legal_info_client`                                         |
|                                                    | Vocabularies | Read lists                                       | `list_client`                                                                 |
| `mapping config`, `mapping update`                 | Data model   | External mappings                                | `mapping_client`, `ontology_get_client_live`                                  |
|                                                    | Projects     | Read project                                     | `project_client`                                                              |
| `migration`                                        | Projects     | Export and import of a project                   | `migration_clients`, `project_client`                                         |

Notes:

- With `dsp-vre-lib`, the four commands `xmlupload`, `upload-files`, `ingest-files` and `ingest-xmlupload`
  call one capability: create data. `dsp-vre-lib` selects the ingest strategy.
- Each command that changes the server needs the Permissions capability
  "operations that the current user can do", to check the rights before it starts.

## Commands without Server Interaction

These commands do not use `dsp-vre-lib`:

- `excel2json`, `excel2lists`, `excel2resources`, `excel2properties`
- `old-excel2json`, `old-excel2lists`
- `excel2xml` and `xmllib`
- `id2iri`
- `update-legal`
- `start-stack`, `stop-stack`

## Worked Example: `dsp-tools create`

`dsp-tools create` reads the JSON project file and converts it into `dsp-vre-lib` dataclasses.
It then checks that the current user can create a project (Permissions).
After that, it calls `set_up_project` one time.

`set_up_project` does these steps in this order:

1. Create the project with its metadata and legal info (Projects).
2. Create the vocabularies (Vocabularies).
3. Create the groups, the users and their project roles (Permissions).
4. Create the data models with classes, properties, cardinalities and their visibility (Data model).

The call has one progress stream and one result.
The result reports the created items, the skipped items that exist, and the failures (principles 6 and 7).
The progress mechanism is an open decision in
[Progress, Reporting and Continuation](../../packages/dsp-vre-lib/docs/adr/0001-public-interface.md#progress-reporting-and-continuation).
