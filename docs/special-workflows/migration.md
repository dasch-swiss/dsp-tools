# Project Migration

!!! Attention

    Only DaSCH system administrators are allowed to migrate projects.

A migration moves a full project — ontology, data, and all multimedia files — from one DSP server to another.

Please note, that the entire workflow may take up to 6 hours for large projects.

At the moment only projects smaller than 200 GB are supported.
If your project is larger, then the export will fail and you will get notified.
If that is the case, please contact Infrastructure and DaSCH Engineering to help migrate it with another workflow.

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
  - user: admin@example.com
  - password: secret
target-server:
  - server: https://target.dasch.swiss
  - user: admin@example.com
  - password: secret
keep-local-export: false
export-savepath: ~/.dsp-tools/migration/
```

| Field               | Description                                                                                    |
|---------------------|------------------------------------------------------------------------------------------------|
| `shortcode`         | shortcode of the project (e.g. `0806`)                                                         |
| `source-server`     | Credentials for the server to migrate **from**                                                 |
| `target-server`     | Credentials for the server to migrate **to**                                                   |
| `keep-local-export` | If `true`, the local export ZIP is not deleted after migration. These files can be very large. |
| `export-savepath`   | Directory where the export ZIP is saved locally. We recommend keeping the default.             |

## Step 2: Run the Migration

### All-In-One

To run the entire migration in one step:

```bash
dsp-tools migration complete migration-0806.yaml
```

This exports the project from the source server, downloads it locally,
imports it into the target server, and cleans up afterwards.

### Step by Step

Use the individual subcommands if you want to keep the local export, for example to re-import it later without
re-exporting.

**Export from the source server:**

```bash
dsp-tools migration export migration-0806.yaml
```

**Import into the target server:**

```bash
dsp-tools migration import migration-0806.yaml
```

**Clean up leftovers on both servers and locally:**

```bash
dsp-tools migration clean-up migration-0806.yaml
```

## If Something Goes Wrong

If the migration fails, contact the DaSCH Engineering Team for help to diagnose the problem.
