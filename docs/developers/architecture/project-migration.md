# `project-migration` Command

## Overview

The command `project-migration` is an all-in-one command that:

- exports data from a server (CLI `migration-export`)
- downloads the export (CLI `migration-download`)
- uploads the import (CLI `migration-import`)
- contains clean up steps (CLI `migration-clean-up`)

The functionality for the CLI command for the clean-up
is only intended to be used manually if an export or import failed.

## Limitations

- API restriction maximum 2h for export, download and import (each)
- Maximum 200 GB Assets and Data
- Currently only able to export with assets

## Process

```mermaid
---
title: Project Migration Command Flow
---
stateDiagram-v2

    state "CLI: migration-export" as export
    state "CLI: migration-download" as download
    state "CLI: migration-import" as import
    state "CLI: migration-clean-up" as cleanup

    [*] --> exportCall

    state export {
        exportCall --> exportStatus: check status
        exportStatus --> exportStatus: in_progress
        exportStatus --> exportFailed: failed
        exportStatus --> exportComplete: completed
        exportFailed --> [*]
    }

    exportComplete --> downloadExport

    state download {
        downloadExport --> downloadFailed: failed
        downloadExport --> downloadComplete: completed
        downloadFailed --> [*]
    }

    downloadComplete --> importCall

    state import {
        importCall --> importStatus: check status
        importStatus --> importStatus: in_progress
        importStatus --> importFailed: failed
        importStatus --> importComplete: completed
        importFailed --> [*]
    }

    importComplete --> cleanupExport

    state cleanup {
        cleanupExport --> cleanupImport: clean-up --export
        cleanupImport --> [*]: clean-up --import
    }

```

## Cleanup on Failure

**Export Failure:**

- none

**Download Failure:**

- Delete partial download file
- Server-side export remains (can retry manually)

**Import Failure:**

- Local export remains (for manual retry)
- Server-side cleanup remains (for potential debugging)

**Manual Cleanup:**

- Use `migration-clean-up` command
- Specify `--export` or `--import`
