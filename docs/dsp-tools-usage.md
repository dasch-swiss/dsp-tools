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
- `-l` | `--lists`: If set, only the lists are created using a [simplified schema](./dsp-tools-create.md#lists). Please note
  that in this case the project must already exist.
- `-v` | `--verbose`: If set, some information about the progress is printed to the console.
  
The command is used to read the definition of a data model (provided in a JSON file) and create it on the
DSP server. The following example shows how to load the ontology defined in `data_model_definition.json` onto the DSP
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
- `-P` | `--project` _shortcode_ | _shortname_ | _iri_: shortcode, shortname or
  [IRI](https://en.wikipedia.org/wiki/Internationalized_Resource_Identifier) of the project
- `-v` | `--verbose`: If set, some information about the progress is printed to the console.

The command is used to get the definition of a data model from a DSP server and write it into a JSON file. This JSON file
could then be used to upload the data model to another DSP server. The following example shows how to get the data model
from a DSP server `https://api.dsl.server.org` provided with the `-s` option. The username `root@example.com` and the
password `test` are used. The data model is saved into the output file `output_file.json`.

```bash
dsp-tools get -s https://api.dsl.server.org -u root@example.com -p test output_file.json
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

The command is used to upload data defined in an XML file onto a DSP server. The following example shows how to upload
data from an XML file `xml_data_file.xml` onto the DSP server `https://api.dsl.server.org` provided with the `-s` option.
The username `root@example.com` and the password `test` are used. The interface for the SIPI IIIF server is provided
with the `-S` option (`https://iiif.dsl.server.org`).

```bash
dsp-tools xmlupload -s https://api.dsl.server.org -u root@example.com -p test -S https://iiif.dsl.server.org xml_data_file.xml
```

The description of the expected XML format can be found [here](./dsp-tools-xmlupload.md). 

## Convert an Excel file into a JSON file that is compatible with dsp-tools

```bash
dsp-tools excel [options] excel_file.xlsx output_file.json
```

The following options are available:

- `-S` | `--sheet` _sheetname_: name of the Excel worksheet to use (default: Tabelle1)
- `-s` | `--shortcode` _shortcode_: shortcode of the project (required)
- `-l` | `--listname` _listname_: name to be used for the list and the list definition file (required)
- `-L` | `--label` _label_: label to be used for the list (required)
- `-x` | `--lang` _lang_: language used for the list labels and commentaries (default: en)
- `-v` | `--verbose`: If set, some information about the progress is printed to the console.

The description of the expected Excel format can be found [here](./dsp-tools-create.md#lists-from-excel).
