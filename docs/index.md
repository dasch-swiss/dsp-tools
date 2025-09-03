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
    - If you want to create the XML file required for a mass-upload onto DSP, take a look at the [`xmllib`](./xmllib-docs/overview.md).
    - You can find an in-depth explanation of our XML file format [here](./data-file/xml-data-file.md).
      Please note, that we recommend to use the `xmllib` library to create the file 
      as we will ensure interoperability between the DSP-API requirements and your input.
    - If you want to validate and upload your XML file take a look [here](./data-file/data-file-commands.md).
      Please note, that only DaSCH employees are permitted to upload data on a production server.
