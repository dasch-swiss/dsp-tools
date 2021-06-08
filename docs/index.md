[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# dsp-tools documentation

dsp-tools is a command line tool that helps you interact with the DaSCH Service Platform server (DSP server).

In order to archive your data on the DaSCH Service Platform, you need a data model (ontology) that describes your data.
The data model is defined in a JSON file which has to be transmitted to the DSP server. If the DSP server is aware of
the data model for your project, conforming data can be uploaded into the DSP repository.

Often, data is initially added in large quantities. Therefore, dsp-tools allows you to perform bulk imports of your data.
In order to do so, the data has to be described in an XML file. dsp-tools is able to read the XML file and upload all data
to the DSP server.

dsp-tools helps you with the following tasks:

- [`dsp-tools create`](./dsp-tools-usage.md#create-a-data-model-on-a-dsp-server) creates the data model (ontology) on a
  DSP server from a provided JSON file containing the data model.
- [`dsp-tools get`](./dsp-tools-usage.md#get-a-data-model-from-a-dsp-server) reads a data model from a DSP server and
  writes it into a JSON file.
- [`dsp-tools xmlupload`](./dsp-tools-usage.md#upload-data-to-a-dsp-server) uploads data from a provided XML file (bulk
  data import).
- [`dsp-tools excel`](./dsp-tools-usage.md#convert-an-excel-file-into-a-json-file-that-is-compatible-with-dsp-tools)
  converts an Excel file into a JSON and/or XML file in order to use it with `dsp-tools create` or `dsp-tools xmlupload`
  (not yet implemented) or converts a list from an Excel file into a JSON file which than can be used in an ontology.
