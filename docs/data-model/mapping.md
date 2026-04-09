[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# `mapping`

The `mapping` command links DSP ontology classes and properties to IRIs from external ontologies
(e.g. schema.org, CIDOC-CRM), enabling interoperability with other knowledge systems.
It has two subcommands: `mapping config` generates a configuration template,
and `mapping add` uploads the mappings to a DSP server.

## `mapping config`

Generates a YAML configuration template for the `mapping add` command.

```bash
dsp-tools mapping config [--project-shortcode SHORTCODE] [--ontology NAME]
```

The available options are:

- `-P` | `--project-shortcode` (optional): 4-digit hexadecimal project shortcode.
  If not provided, you will be prompted to enter it.
- `--ontology` (optional): name of the ontology to map.
  If not provided, you will be prompted to enter it.

The command creates a file named `{shortcode}-{ontology}-mapping.yaml` in the current working directory.

### Config file format

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

## `mapping add`

Reads an Excel file and uploads its mappings to a DSP server.

```bash
dsp-tools mapping add config_file
```

The available arguments are:

- `config_file` (mandatory): path to the YAML configuration file, created with `mapping config`.

### Excel file format

The Excel file must contain exactly three sheets: `prefix`, `classes`, and `properties`.

#### `prefix` sheet

Declares the namespace prefixes used in the `classes` and `properties` sheets.
Required columns: `prefix`, `link`.

| prefix | link                                  |
|--------|---------------------------------------|
| schema | `https://schema.org/`                 |
| crm    | `http://www.cidoc-crm.org/cidoc-crm/` |

#### `classes` sheet

Maps DSP class names to external ontology IRIs.
Required columns: `class`, `mapping`.

| class    | mapping                          |
|----------|----------------------------------|
| `Book`   | `schema:Book`                    |
| `Person` | `schema:Person ; crm:E21_Person` |

#### `properties` sheet

Maps DSP property names to external ontology IRIs.
Required columns: `property`, `mapping`.

| property     | mapping                                   |
|--------------|-------------------------------------------|
| `hasTitle`   | `schema:name`                             |
| `hasCreator` | `schema:creator ; crm:P14_carried_out_by` |

#### Syntax in the `mapping` column

- **Prefixed form**: `prefix:localname` (e.g. `schema:Book`) — expanded using the `prefix` sheet.
- **Full IRI**: `https://schema.org/Book` — passed through unchanged.
- **Multiple IRIs**: separate with semicolons (`;`)
