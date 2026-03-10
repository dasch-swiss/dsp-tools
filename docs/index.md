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

| Command              | Description                                                                                                      | Documentation                                                     |
|----------------------|------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| `create`             | Create a project on a server from a JSON file<br>`dsp-tools create datamodel.json`                               | [→](./data-model/data-model-cli.md#create)                        |
| `excel2json`         | Create the project definition JSON from Excel files<br>`dsp-tools excel2json excelfolder project.json`           | [→](./data-model/excel2json.md#excel2json)                        |
| `excel2lists`        | Create the list section of the project JSON<br>`dsp-tools excel2lists excelfolder lists.json`                    | [→](./data-model/excel2json.md#excel2lists)                       |
| `excel2properties`   | Create the properties section of the JSON<br>`dsp-tools excel2properties properties.xlsx properties.json`        | [→](./data-model/excel2json.md#excel2properties)                  |
| `excel2resources`    | Create the resource section of the JSON<br>`dsp-tools excel2resources resources.xlsx resources.json`             | [→](./data-model/excel2json.md#excel2resources)                   |
| `get`                | Retrieve a project definition JSON from a server<br>`dsp-tools get -P 0XXX datamodel.json`                       | [→](./data-model/data-model-cli.md#get)                           |
| `id2iri`             | Replace internal IDs with IRIs in an XML file<br>`dsp-tools id2iri new_data.xml id2iri_mapping.json`             | [→](./data-file/data-file-commands.md#id2iri)                     |
| `ingest-files`       | Kick off the ingest process and save the mapping CSV<br>`dsp-tools ingest-files 0XXX`                            | [→](./special-workflows/workflow-xmlupload.md#ingest-files)       |
| `ingest-xmlupload`   | Create resources from XML after files are ingested<br>`dsp-tools ingest-xmlupload data.xml`                      | [→](./special-workflows/workflow-xmlupload.md#ingest-xmlupload)   |
| `migration`          | Migrate a project between servers<br>`dsp-tools migration`                                                       | [→](./special-workflows/migration.md)                             |
| `migration config`   | Create a migration config YAML file<br>`dsp-tools migration config -P 0XXX`                                      | [→](./special-workflows/migration.md#step-1-create-a-config-file) |
| `migration complete` | Execute a complete migration<br>`dsp-tools migration complete migration-0XXX.yaml`                               | [→](./special-workflows/migration.md#all-in-one)                  |
| `migration export`   | Download project data from the source server<br>`dsp-tools migration export migration-0XXX.yaml`                 | [→](./special-workflows/migration.md#step-by-step)                |
| `migration import`   | Import a downloaded export to another server<br>`dsp-tools migration import migration-0XXX.yaml`                 | [→](./special-workflows/migration.md#step-by-step)                |
| `migration clean-up` | Clean up local files and server references<br>`dsp-tools migration clean-up migration-0XXX.yaml`                 | [→](./special-workflows/migration.md#step-by-step)                |
| `old-excel2json`     | Create project definition JSON using the old Excel format<br>`dsp-tools old-excel2json excelfolder project.json` | [→](./data-model/excel2json.md#old-excel2json)                    |
| `old-excel2lists`    | Create the list section using the old Excel format<br>`dsp-tools old-excel2lists excelfolder lists.json`         | [→](./data-model/excel2json.md#old-excel2lists)                   |
| `resume-xmlupload`   | Resume a previously interrupted xmlupload<br>`dsp-tools resume-xmlupload`                                        | [→](./data-file/data-file-commands.md#resume-xmlupload)           |
| `start-stack`        | Start a local DSP stack<br>`dsp-tools start-stack`                                                               | [→](./local-stack.md#start-stack)                                 |
| `stop-stack`         | Stop the local DSP stack<br>`dsp-tools stop-stack`                                                               | [→](./local-stack.md#stop-stack)                                  |
| `update-legal`       | Update legal metadata in XML files to the new format<br>`dsp-tools update-legal data.xml`                        | [→](./special-workflows/update-legal.md)                          |
| `upload-files`       | Upload multimedia files referenced in an XML file<br>`dsp-tools upload-files data.xml`                           | [→](./special-workflows/workflow-xmlupload.md#upload-files)       |
| `validate-data`      | Validate XML data against a data model on a server<br>`dsp-tools validate-data data.xml`                         | [→](./data-file/data-file-commands.md#validate-data)              |
| `xmlupload`          | Create resources from an XML file on a server<br>`dsp-tools xmlupload data.xml`                                  | [→](./data-file/data-file-commands.md#xmlupload)                  |
