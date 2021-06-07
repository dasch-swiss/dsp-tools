[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# dsp-tools
dsp-tools is a command line tool that helps you interact with the DaSCH Service Platform server (DSP server).

In order to archive your data on the DaSCH Service Platform, you need a data model (ontology) that describes your data.
The data model is defined in a JSON file which has to be transmitted to the DSP server. If the DSP server is aware of
the data model for your project, conforming data can be uploaded into the DSP repository.

Often, data is initially added in large quantities. Therefore, dsp-tools allows you to perform bulk imports of your data.
In order to do so, the data has to be described in an XML file. dsp-tools is able to read the XML file and upload all data
to the DSP server.

dsp-tools helps you with the following tasks:

- `dsp-tools create` creates the data model (ontology) on a DSP server from a provided JSON file containing the data
  model.
- `dsp-tools get` reads a data model from a DSP server and writes it into a JSON file.
- `dsp-tools xmlupload` uploads data from a provided XML file (bulk data import).
- `dsp-tools excel` converts an Excel file into a JSON and/or XML file in order to use it with `dsp-tools create` or
  `dsp-tools xmlupload` (not yet implemented) or converts a list from an Excel file into a JSON file which than can be
  used in an ontology.

## Usage

### Installation

To install the latest version run:

```
pip3 install dsp-tools
```

To update to the latest version run:

```
pip3 install --upgrade dsp-tools
```

### Create a data model on a DSP server

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

### Get a data model from a DSP server

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

### Upload data to a DSP server

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

### Convert an Excel file into a JSON file that is compatible with dsp-tools

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

## Information for developers

### Makefile

There is a `Makefile` for all the following tasks (and more). Type `make` to print the available targets.

### Install from source

To install from source run:
```bash
python3 setup.py install
```

### Requirements

To install the requirements run:

```bash
pip3 install -r requirements.txt
```

To generate a requirements file (usually requirements.txt), that you commit with your project, run:

```bash
pip3 freeze > requirements.txt
```

### Testing
Please note that testing requires launching the complete DSP API stack which is based on docker images. Therefore, we
recommend installing the [docker desktop client](https://www.docker.com/products).

To run the complete test suite:

```bash
make test
```

### Publishing

Publishing is automated with GitHub Actions and should _not_ be done manually. Please follow the
[Pull Request Guidelines](https://docs.dasch.swiss/developers/dsp/contribution/#pull-request-guidelines). If done
correctly, when merging a pull request into `main`, the `release-please` action will create or update a pull request for
a release. This pull request will follow semantic versioning and update the change log. Once all desired features are
merged, the release can be executed by merging this release pull request into `main`. This will trigger actions that
create a release on GitHub, on PyPI and the docs.

Please ensure you have only one pull request per feature.

### Publishing manually

Publishing is automated with GitHub Actions and should _not_ be done manually. If you still need to do it, follow the
steps below.

Generate the distribution package. Make sure you have the latest versions of `setuptools` and `wheel` installed:

```bash
python3 -m pip install --upgrade pip setuptools wheel
python3 setup.py sdist bdist_wheel
```

You can install the package locally from the dist:

```bash
python3 -m pip ./dist/some_name.whl
```

Upload package works also with `make`:

```bash
make dist
make upload
```

For local development:

```bash
python3 setup.py develop
```

### Contributing to the documentation

The documentation is a collection of [markdown](https://en.wikipedia.org/wiki/Markdown) files in the `docs` folder.  
After updates of the files, build and check the result with the following commands:

```bash
make build-docs
make serve-docs 
```

To update the changes to the official documentation pages run:

```bash
make publish-docs
```
