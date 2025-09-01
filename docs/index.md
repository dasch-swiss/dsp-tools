[![DSP-TOOLS version on PyPI](https://img.shields.io/pypi/v/dsp-tools.svg)](https://pypi.org/project/dsp-tools/) 
[![Supported Python versions](https://img.shields.io/pypi/pyversions/dsp-tools.svg)](https://pypi.org/project/dsp-tools/)
[![License](https://img.shields.io/pypi/l/dsp-tools.svg)](https://pypi.org/project/dsp-tools/) 
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) 
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![mypy](https://img.shields.io/badge/mypy-blue)](https://github.com/python/mypy) 

# DSP-TOOLS Documentation

DSP-TOOLS is a Python package with a command line interface 
that helps you interact with a DSP server. 
A DSP server is a remote server or a local machine 
where the [DSP-API](https://github.com/dasch-swiss/dsp-api) is running on. 

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

The two main tasks that DSP-TOOLS serves for are:

- **Create a project with its data model(s), described in a JSON file, on a DSP server**  
  In order to archive your data on the DaSCH Service Platform, 
  you need a data model that describes your data.
  The data model is defined in a JSON project definition file 
  which has to be transmitted to the DSP server. 
  If the DSP server is aware of the data model for your project, 
  conforming data can be uploaded into the DSP repository.
  [Click here for details.](./data-model/json-project/overview.md)
- **Create and upload data, described in an XML file, to a DSP server that has a project with a matching data model**  
  Sometimes, data is added in large quantities. 
  Therefore, DSP-TOOLS allows you to perform bulk imports of your data.
  In order to do so, the data has to be described in an XML file. 
  DSP-TOOLS is able to read the XML file 
  and upload all data to the DSP server.
  [Click here for details.](./data-file/xml-data-file.md)
