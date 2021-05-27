[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# dsp-tools
In order to work with a DaSCH Service Platform server (DSP-server), the user has to create a data
model (aka `ontologies`) of her/his data. This data model is defined in a special JSON-file which
then can be transmitted to the DSP-server. If the DSP-server is aware of the data model, conforming data
can be uploaded to the server.

Often, data is initially added in large quantities. Such `bulk data imports` can also be performed using the
dsp-tools. For this purpose, the data has first to be converted in a special XML-file that can be read by
dsp-tools. The dsp-tools program will read this file and upload all data to the DSP-server.

Thus, the command `dsp-tools` can be used to upload a data model (ontology) from a JSON file to a DaSCH Service Platform (DSP)
server, to dump a data model from a DSP server to a JSON file, or to upload data to a DSP server from
a XML file

- `dsp-tools create` creates a data model. Furthermore, the script reads a JSON file containing the data model 
  (ontology) definition, connects to the DSP server and creates the data model.
- `dsp-tools get` reads a data model from a server and creates a JSON file that can be used again by
  `dsp-tools create` to implement the data model on another server
- `dsp-tools xmlupload` to upload data from a XML file (bulk data import)
- `dsp-tools excel` to convert an Excel-file into a JSON and/or XML file for the `create` or `xmlupload` options.

## Usage

### Installation

To install the latest version published on PyPI run:
```
$ pip3 install dsp-tools
```

To update to the latest version run:
```
$ pip3 install --upgrade dsp-tools
```



### Create an data model on a server

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

The description about the JSON format can be found [here](./dsp-tools-create.md). 

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

- _"-s server" | "--server server"_: URL of the Knora server [default: http://0.0.0.0:3333].
- _"-u username" | "--user username"_: Username to log into Knora [default: root@example.com].
- _"-p password" | "--password password"_: Password for login to the Knora server [default: test].
- _"-i dirpath" | "--imgdir"dirpath"_: Path to the directory where the bitstream objects are stored [default: "."].
- _"-S sipiserver" | "--sipi sipiserver"_: URL of the SIPI IIIF-server [default: http://0.0.0.0:1024]
- _"xmlfile"_: Path to xml-File containing the data.

The description about the XML-format for the data is found [here](./dsp-tools-xmlupload.md).
    
### Convert an Excel file for use with dsp tools

```bash
$ dsp-tools excel [options] excel-file output-file
```

The excel command supports the following options:

- _"-S sheetname" | "--sheet sheetname"_: Name of the excel worksheet to use [default: Tabelle1].
- _"-s shortcode" | "--shortcode shortcode"_: The 4 digit hexcode given to the project the list belongs to [required].
- _"-l listname" | "--listname listname"_: Name to be used for the list and to be inserted into thge list definitionfile [required].
- _"-L label" | "--label label"_: The label text to be used for the list [required].
- _"-x lang" | "--lang lang"_: The language the list labels and commentary is given [default: en].
- _"-v" | "--verbose"_: Print out some information about progress.
- _"excel-file"_: Input file in the Excel "*.xlsx"-Format.
- _"output-file"_: Output file containing the JSON-formatted definition of the list.

A description of the required Excel format is found [here](./dsp-tools-create.md#lists-from-excel).

## Information for Developers

## Makefile

There is a helping `Makefile` for all of the following tasks (and more).  
It is self-explanatory and a simple `make` will print its available targets.

## Install from source

To install from source, i.e. this repository run:
```
$ python3 setup.py install
```

## Requirements

To install the requirements:

```bash
$ pip3 install -r requirements.txt
```


To generate a "requirements" file (usually requirements.txt), that you commit with your project, do:

```bash
$ pip3 freeze > requirements.txt
```

## Testing
Please note that testing requires launching the complete dsp-api stack which is based on docker images.
Therefore You need to install the [docker desktop client](https://www.docker.com/products).
Make test will run the complete test suite for dsp-tools.

```bash
make test
```

## Publishing

Publishing is automated with github actions and should _not_ be done manually.

Ensure to have only one Pull Request per feature, and follow the [conventions for commit messages and PR title](https://docs.dasch.swiss/developers/dsp/contribution/#pull-request-guidelines).

If this is done correctly, when merging a PR into `main`, the `release-please` action will create or update a release-PR.  
This PR will follow semantic versioning and update the change log.  
Once all desired features are merged, the release can be executed by merging the release-PR into `main`.  
This will trigger actions that create a release on Github, on PyPI and the docs.


### Publishing Manually

Generate distribution package. Make sure you have the latest versions of `setuptools` and `wheel` installed:

```bash
$ python3 -m pip install --upgrade pip setuptools wheel
$ python3 setup.py sdist bdist_wheel
```

You can install the package locally from the dist:

```bash
$ python3 -m pip ./dist/some_name.whl
```

Upload package also with `make`:

```bash
$ make dist
$ make upload
```

For local development:

```bash
$ python3 setup.py develop
```

## Contributing to the documentation

The documentation is a collection of [markdown](https://en.wikipedia.org/wiki/Markdown) in the `docs` sub-folder.  
After updates, it is possible to build and check the result with the commands:

```bash
$ make build-docs
$ make serve-docs 
```

To update the changes to the official documentation pages:

```bash
$ make publish-docs
```

