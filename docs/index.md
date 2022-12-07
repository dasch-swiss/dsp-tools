[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS documentation

DSP-TOOLS is a Python package with a command line interface that helps you interact with a DSP server. The DSP server 
you interact with can be on a remote server, or on your local machine. The two main tasks that DSP-TOOLS serves for are:

**Create a project with its data model(s), described in a JSON file, on a DSP server**  
In order to archive your data on the DaSCH Service Platform, you need a data model that describes your data.
The data model is defined in a JSON project definition file which has to be transmitted to the DSP server. If the DSP 
server is aware of the data model for your project, conforming data can be uploaded into the DSP repository.

**Upload data, described in an XML file, to a DSP server that has a project with a matching data model**  
Sometimes, data is added in large quantities. Therefore, DSP-TOOLS allows you to perform bulk imports of your
data. In order to do so, the data has to be described in an XML file. DSP-TOOLS is able to read the XML file and upload
all data to the DSP server.

All of DSP-TOOLS' functionality revolves around these two basic tasks. 

DSP-TOOLS provides the following functionalities:

- [`dsp-tools create`](./dsp-tools-usage.md#create-a-project-on-a-dsp-server) creates the project with its data model(s) 
  on a DSP server from a JSON file.
- [`dsp-tools get`](./dsp-tools-usage.md#get-a-project-from-a-dsp-server) reads a project with its data model(s) from 
  a DSP server and writes it into a JSON file.
- [`dsp-tools xmlupload`](./dsp-tools-usage.md#upload-data-to-a-dsp-server) uploads data from an XML file (bulk
  data import) and writes the mapping from internal IDs to IRIs into a local file.
- [`dsp-tools excel2json`](./dsp-tools-usage.md#create-a-json-project-file-from-excel-files) creates an entire JSON
  project file from a folder with Excel files in it.
    - [`dsp-tools excel2lists`](./dsp-tools-usage.md#create-the-lists-section-of-a-json-project-file-from-excel-files)
      creates the "lists" section of a JSON project file from one or several Excel files. The resulting section can be 
      integrated into a JSON project file and then be uploaded to a DSP server with `dsp-tools create`.
    - [`dsp-tools excel2resources`](./dsp-tools-usage.md#create-the-resources-section-of-a-json-project-file-from-an-excel-file)
      creates the "resources" section of a JSON project file from an Excel file. The resulting section can be integrated 
      into a JSON project file and then be uploaded to a DSP server with `dsp-tools create`.
    - [`dsp-tools excel2properties`](./dsp-tools-usage.md#create-the-properties-section-of-a-json-project-file-from-an-excel-file)
      creates the "properties" section of a JSON project file from an Excel file. The resulting section can be integrated 
      into a JSON project file and then be uploaded to a DSP server with `dsp-tools create`.
- [`dsp-tools excel2xml`](./dsp-tools-usage.md#create-an-xml-file-from-excelcsv) transforms a data source to XML if it 
  is already structured according to the DSP specifications.
- [The module `excel2xml`](./dsp-tools-usage.md#use-the-module-excel2xml-to-convert-a-data-source-to-xml) provides helper
  methods that can be used in a Python script to convert data from a tabular format into XML.
- [`dsp-tools id2iri`](./dsp-tools-usage.md#replace-internal-ids-with-iris-in-xml-file)
  takes an XML file for bulk data import and replaces referenced internal IDs with IRIs. The mapping has to be provided
  with a JSON file.
- [`dsp-tools start-stack / stop-stack`](./dsp-tools-usage.md#start-a-dsp-stack-on-your-local-machine)
  assist you in running a DSP stack on your local machine.
