# Project Migration

!!! Attention

    Only DaSCH system administrators are allowed to migrate projects.

A migration moves a full project — ontology, data, and all multimedia files — from one DSP server to another.

Please note that the entire workflow may take several hours for large projects.

At the moment only projects smaller than 200 GB are supported.
If your project is larger, then the export will fail and you will get notified.
If that is the case, please contact the DaSCH Infrastructure and/or Engineering teams to find another solution.

It is only possible to do 1 export on a server (both for export and import).
If there are conflicts, dsp-tools will stop and print a message.

## Step 1: Create a Config File

Run the following command to generate a config file for your project:

```bash
dsp-tools migration config --project-shortcode 0806
```

This creates a file called `migration-0806.yaml` in your current directory.

### Fill In the Config File

Open the generated file and fill in the server details:

```yaml
shortcode: "0806"
source-server:
  - server: https://source.dasch.swiss
  - user: system-admin@example.com
  - password: secret
target-server:
  - server: https://target.dasch.swiss
  - user: system-admin@example.com
  - password: secret
keep-local-export: false
export-savepath: ~/.dsp-tools/migration/
```

| Field               | Description                                                                                       |
|---------------------|---------------------------------------------------------------------------------------------------|
| `shortcode`         | Shortcode of the project (e.g. `0806`)                                                            |
| `source-server`     | Credentials for the server to migrate **from**                                                    |
| `target-server`     | Credentials for the server to migrate **to**                                                      |
| `keep-local-export` | If `true`, the local export files are not deleted after migration. These files can be very large. |
| `export-savepath`   | Directory where the export files are saved locally. We recommend keeping the default.             |

## Local Export Files

During the migration, two files are created locally in the `export-savepath` directory.

Unless you specified to keep the files after the import, both of these will be removed.

- `export-0806.zip` — the project export downloaded from the source server
- `migration-references-0806.json` — internal reference data used across migration steps

!!! Warning

    Do not rename, move, or modify these files.
    The migration commands rely on fixed filenames and will fail if the files have been changed.

## Step 2: Run the Migration

### All-In-One

To run the entire migration in one step:

```bash
dsp-tools migration complete migration-0806.yaml
```

This exports the project from the source server, downloads it locally,
imports it into the target server, and cleans up afterwards.

### Step by Step

Use the individual subcommands if you need more control, for example to import a project into
multiple target servers, or to keep the local export for archiving.

**Export from the source server and download locally:**

```bash
dsp-tools migration export migration-0806.yaml
```

**Import into the target server:**

```bash
dsp-tools migration import migration-0806.yaml
```

You can run the import command multiple times with different `target-server` credentials
to import the same export into multiple servers.

**Clean up leftovers on both servers and locally:**

```bash
dsp-tools migration clean-up migration-0806.yaml
```

Run this once you are done with all imports.
It removes the temporary export from the source server, the temporary import from the target server,
and the local export files (unless `keep-local-export` is set to `true`).

## If Something Goes Wrong

If the export or import fails, contact the DaSCH Engineering Team for help to diagnose the problem.
