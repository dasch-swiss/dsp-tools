[![DSP-TOOLS version on PyPI](https://img.shields.io/pypi/v/dsp-tools.svg)](https://pypi.org/project/dsp-tools/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/dsp-tools.svg)](https://pypi.org/project/dsp-tools/)
[![License](https://img.shields.io/pypi/l/dsp-tools.svg)](https://pypi.org/project/dsp-tools/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![mypy](https://img.shields.io/badge/mypy-blue)](https://github.com/python/mypy)

# DSP-TOOLS Documentation

## Installing `dsp-tools`

To install the latest version, run:

```bash
pip3 install dsp-tools
```

To update to the latest version run:

```bash
pip3 install --upgrade dsp-tools
```

> 🚨 If your Python version is older than ours,
> pip will silently install an outdated version of DSP-TOOLS.  
> DSP-TOOLS requires one of these Python versions:
> [![](https://img.shields.io/pypi/pyversions/dsp-tools.svg)](https://pypi.org/project/dsp-tools/)  
> The most recent version of DSP-TOOLS is
> [![](https://img.shields.io/pypi/v/dsp-tools.svg)](https://pypi.org/project/dsp-tools/)



The `dsp-tools` package provides you with functionalities in the command line
to interact with the [DSP-API](https://github.com/dasch-swiss/dsp-api), both remote and locally.
Additionally, it contains the `xmllib` which helps you construct the XML file required for a mass upload.

## Where To Start?

`dsp-tools` provides you with the following core functionalities.

- **Running a Local Stack:** If you want to run your own DSP stack locally, take a look [here](./local-stack.md).
- **Data Modelling:** There are several ways to create a data model with `dsp-tools`
    - Take a look at the technical specification for the [JSON file](./data-model/json-project/overview.md).
    - Or take a look at our tool to [convert Excel files into the JSON format](./data-model/excel2json.md).
    - You can create a data model on the DSP-APP. To re-use that data model on another server
      you can use the CLI command described [here](./data-model/data-model-cli.md#get).
- **Data for Mass-Upload:**
    - If you want to create the XML file required for a mass-upload onto DSP, take a look at the [
      `xmllib`](./xmllib-docs/overview.md).
    - You can find an in-depth explanation of our XML file format [here](./data-file/xml-data-file.md).
      Please note, that we recommend to use the `xmllib` library to create the file
      as we will ensure interoperability between the DSP-API requirements and your input.
    - If you want to validate and upload your XML file take a look [here](./data-file/data-file-commands.md).
      Please note, that only DaSCH employees are permitted to upload data on a production server.

## List of CLI Commands

The following CLI Commands are available, listed here in alphabetical order.

### `create`

Create a project on the server using the project definition JSON file.

Click [here](./data-model/data-model-cli.md#create) for more information.

### `excel2json`

Create the project definition JSON file using pre-defined Excel files.

The following commands can be used to only create a section of the project definition.

#### `excel2lists`

Create the list section of the project JSON file.

#### `excel2properties`

Create the properties section within one ontology of the JSON file.

#### `excel2resources`

Create the resource section within one ontology of the JSON file.

### `get`

Get the complete project definition JSON from a server.

### `id2iri`

This command replaces internal IDs of an XML file (`<resptr>` tags and salsah-links inside `<text>` tags)
by IRIs provided in a mapping file.

### `ingest-files`

Part of the special xmlupload workflow that uploads the file before creating the data.

This command kicks off the ingest process on the server, and waits until it has completed.
Then, it saves the mapping CSV in the current working directory.

### `ingest-xmlupload`

Part of the special xmlupload workflow that uploads the file before creating the data.

This command creates all resources defined in an XML file on a DSP server.
Pre-requisite is that the files are already uploaded on the server.

### `migration`

Used to migrate one project from one server to another.
This process can be invoked by the following sub-commands.

#### `migration config`

Create a config YAML file, that contains all the necessary information for a migration.
This step is mandatory for all other commands.

#### `migration complete`

Execute a complete migration from one server to another.

#### `migration export`

Download the migration information from the source server.

#### `migration import`

Import the previously downloaded export to another server.

#### `migration clean-up`

Clean-up locally created files and references to the migration on the servers.

### `old-excel2json`

Create the project definition JSON file using the old format of pre-defined Excel files.

#### `old-excel2lists`

Create the list section of the project JSON file using the old format of the pre-defined Excel files.

### `resume-xmlupload`

Resume a previously interrupted xmlupload.

### `start-stack`

Start a local stack of the DaSCH Service Platform, this requires the installation of Docker Desktop.

### `stop-stack`

Stop the local stack of the DaSCH Service Platform.

### `update-legal`

If an XML file contains multimedia files, they must be accompanied by legal metadata.
Older XML files may contain legal metadata as text properties.
This document guides you through the process of updating them to the new format.

### `upload-files`

Part of the special xmlupload workflow that uploads the file before creating the data.

This command uploads all files referenced in the `<bitstream>` tags of an XML file to a server
(without any processing/ingesting).

### `validate-data`

Execute a complete Schema validation of the data XML. This requires that the project exists locally or on a server.

### `xmlupload`

Execute an upload of the data XML. This requires that the project exists locally or on a server.


