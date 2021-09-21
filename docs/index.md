[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS documentation

dsp-tools is a command line tool that helps you interact with the DaSCH Service Platform server (DSP server).

In order to archive your data on the DaSCH Service Platform, you need a data model (ontology) that describes your data.
The data model is defined in a JSON file which has to be transmitted to the DSP server. If the DSP server is aware of
the data model for your project, conforming data can be uploaded into the DSP repository.

Often, data is initially added in large quantities. Therefore, dsp-tools allows you to perform bulk imports of your
data. In order to do so, the data has to be described in an XML file. dsp-tools is able to read the XML file and upload
all data to the DSP server.

dsp-tools helps you with the following tasks:

- [`dsp-tools create`](./dsp-tools-usage.md#create-a-data-model-on-a-dsp-server) creates the data model (ontology) on a
  DSP server from a provided JSON file containing the data model.
- [`dsp-tools get`](./dsp-tools-usage.md#get-a-data-model-from-a-dsp-server) reads a data model from a DSP server and
  writes it into a JSON file.
- [`dsp-tools xmlupload`](./dsp-tools-usage.md#upload-data-to-a-dsp-server) uploads data from a provided XML file (bulk
  data import).
- [`dsp-tools excel`](./dsp-tools-usage.md#create-a-json-list-file-from-one-or-several-excel-files)
  creates a JSON or XML file from one or several Excel files. The created data can either be integrated into an ontology
  or be uploaded directly to a DSP server with `dsp-tools create`.
- [`dsp-tools excel2resources`](./dsp-tools-usage.md#create-resources-from-an-excel-file)
  creates the ontology's resource section from an Excel file. The resulting section can be integrated into an ontology
  and then be uploaded to a DSP server with `dsp-tools create`.
- [`dsp-tools excel2properties`](./dsp-tools-usage.md#create-properties-from-an-excel-file)
  creates the ontology's properties section from an Excel file. The resulting section can be integrated into an ontology
  and then be uploaded to a DSP server with `dsp-tools create`.

