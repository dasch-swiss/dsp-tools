[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Installation and usage

The following paragraphs gives you an overview of how to install and use dsp-tools.




## Installation

To install the latest version run:

```bash
pip3 install dsp-tools
```

To update to the latest version run:

```bash
pip3 install --upgrade dsp-tools
```




## Create a project on a DSP server

```bash
dsp-tools create [options] project_definition.json
```

The following options are available:

- `-s` | `--server` _server_: URL of the DSP server (default: 0.0.0.0:3333)
- `-u` | `--user` _username_: username used for authentication with the DSP API (default: root@example.com)
- `-p` | `--password` _password_: password used for authentication with the DSP API (default: test)
- `-V` | `--validate-only`: If set, only the validation of the JSON file is performed.
- `-l` | `--lists-only`: If set, only the lists are created. Please note that in this case the project must already exist.
- `-v` | `--verbose`: If set, more information about the progress is printed to the console.
- `-d` | `--dump`: If set, dump test files for DSP-API requests.

The command is used to read the definition of a project with its data model(s) (provided in a JSON file) and create it 
on the DSP server. The following example shows how to upload the project defined in `project_definition.json` to the DSP
server `https://admin.dasch.swiss`:

```bash
dsp-tools create -s https://api.dasch.swiss -u root@example.com -p test project_definition.json
```

The expected JSON format is [documented here](./dsp-tools-create.md).




## Get a project from a DSP server

```bash
dsp-tools get [options] output_file.json
```

The following options are available:

- `-s` | `--server`: URL of the DSP server (default: 0.0.0.0:3333)
- `-u` | `--user`: username used for authentication with the DSP API (default: root@example.com)
- `-p` | `--password`: password used for authentication with the DSP API (default: test)
- `-P` | `--project`: shortcode, shortname or
  [IRI](https://en.wikipedia.org/wiki/Internationalized_Resource_Identifier) of the project (mandatory)
- `-v` | `--verbose`: If set, some information about the progress is printed to the console.

The command is used to get the definition of a project with its data model(s) from a DSP server and write it into a JSON 
file. This JSON file can then be used to create the same project on another DSP server. The following example shows how 
to get a project from the DSP server `https://admin.dasch.swiss`.

```bash
dsp-tools get -s https://api.dasch.swiss -u root@example.com -p test -P my_project output_file.json
```

The expected JSON format is [documented here](./dsp-tools-create.md).




## Upload data to a DSP server

```bash
dsp-tools xmlupload [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` _server_: URL of the DSP server (default: 0.0.0.0:3333)
- `-u` | `--user` _username_: username used for authentication with the DSP API (default: root@example.com)
- `-p` | `--password` _password_: password used for authentication with the DSP API (default: test)
- `-V` | `--validate`: If set, only the validation of the XML file is performed.
- `-i` | `--imgdir` _dirpath_: path to the directory where the bitstream objects are stored (default: .)
- `-S` | `--sipi` _SIPIserver_: URL of the SIPI IIIF server (default: http://0.0.0.0:1024)
- `-I` | `--incremental` : If set, IRIs instead of internal IDs are expected as reference to already existing resources on DSP
- `-v` | `--verbose`: If set, more information about the uploaded resources is printed to the console.

The command is used to upload data defined in an XML file onto a DSP server. The following example shows how to upload
data from the XML file `xml_data_file.xml` to the DSP server `https://admin.dasch.swiss`:

```bash
dsp-tools xmlupload -s https://api.dasch.swiss -u root@example.com -p test -S https://iiif.dasch.swiss xml_data_file.xml
```

The expected XML format is [documented here](./dsp-tools-xmlupload.md).

An internal ID is used in the `<resptr>` tag of an XML file to reference resources inside the same XML file. Once data 
is uploaded to DSP, it cannot be referenced by this internal ID anymore. Instead, the resource's IRI has to be used. 
After a successful `xmlupload`, the mapping of internal IDs to their respective IRIs is written to a file
called `id2iri_mapping_[timstamp].json`.
See [`dsp-tools id2iri`](./dsp-tools-usage.md#replace-internal-ids-with-iris-in-xml-file) for more information about how
to use this file to replace internal IDs in an existing XML file to reference existing resources.




## Create the "lists" section of a JSON project file from Excel files

```bash
dsp-tools excel2lists folder output.json
```

Arguments:
 - `folder` (optional, default: "lists"): folder with the Excel file(s)
 - `output.json` (optional, default: "lists.json"): Output file

The expected Excel format is [documented here](./dsp-tools-excel.md#create-the-lists-section-of-a-json-project-file-from-excel-files).



## Create the "resources" section of a JSON project file from an Excel file

```bash
dsp-tools excel2resources excel_file.xlsx output_file.json
```

The command is used to create the resources section of an ontology from an Excel file. Therefore, an Excel file has to
be provided with the data in the first worksheet of the Excel file.

The following example shows how to create the resources section from an Excel file called `Resources.xlsx`. The output
is written to a file called `resources.json`.

```bash
dsp-tools excel2resources Resources.xlsx resources.json
```

More information about the usage of this command can be
found [here](./dsp-tools-excel.md#create-the-resources-for-a-data-model-from-an-excel-file).




## Create the "properties" section of a JSON project file from an Excel file

```bash
dsp-tools excel2properties excel_file.xlsx output_file.json
```

The command is used to create the properties section of an ontology from an Excel file. Therefore, an Excel file has to
be provided with the data in the first worksheet of the Excel file.

The following example shows how to create the properties section from an Excel file called `Properties.xlsx`. The output
is written to a file called `properties.json`.

```bash
dsp-tools excel2properties Properties.xlsx properties.json
```

More information about the usage of this command can be found
[here](./dsp-tools-excel.md#create-the-properties-for-a-data-model-from-an-excel-file).



## Create an XML file from Excel/CSV
```bash
dsp-tools excel2xml data-source.xlsx project_shortcode ontology_name
```

Arguments:

 - data-source.xlsx: An Excel/CSV file that is structured according to [these requirements](dsp-tools-excel.md#cli-command-excel2xml)
 - project_shortcode: The four-digit hexadecimal shortcode of the project
 - ontology_name: the name of the ontology that the data belongs to

If your data source is already structured according to the DSP specifications, but it is not in XML format yet, the 
command `excel2xml` will transform it into XML. This is mostly used for DaSCH-interal data migration. There are no 
flags/options for this command. The details of this command are documented [here](dsp-tools-excel.md#cli-command-excel2xml).

If your data source is not yet structured according to the DSP specifications, you need a custom Python script for the 
data transformation. For this, you might want to import the module `excel2xml` into your Python script, which is 
described in the next paragraph.



## Use the module `excel2xml` to convert a data source to XML
dsp-tools assists you in converting a data source in CSV/XLS(X) format to an XML file. Unlike the other features of 
dsp-tools, this doesn't work via command line, but via helper methods that you can import into your own Python script. 
Because every data source is different, there is no single algorithm to convert them to a DSP conform XML. Every user 
has to deal with the specialties of his/her data source, but `excel2xml`'s helper methods can help a lot. Read more 
about it [here](./dsp-tools-excel2xml.md).




## Replace internal IDs with IRIs in XML file

```bash
dsp-tools id2iri xml_file.xml mapping_file.json --outfile xml_out_file.xml
```

When uploading data with `dsp-tools xmlupload` an internal ID is used in the `<resptr>` tag of the XML file to reference
resources inside the same XML file. Once data is uploaded to DSP it cannot be referenced by this internal ID anymore.
Instead, the resource's IRI has to be used.

With `dsp-tools id2iri` internal IDs can be replaced with their corresponding IRIs within a provided XML. The output is
written to a new XML file called `id2iri_replaced_[timestamp].xml` (the file path and name can be overwritten with
option `--outfile`). If all internal IDs were replaced, the newly created XML can be used
with `dsp-tools xmlupload --incremental id2iri_replaced_20211026_120247263754.xml` to upload the data.

Note that internal IDs and IRIs cannot be mixed. The input XML file has to be provided as well as the JSON file which
contains the mapping from internal IDs to IRIs. This JSON file is generated after each successful `xmlupload`.

In order to upload data incrementally the procedure described [here](dsp-tools-xmlupload.md#incremental-xml-upload) is recommended.


## Generate test data
```bash
dsp-tools generate-test-data config.json
```
Lorem ipsum
