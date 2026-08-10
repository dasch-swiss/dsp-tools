[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# CLI-Commands

## `create`

This command reads a JSON project definition (containing one or more data models)
and creates it on a DSP server.

```bash
dsp-tools create [options] project_definition.json
```

The most frequently used options are:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API

To see all possible options, type `dsp-tools create --help`.

### The `--exit-if-exists` flag

By default, if a project with the same shortcode already exists on the server,
`create` continues and adds the definitions from the JSON file to the existing project.
Pass `--exit-if-exists` to abort instead, as soon as an existing project is detected,
without uploading anything.

This is useful in automated pipelines that must not modify an already-existing project.
Depending on the outcome, the command exits with one of these codes:

- `0`: the project did not exist yet and was created.
- `3`: the project already existed, so nothing was uploaded.
- `1`: the command failed for another reason.

A calling script can check for exit code `3` to skip subsequent steps (such as a data upload) gracefully.

The defaults are intended for local testing:

```bash
dsp-tools create project_definition.json
```

This will create the project defined in `project_definition.json` on `localhost` for local viewing.

In order to create the same project
on the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools create -s https://api.dasch.swiss -u 'your@email.com' -p 'password' project_definition.json
```

The expected JSON format is [documented here](./json-project/overview.md).

## `get`

This command retrieves a project with its data model(s) from a DSP server
and writes it into a JSON file.
This JSON file can then be used
to create the same project on another DSP server.

```bash
dsp-tools get [options] project_definition.json
```

The most frequently used options are:

- `-P` | `--project` (mandatory): shortcode, shortname or IRI of the project
- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API

To see all possible options, type `dsp-tools get --help`.

The defaults are intended for local testing:

```bash
dsp-tools get -P my_project project_definition.json
```

will get `my_project` from `localhost`.

In order to get a project from the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools get -s https://api.dasch.swiss -u 'your@email.com' -p 'password' -P my_project project_definition.json
```

It is possible to get a project from a DSP server without giving credentials.
But in this case, the resulting JSON file won't have a "users" section.

The expected JSON format is [documented here](./json-project/overview.md).

## `mapping`

The `mapping` command links DSP ontology classes and properties to IRIs from external ontologies
(e.g. schema.org, CIDOC-CRM), enabling interoperability with other knowledge systems,
through definitions from an Excel file.
It has two subcommands: `mapping config` generates a configuration template,
and `mapping update` replaces the external mappings stored on a DSP server with the ones from an Excel file
(see [Replace semantics](#mapping-update)).

<!-- markdownlint-disable MD036 -->

### Excel file format

The Excel file must contain exactly three sheets: `prefix`, `classes`, and `properties`.

**`prefix` sheet**

Declares the namespace prefixes used in the `classes` and `properties` sheets.
Required columns: `prefix`, `link`.

| prefix | link                                  |
|--------|---------------------------------------|
| schema | `https://schema.org/`                 |
| crm    | `http://www.cidoc-crm.org/cidoc-crm/` |

**`classes` sheet**

Maps DSP class names to external ontology IRIs.
Required columns: `class`, `mapping`.

| class    | mapping                          |
|----------|----------------------------------|
| `Book`   | `schema:Book`                    |
| `Person` | `schema:Person ; crm:E21_Person` |

**`properties` sheet**

Maps DSP property names to external ontology IRIs.
Required columns: `property`, `mapping`.

| property     | mapping                                   |
|--------------|-------------------------------------------|
| `hasTitle`   | `schema:name`                             |
| `hasCreator` | `schema:creator ; crm:P14_carried_out_by` |

**Syntax in the `mapping` column**

- **Prefixed form**: `prefix:localname` (e.g. `schema:Book`) — expanded using the `prefix` sheet.
- **Full IRI**: `https://schema.org/Book` — passed through unchanged.
- **Multiple IRIs**: separate with semicolons (`;`)

### `mapping config`

Generates a YAML configuration template for the `mapping update` command.

```bash
dsp-tools mapping config [--project-shortcode SHORTCODE] [--ontology NAME]
```

The available options are:

- `-P` | `--project-shortcode` (optional): 4-digit hexadecimal project shortcode.
  If not provided, you will be prompted to enter it (in a non-interactive session, the command
  fails with an error asking you to pass `--project-shortcode` instead).
- `--ontology` (optional): name of the ontology to map.
  If not provided, you will be prompted to enter it (in a non-interactive session, the command
  fails with an error asking you to pass `--ontology` instead).

The command creates a file named `{shortcode}-{ontology}-mapping.yaml` in the current working directory.

**Config file format**

```yaml
---
shortcode: "0XXX"
ontology: "my-ontology"
excel-file: path/to/mappings.xlsx
server: http://0.0.0.0:3333
user: root@example.com
password: test
```

All fields are required.
The `server`, `user`, and `password` fields follow the same conventions as other DSP-TOOLS commands.

### `mapping update`

Reads an Excel file and replaces the external mappings of the ontology on a DSP server with the ones it defines.

```bash
dsp-tools mapping update 0XXX-my-onto-mapping.yaml
```

The available arguments are:

- `config_file` (mandatory): path to the YAML configuration file, created with `mapping config`.

**Replace semantics**

The Excel file is the single source of truth for the external mappings of the ontology named in the config file:
after the command runs, the ontology's external mappings match the Excel file exactly, nothing more and nothing
less.

- **Every class and property of the ontology is affected**, including those the Excel file does not mention at
  all. A class that was mapped in an earlier run, but is absent from the Excel file now, loses its mappings.
- Only the ontology named in the config file is affected. Other ontologies of the same project are untouched.
- A mapping listed in both the old and the new state is left as is. Running the command again with an unchanged
  Excel file changes nothing on the server.

The following super-classes and super-properties are always kept, no matter what the Excel file says:

- DSP's own ones, e.g. `knora-api:Resource` and `knora-api:hasValue`, present on every DSP server.
- Any super-class or super-property that comes from one of your project's own ontologies — whether from the
  ontology you are mapping or from another ontology in the same project. Inheriting from your own classes and
  properties is normal DSP modeling, not an external mapping, so it is never affected.

Before changing anything, the command prints how many mappings will be removed and which classes and properties
are affected.

The command is re-runnable: if it fails, fix the reported problems and run it again with the same config file.
If a class or property loses its old mappings but does not receive its new ones because of a failure, it is left
without external mappings until the next successful run.

If someone else edits the same ontology's mappings while the command is running, the result can be inconsistent:
a removal may not take effect, or a mapping added by someone else in the meantime may unexpectedly survive.

<!-- markdownlint-enable MD036 -->
