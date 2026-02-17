# `project-migration` Command

The command `project-migration` is an all-in-one command that:

- exports data from a server (CLI `migration-export`)
- downloads the export (CLI `migration-download`)
- uploads the import (CLI `migration-import`)
- contains clean up steps (CLI `migration-clean-up`)

The functionality for the CLI command for the clean-up
is only intended to be used manually if an export or import failed.

## Process

CLI: `project-migration`

- `migration-export`

    - export call ok
    - inform user
    - check status
        - in_progress -> check status
        - failed -> stop inform user
        - completed -> continue
    - inform user
    - Download export
    - inform user

- `migration-clean-up --export`

- `migration-import`

    - import call ok
    - inform user
    - check status
        - in_progress -> check status
        - failed -> stop inform user
        - completed -> continue
    - inform user

- `migration-clean-up --import`


