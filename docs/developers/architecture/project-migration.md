# `project-migration` Command

## Overview

The command `project-migration` is an all-in-one command that:

- Exports data from a server (CLI `migration-export`)
- Downloads the export (CLI `migration-download`)
- Uploads the import (CLI `migration-import`)
- Contains clean up steps (CLI `migration-clean-up`)
- Removes export from local disk (if flag `--remove-local-export` is set)

The functionality for the CLI command for the clean-up
is only intended to be used manually if an export or import failed.

## Limitations

- API restriction maximum 2h for export, download and import (each)
- Maximum 200 GB size limitation on assets and data
- Currently only able to export with assets

## Process

```mermaid
---
title: CLI project-migration
---
stateDiagram-v2
    state "CLI: migration-export" as export
    state "HTTP: Export" as exportCall
    state "HTTP: Check Status" as exportStatus
    state "Export on Server" as exportComplete
    state "CLI: migration-download" as download
    state "HTTP: Download from Server" as downloadExport
    state "Download saved on Disk" as downloadComplete
    state "CLI: migration-import" as import
    state "HTTP: Import" as importCall
    state "HTTP: Check Status" as importStatus
    state "Import Complete" as importComplete
    state "CLI: migration-clean-up" as cleanup
    state "HTTP Export Server<br>Remove Export ID" as cleanupExport
    state "HTTP Import Server<br>Remove Export ID" as cleanupImport
    state "Remove Export Zip from Local Disk" as removeFromDisk
    state "Keep Export Zip on Local Disk" as keepOnDisk
    [*] --> exportCall

    state export {
        exportCall --> exportStatus: check status
        exportStatus --> [*]: failed
        exportStatus --> exportStatus: in_progress
        exportStatus --> exportComplete: completed
    }

    exportComplete --> downloadExport

    state download {
        downloadExport --> [*]: failed
        downloadExport --> downloadComplete: completed
    }

    downloadComplete --> importCall

    state import {
        importCall --> importStatus: check status
        importStatus --> [*]: failed
        importStatus --> importStatus: in_progress
        importStatus --> importComplete: completed
    }

    importComplete --> Continue

    state cleanup {
        Continue --> cleanupExport: clean-up --export
        cleanupExport --> cleanupImport: clean-up --import
        cleanupImport --> removeFromDisk: If flag --remove-local-export
        cleanupImport --> keepOnDisk: If flag --keep-local-export
    }
```

## Cleanup on Failure

**Export Failure:**

- None

**Download Failure:**

- Delete partial download file
- Server-side export remains (can retry manually)

**Import Failure:**

- Local export remains (for manual retry)
- Server-side cleanup remains (for potential debugging)

**Manual Cleanup:**

- Use `migration-clean-up` command
- Specify `--export` or `--import`
