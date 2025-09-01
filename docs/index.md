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
- **Upload data, described in an XML file, to a DSP server that has a project with a matching data model**  
  Sometimes, data is added in large quantities. 
  Therefore, DSP-TOOLS allows you to perform bulk imports of your data.
  In order to do so, the data has to be described in an XML file. 
  DSP-TOOLS is able to read the XML file 
  and upload all data to the DSP server.

All functionalities of DSP-TOOLS revolve around these two basic tasks. 

DSP-TOOLS provides the following functionalities:

- [`dsp-tools create`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#create) 
  creates the project with its data model(s) on a DSP server from a JSON file.
- [`dsp-tools get`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands#get) 
  reads a project with its data model(s) from 
  a DSP server and writes it into a JSON file.
- [`dsp-tools validate-data`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#validate-data)
  validates an XML data file according to the ontology previously uploaded on the server.
- [`dsp-tools xmlupload`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#xmlupload) 
  uploads data from an XML file (bulk data import)
  and writes the mapping from internal IDs to IRIs into a local file.
- New workflow for `xmlupload`:
    - [`dsp-tools upload-files`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#upload-files)
      uploads all files that are referenced in an XML file to a DSP server.
    - [`dsp-tools ingest-files`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#ingest-files)
      kicks off the ingest process, and retrieves the mapping CSV when it is finished.
    - [`dsp-tools ingest-xmlupload`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#ingest-xmlupload)
      creates the resources contained in the XML file, using the mapping CSV
- [`dsp-tools resume-xmlupload`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#resume-xmlupload) 
  resumes a previously interrupted `xmlupload` or `ingest-xmlupload`.
- [`dsp-tools excel2json`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#excel2json) 
  creates an entire JSON project file from a folder with Excel files in it.
    - [`dsp-tools excel2lists`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#excel2lists)
      creates the "lists" section of a JSON project file from one or several Excel files. 
      The resulting section can be integrated into a JSON project file
      and then be uploaded to a DSP server with `dsp-tools create`.
    - [`dsp-tools excel2resources`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#excel2resources)
      creates the "resources" section of a JSON project file from an Excel file. 
      The resulting section can be integrated into a JSON project file 
      and then be uploaded to a DSP server with `dsp-tools create`.
    - [`dsp-tools excel2properties`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#excel2properties)
      creates the "properties" section of a JSON project file from an Excel file. 
      The resulting section can be integrated into a JSON project file 
      and then be uploaded to a DSP server with `dsp-tools create`.
- [`dsp-tools old-excel2json`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#old-excel2json)
  does the same as the newer `excel2json` command, but the Excel format for the `lists` section is different.
    - [`dsp-tools old-excel2lists`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#old-excel2lists)
      does the same as the newer `excel2lists` command, but the Excel format is different.
- [`dsp-tools excel2xml`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#excel2xml) 
  transforms a data source to XML 
  if it is already structured according to the DSP specifications.
- [The module `excel2xml`](https://docs.dasch.swiss/latest/DSP-TOOLS/excel2xml-module) 
  provides helper methods that can be used in a Python script 
  to convert data from a tabular format into XML. (**DEPRECATED in favor of `xmllib`**)
- [The `xmllib` library](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/xmlroot/) 
  provides helper functions that can be used in a Python script 
  to convert data from a tabular format into XML.
- [`dsp-tools id2iri`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#id2iri)
  takes an XML file for bulk data import and replaces referenced internal IDs with IRIs. 
  The mapping has to be provided with a JSON file.
- [`dsp-tools start-stack / stop-stack`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#start-stack)
  assist you in running a DSP stack on your local machine.
- [`dsp-tools template`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#template)
  creates a template repository with a minimal JSON and XML file.
- [`dsp-tools rosetta`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#rosetta)
  clones the most up to date rosetta repository,
  creates the data model and uploads the data.
