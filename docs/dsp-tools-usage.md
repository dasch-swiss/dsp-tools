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

## Create a data model on a DSP server

```bash
dsp-tools create [options] data_model_definition.json
```

The following options are available:

- `-s` | `--server` _server_: URL of the DSP server (default: localhost:3333)
- `-u` | `--user` _username_: username used for authentication with the DSP API (default: root@example.com)
- `-p` | `--password` _password_: password used for authentication with the DSP API (default: test)
- `-V` | `--validate`: If set, only the validation of the JSON file is performed.
- `-l` | `--lists`: If set, only the lists are created using a [simplified schema](./dsp-tools-create.md#lists). Please
  note that in this case the project must already exist.
- `-v` | `--verbose`: If set, some information about the progress is printed to the console.

The command is used to read the definition of a data model (provided in a JSON file) and create it on the DSP server.
The following example shows how to load the ontology defined in `data_model_definition.json` onto the DSP
server `https://api.dsl.server.org` provided with the `-s` option. The username `root@example.com` and the password
`test` are used.

```bash
dsp-tools create -s https://api.dsl.server.org -u root@example.com -p test data_model_definition.json
```

The description of the expected JSON format can be found [here](./dsp-tools-create.md).

## Get a data model from a DSP server

```bash
dsp-tools get [options] output_file.json
```

The following options are available:

- `-s` | `--server` _server_: URL of the DSP server (default: localhost:3333)
- `-u` | `--user` _username_: username used for authentication with the DSP API (default: root@example.com)
- `-p` | `--password` _password_: password used for authentication with the DSP API (default: test)
- `-P` | `--project` _shortcode_ | _shortname_ | _iri_: shortcode, shortname or (mandatory)
  [IRI](https://en.wikipedia.org/wiki/Internationalized_Resource_Identifier) of the project
- `-v` | `--verbose`: If set, some information about the progress is printed to the console.

The command is used to get the definition of a data model from a DSP server and write it into a JSON file. This JSON
file could then be used to upload the data model to another DSP server. The following example shows how to get the data
model from a DSP server `https://api.dsl.server.org` provided with the `-s` option. The username `root@example.com` and
the password `test` are used. The data model is saved into the output file `output_file.json`.

```bash
dsp-tools get -s https://api.dsl.server.org -u root@example.com -p test -P my_project output_file.json
```

## Upload data to a DSP server

```bash
dsp-tools xmlupload [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` _server_: URL of the DSP server (default: localhost:3333)
- `-u` | `--user` _username_: username used for authentication with the DSP API (default: root@example.com)
- `-p` | `--password` _password_: password used for authentication with the DSP API (default: test)
- `-i` | `--imgdir` _dirpath_: path to the directory where the bitstream objects are stored (default: .)
- `-S` | `--sipi` _SIPIserver_: URL of the SIPI IIIF server (default: http://0.0.0.0:1024)
- `--incremental` : If set, IRIs instead of internal IDs are expected as reference to already existing resources on DSP
- `-v` | `--verbose`: If set, more information about the uploaded resources is printed to the console.

The command is used to upload data defined in an XML file onto a DSP server. The following example shows how to upload
data from an XML file `xml_data_file.xml` onto the DSP server `https://api.dsl.server.org` provided with the `-s`
option. The username `root@example.com` and the password `test` are used. The interface for the SIPI IIIF server is
provided with the `-S`
option (`https://iiif.dsl.server.org`).

```bash
dsp-tools xmlupload -s https://api.dsl.server.org -u root@example.com -p test -S https://iiif.dsl.server.org xml_data_file.xml
```

The description of the expected XML format can be found [here](./dsp-tools-xmlupload.md).

An internal ID is used in the `<resptr>` tag of an XML file used for `xmlupload` to reference resources inside the same
XML file. Once data is uploaded to DSP it cannot be referenced by this internal ID anymore. Instead, the resource's IRI
has to be used. The mapping of internal IDs to their respective IRIs is written to a file
called `id2iri_mapping_[timstamp].json` after a successful `xmlupload`.
See [`dsp-tools id2iri`](./dsp-tools-usage.md#replace-internal-ids-with-iris-in-xml-file) for more information about how
to use this file to replace internal IDs in an existing XML file to reference existing resources.

## Create a JSON list file from one or several Excel files

```bash
dsp-tools excel [option] folder_with_excel_files output_file.json
```

The following option is available:

- `-l` | `--listname` _listname_: name to be used for the list (filename before last occurrence of `_` is used if
  omitted)

The command is used to create a JSON list file from one or several Excel files. It is possible to create multilingual
lists. Therefore, an Excel file for each language has to be provided. The data has to be in the first worksheet of the
Excel file and all Excel files have to be in the same directory. When calling the `excel` command, this directory has to
be provided as an argument to the call.

The following example shows how to create a JSON list from Excel files in a directory called `lists`.

```bash
dsp-tools excel lists list.json
```

The description of the expected Excel format can be found [here](./dsp-tools-create.md#lists-from-excel). More
information about the usage of this command can be
found [here](./dsp-tools-excel.md#create-a-list-from-one-or-several-excel-files).

## Create resources from an Excel file

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
found [here](./dsp-tools-excel.md#create-the-resources-for-a-data-model-from-an-excel-file)
.

## Create properties from an Excel file

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
[here](./dsp-tools-excel.md#create-the-properties-for-a-data-model-from-an-excel-file)
.

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
