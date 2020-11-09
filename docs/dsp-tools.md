[![PyPI version](https://badge.fury.io/py/knora.svg)](https://badge.fury.io/py/knora)

# dsp-tools
In order to work with a DaSCH Service Platform server (DSP-server), the user has to create a data
models (aka `ontologies`) of her/his data. This data model is defined in a special JSON-file which
then can be transmitted to the DSP-server. If the DSP-server is aware of the data model, conforming data
can be uploaded to the server.

Often, data is initially added in large quantities. Such `bulk data imports` can also be performed using the
dsp-tools. For this purpose, the data has first to be converted in a special XML-file that can be read by
dsp-tools. The dsp-tools program will read this file and upload all data to the DSP-server.

Thus, the command `dsp-tools` can be used to upload a data model (ontology) from a JSON file to a DaSCH Service Platform (DSP)
server, to dump a data model from a DSP server to a JSON file, or to upload data to a DSP server from
a XML file

- `dsp-tools create` creates an ontology. Furthermore, the script reads a JSON file containing the data model 
  (ontology) definition, connects to the DSP server and creates the data model.
- `dsp-tools get` reads an ontology from a server and creates a JSON file that can be used again by
  `dsp-tools create` to implement the data model on another server
- `dsp-tools xmlupload` to upload data from a XML file (bulk data import)

## Usage

### Create an ontology on a server

```bash
$ dsp-tools create [options] data_model_definition.json
```
The above command line supports the following options:

- _"-s server" | "--server server"_: URL of the DSP server [default: localhost:3333].
- _"-u username" | "--user username"_: Username to log into DSP [default: root@example.com].
- _"-p password" | "--password password"_: Password for login to the DSP server [default: test].
- _"-V" | "--validate"_: If this flag is set, only the validation of the JSON runs.
- _"-l" | "--lists"_: This only creates the lists using a [simplified schema](#json-for-lists). Please note
  that in this case the project __must__ exist.
- _"-v" | "--verbose"_: Print out some information about progress
  
This command is used to read a JSON-based definition of an ontology and create it on the
given DSP-server. So for example you can have the command:

```
$ dsp-tools create -s https://api.dsl.server.org data_model_definition.json
```

which would load the ontology defined in `data_model_definition.json` onto the server given
by the `-s`-options.

### Get an ontology from a server

```bash
$ dsp-tools get [options] output-file
```

The above command line supports the following options:

- _"-s server" | "--server server"_: URL of the Knora server [default: localhost:3333].
- _"-u username" | "--user username"_: Username to log into Knora [default: root@example.com].
- _"-p password" | "--password password"_: Password for login to the Knora server [default: test].
- _"-P project" | "--project shortcode|shortname|iri"_: Shortcode, shortname or iri of project
- _"-v" | "--verbose"_: Print out some information about progress

### Upload data to a DSP server

```bash
$ dsp-tools xmlupload [options] xml-data-file
```

This command line uploads all the data defined in the XML file. It supports the following options:

- _"-s server" | "--server server"_: URL of the Knora server [default: localhost:3333].
- _"-u username" | "--user username"_: Username to log into Knora [default: root@example.com].
- _"-p password" | "--password password"_: Password for login to the Knora server [default: test].

    parser_upload.add_argument("-i", "--imgdir", type=str, default=".", help="Path to folder containing the images")
    parser_upload.add_argument("-S", "--sipi", type=str, default="http://0.0.0.0:1024", help="URL of SIPI server")

