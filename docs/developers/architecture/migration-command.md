# `migration` Command

## Overview

The command `migration` is an all-in-one command that:

- Prepares the zip file on the source server (CLI `migration export`)
- Downloads the zip file from the source server (CLI `migration download`)
- Uploads the zip file on the target server(CLI `migration import`)
- Contains clean up steps on both servers (CLI `migration clean-up`)

The functionality for the CLI command for the clean-up
is only intended to be used manually if the preparation of the zip file, download or import failed.

To specify servers, users, etc. this command will take a config file
which can be created with the command `migration config`.

## Limitations

- API restriction maximum 2h for preparation, download and import (each)
- Maximum 200 GB size limitation on assets and data
- Currently only able to migrate with assets

## Process

```mermaid
---
title: CLI migration
---
stateDiagram-v2
    state "CLI: migration export" as export
    state "HTTP: Export" as exportCall
    state "HTTP: Check Status" as exportStatus
    state "Export on Server" as exportComplete
    state "CLI: migration download" as download
    state "HTTP: Download from Server" as downloadExport
    state "Download saved on Disk" as downloadComplete
    state "CLI: migration import" as import
    state "HTTP: Import" as importCall
    state "HTTP: Check Status" as importStatus
    state "Import Complete" as importComplete
    state "CLI: migration clean-up" as cleanup
    state "HTTP: Export Server<br>Remove Export ID" as cleanupExport
    state "HTTP: Import Server<br>Remove Export ID" as cleanupImport
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
    }
```

## Cleanup on Failure

**Export Failure:**

- None

**Download Failure:**

- Delete partial download file
- No server-side cleanup (can retry manually)

**Import Failure:**

- Local zip file remains (for manual retry)
- No server-side cleanup (for potential debugging)

**Manual Cleanup:**

- Use `migration clean-up` command
- Specify `--export` or `--import`
