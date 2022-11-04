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

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP API 
- `-V` | `--validate-only` (optional): If set, only the validation of the JSON file is performed.
- `-l` | `--lists-only` (optional): If set, only the lists are created. Please note that in this case the project must already exist.
- `-v` | `--verbose` (optional): If set, more information about the progress is printed to the console.
- `-d` | `--dump` (optional): If set, dump test files for DSP-API requests.

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

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP API 
- `-P` | `--project` (mandatory): shortcode, shortname or
  [IRI](https://en.wikipedia.org/wiki/Internationalized_Resource_Identifier) of the project 
- `-v` | `--verbose` (optional): If set, some information about the progress is printed to the console.

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

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP API
- `-i` | `--imgdir` (optional, default: `.`): path to the directory where the bitstream objects are stored
- `-S` | `--sipi` (optional, default: `http://0.0.0.0:1024`): URL of the SIPI IIIF server 
- `-I` | `--incremental` (optional) : If set, IRIs instead of internal IDs are expected as reference to already existing resources on DSP
- `-V` | `--validate` (optional): If set, the XML file will only be validated, but not uploaded.
- `-v` | `--verbose` (optional): If set, more information about the process is printed to the console.

The command is used to upload data defined in an XML file onto a DSP server. The defaults are intended for local 
testing: 
```bash
dsp-tools xmlupload xml_data_file.xml
```

will upload the XML file on `localhost` for local viewing. It assumes that DSP-API has been started up with the default 
settings, and that potential `<bitstream>` tags contain file paths that are relative to the working directory from where 
`dsp-tools` is called from.

When uploading data to a remote DSP server, there are three relevant URLs you should know about:

 - Subdomain `admin` stands for the DSP-APP frontend that you look at in your browser
 - Subdomain `api` stands for the DSP-API (where dsp-tools sends its data to) 
 - Subdomain `iiif` stands for the SIPI-server interface (where dsp-tools sends the multimedia files to)

This means that for uploading data to a DSP server on the domain `dasch.swiss`, you have to type the following:
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




## Create a JSON project file from Excel files

``` 
dsp-tools excel2project data_model_files project.json
```

The expected file and folder structures are described [here](./dsp-tools-excel.md#json-project-file-from-excel).




### Create the "lists" section of a JSON project file from Excel files

```bash
dsp-tools excel2lists [options] folder output.json
```

The following options are available:

- `-v` | `--verbose` (optional): If set, more information about the progress is printed to the console.

The expected Excel format is [documented here](./dsp-tools-excel.md#lists-section).

**Tip: The command [`excel2project`](#create-a-json-project-file-from-excel-files) might be more convenient to use.**



### Create the "resources" section of a JSON project file from an Excel file

```bash
dsp-tools excel2resources excel_file.xlsx output_file.json
```

The command is used to create the resources section of an ontology from an Excel file. Therefore, an Excel file has to
be provided with the data in the first worksheet of the Excel file.

The expected Excel format is [documented here](./dsp-tools-excel.md#resources-section).

**Tip: The command [`excel2project`](#create-a-json-project-file-from-excel-files) might be more convenient to use.**




### Create the "properties" section of a JSON project file from an Excel file

```bash
dsp-tools excel2properties excel_file.xlsx output_file.json
```

The command is used to create the properties section of an ontology from an Excel file. Therefore, an Excel file has to
be provided with the data in the first worksheet of the Excel file.

The expected Excel format is [documented here](./dsp-tools-excel.md#properties-section).

**Tip: The command [`excel2project`](#create-a-json-project-file-from-excel-files) might be more convenient to use.**



## Create an XML file from Excel/CSV
```bash
dsp-tools excel2xml data-source.xlsx project_shortcode ontology_name
```

Arguments:

 - data-source.xlsx (mandatory): An Excel/CSV file that is structured according to [these requirements](dsp-tools-excel.md#cli-command-excel2xml)
 - project_shortcode (mandatory): The four-digit hexadecimal shortcode of the project
 - ontology_name (mandatory): the name of the ontology that the data belongs to

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



## Start a DSP-stack on your local machine (for DaSCH-internal use only)

For testing purposes, it is sometimes necessary to have DSP-API and/or DSP-APP running on a local machine. The startup 
and shutdown of API and APP can be complicated: Both repos need to be cloned locally, a `git pull` has to be executed 
from time to time to stay up to date, and then there are several commands for each repository to remember. 
That's why dsp-tools offers some commands to facilitate the handling of API and APP. 

The only requirements for these commands are:

 - the initial installation of all software that you accomplished when you started working at DaSCH
 - Docker must be running

It isn't necessary anymore to clone DSP-API and DSP-APP, to navigate to these repos and execute commands there.

Please note that these commands were developed for DaSCH-internal use only. They only work on Macs that have the 
required software installed that makes it possible to run the API and APP. We don't offer support or troubleshooting 
for these commands.


### Start DSP-API

```
dsp-tools start-api
```

This command makes a clone of the [DSP-API repository](https://github.com/dasch-swiss/dsp-api) into `~/.dsp-tools`. If
it finds an existing clone there, it runs `git pull` instead. If the API is already running, it shuts down the old 
instance and starts a new one. If the dependencies are outdated or not installed, a warning is printed to the console.


### Shut DSP-API down

```
dsp-tools stop-api
```

This command shuts DSP-API down, deletes all Docker volumes, and removes temporary files.


### Start DSP-APP

```
dsp-tools start-app
```

This command makes a clone of the [DSP-APp repository](https://github.com/dasch-swiss/dsp-app) into `~/.dsp-tools`. If
it finds an existing clone there, it runs `git pull` instead. Then, it installs the `npm` dependencies and runs DSP-APP.
You must keep the terminal window open as long as you work with the APP. Then, you can press `Ctrl` + `C` to stop DSP-APP.
