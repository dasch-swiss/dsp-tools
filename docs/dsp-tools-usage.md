[![DSP-TOOLS](https://img.shields.io/github/v/release/dasch-swiss/dsp-tools?include_prereleases&label=DSP-TOOLS)](https://github.com/dasch-swiss/dsp-tools)

# Installation and usage

DSP-TOOLS is a Python package with a command line interface 
that helps you interact with a DSP server. 
The DSP server you interact with can be on a remote server, 
or on your local machine. 
The following paragraphs give you an overview of how to install and use DSP-TOOLS.



## Installation

To install the latest version, run:

```bash
pip3 install dsp-tools
```

To update to the latest version run:

```bash
pip3 install --upgrade dsp-tools
```



## Before starting: Have in mind the URLs of a DSP server

DaSCH follows some conventions when setting up our servers. 
Most of the commands documented on this page 
assume that you know how to address the subdomains of a DSP server.
There are three relevant URLs you should know about:

 - Subdomain `admin` stands for the DSP-APP frontend that you look at in your browser
 - Subdomain `api` stands for the DSP-API (where DSP-TOOLS sends its data to) 
 - Subdomain `iiif` stands for the SIPI-server interface (where DSP-TOOLS sends the multimedia files to)

This means that for uploading data to a DSP server 
on the domain `dasch.swiss`, 
you have to type the following:

```bash
dsp-tools xmlupload -s https://api.dasch.swiss -u root@example.com -p test -S https://iiif.dasch.swiss xml_data_file.xml
```



## Create a project on a DSP server

This command reads the definition of a project with its data model(s) 
(provided in a JSON file) 
and creates it on a DSP server.

```bash
dsp-tools create [options] project_definition.json
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
- `-V` | `--validate-only` (optional): If set, only the validation of the JSON file is performed.
- `-l` | `--lists-only` (optional): If set, only the lists are created. Please note that in this case the project must already exist.
- `-v` | `--verbose` (optional): If set, more information about the progress is printed to the console.
- `-d` | `--dump` (optional): If set, dump test files for DSP-API requests.

The defaults are intended for local testing: 

```bash
dsp-tools create project_definition.json
```

will create the project defined in `project_definition.json` on `localhost` for local viewing.

In order to create the same project
on the DSP server `https://admin.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools create -s https://api.dasch.swiss -u root@example.com -p test project_definition.json
```

The expected JSON format is [documented here](./dsp-tools-create.md).



## Get a project from a DSP server

This command retrieves the definition of a project with its data model(s) 
from a DSP server 
and writes it into a JSON file. 
This JSON file can then be used 
to create the same project on another DSP server. 

```bash
dsp-tools get [options] output_file.json
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
- `-P` | `--project` (mandatory): shortcode, shortname or
  [IRI](https://en.wikipedia.org/wiki/Internationalized_Resource_Identifier) of the project 
- `-v` | `--verbose` (optional): If set, some information about the progress is printed to the console.

The following example shows 
how to get a project from the DSP server `https://admin.dasch.swiss`:

```bash
dsp-tools get -s https://api.dasch.swiss -u root@example.com -p test -P my_project output_file.json
```

The expected JSON format is [documented here](./dsp-tools-create.md).



## Upload data to a DSP server

This command uploads data defined in an XML file onto a DSP server. 

```bash
dsp-tools xmlupload [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `-i` | `--imgdir` (optional, default: `.`): folder where the paths in the `<bitstream>` tags are evaluated from
- `-S` | `--sipi` (optional, default: `http://0.0.0.0:1024`): URL of the SIPI IIIF server 
- `-I` | `--incremental` (optional) : If set, IRIs instead of internal IDs are expected as reference to already existing resources on DSP
- `-V` | `--validate` (optional): If set, the XML file will only be validated, but not uploaded.
- `-v` | `--verbose` (optional): If set, more information about the process is printed to the console.
- `-m` | `--metrics` (optional): If set, write metrics into a "metrics" folder in the current working directory

The defaults are intended for local testing: 

```bash
dsp-tools xmlupload xml_data_file.xml
```

will upload the data defined in `xml_data_file.xml` on `localhost` for local viewing.

In order to upload the same data 
to the DSP server `https://admin.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools xmlupload -s https://api.dasch.swiss -u root@example.com -p test -S https://iiif.dasch.swiss xml_data_file.xml
```

The expected XML format is [documented here](./dsp-tools-xmlupload.md).



## Create a JSON project file from Excel files

This command creates a JSON project file from a nested folder structure with Excel files.

``` 
dsp-tools excel2json data_model_files project.json
```

The expected Excel file format and the folder structure are documented [here](./dsp-tools-excel2json.md).



### Create the "lists" section of a JSON project file from Excel files

This command creates the "lists" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2lists [options] folder output.json
```

The following options are available:

- `-v` | `--verbose` (optional): If set, more information about the progress is printed to the console.

The expected Excel file format and the folder structure are documented [here](./dsp-tools-excel2json.md#lists-section).

| Hint                                                                                                      |
|-----------------------------------------------------------------------------------------------------------|
| The command [`excel2json`](#create-a-json-project-file-from-excel-files) might be more convenient to use. |



### Create the "resources" section of a JSON project file from an Excel file

This command creates the "resources" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2resources excel_file.xlsx output_file.json
```

The expected Excel format is [documented here](./dsp-tools-excel2json.md#resources-section).

| Hint                                                                                                      |
|-----------------------------------------------------------------------------------------------------------|
| The command [`excel2json`](#create-a-json-project-file-from-excel-files) might be more convenient to use. |



### Create the "properties" section of a JSON project file from an Excel file

This command creates the "properties" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2properties excel_file.xlsx output_file.json
```

The expected Excel format is [documented here](./dsp-tools-excel2json.md#properties-section).

| Hint                                                                                                      |
|-----------------------------------------------------------------------------------------------------------|
| The command [`excel2json`](#create-a-json-project-file-from-excel-files) might be more convenient to use. |



## Create an XML file from Excel/CSV

This command converts a data source 
that is already structured according to the DSP specifications 
to XML.
This is mostly used for DaSCH-internal data migration.

```bash
dsp-tools excel2xml data-source.xlsx project_shortcode ontology_name
```

Arguments:

 - data-source.xlsx (mandatory): An Excel/CSV file that is structured as explained below
 - project_shortcode (mandatory): The four-digit hexadecimal shortcode of the project
 - ontology_name (mandatory): the name of the ontology that the data belongs to

The expected Excel format is [documented here](./dsp-tools-excel2xml-file-format.md).

If your data source is not yet structured according to the DSP specifications, 
you need a custom Python script for the data transformation. 
For this, you might want to import the module `excel2xml` into your Python script, 
which is described in the next paragraph.



## Use the module `excel2xml` to convert a data source to XML

DSP-TOOLS assists you 
in converting a data source in CSV/XLS(X) format 
to an XML file. 
Unlike the other features of DSP-TOOLS, 
this doesn't work via command line, 
but via helper methods that you can import into your own Python script. 
Because every data source is different, 
there is no single algorithm to convert them to a DSP conform XML. 
Every user has to deal with the specialties of their data source, 
but `excel2xml`'s helper methods can help a lot. 
Read more about it [here](./dsp-tools-excel2xml.md).



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

An internal ID is used in the `<resptr>` tag of an XML file to reference resources inside the same XML file. Once data 
is uploaded to DSP, it cannot be referenced by this internal ID anymore. Instead, the resource's IRI has to be used. 
After a successful `xmlupload`, the mapping of internal IDs to their respective IRIs is written to a file
called `id2iri_mapping_[timstamp].json`.
After a successful upload of the data, an output file is written (called `id2iri_mapping_[timstamp].json`) with the 
mapping of internal IDs used inside the XML and their corresponding IRIs which uniquely identify them inside DSP. This 
file should be kept if data is later added with the `--incremental` option. 

To do an incremental XML upload, one of the following procedures is recommended.

- Incremental XML upload with use of internal IDs:
     1. Initial XML upload with internal IDs.
     2. The file `id2iri_mapping_[timestamp].json` is created.
     3. Create new XML file(s) with resources referencing other resources by their internal IDs in `<resptr>` (using the same IDs as in the initial XML upload).
     4. Run `dsp-tools id2iri new_data.xml id2iri_mapping_[timestamp].json` to replace the internal IDs in `new_data.xml` with IRIs. Only internal IDs inside the `<resptr>` tag are replaced.
     5. Run `dsp-tools xmlupload --incremental new_data.xml` to upload the data to DSP.
- Incremental XML Upload with the use of IRIs: Use IRIs in the XML to reference existing data on the DSP server.





## Start a DSP stack on your local machine 

DSP-API is the heart of the DaSCH service platform. It is a server application for storing data from the Humanities. 
DSP-APP is a generic user interface for the user to look at and work with data stored in DSP-API. It's a server 
application, too. For testing purposes, it is sometimes necessary to run DSP-API and DSP-APP on a local machine. 
There are two ways to do this:

 - simple: run `dsp-tools start-stack`
 - advanced: execute commands from within the DSP-API/DSP-APP repositories

Here's an overview of the two ways:

|                             | simple                      | advanced                                                                 |
|-----------------------------|-----------------------------|--------------------------------------------------------------------------|
| target group                | researchers, RDU employees  | developers of DSP-API or DSP-APP                                         |
| how it works                | run `dsp-tools start-stack` | execute commands from within locally cloned DSP-API/DSP-APP repositories |
| software dependencies       | Docker, Python, DSP-TOOLS   | XCode command line tools, Docker, sbt, Java, Angular, node, yarn         |
| mechanism in the background | run pre-built Docker images | build DSP-API and DSP-APP from a branch in the repository                |
| available versions          | latest released version     | any branch, or locally modified working tree                             |
| caveats                     |                             | dependencies must be kept up to date                                     |



### Simple way: `dsp-tools start-stack`

This command runs Docker images with the latest released versions of DSP-API and DSP-APP, i.e. the versions that are 
running on [https://admin.dasch.swiss](https://admin.dasch.swiss). The only prerequisite for this is that Docker 
is running, and that you have Python and DSP-TOOLS installed. Just type:

```
dsp-tools start-stack
```

**dsp-tools will ask you for permission to clean Docker with a `docker system prune`. This will remove all unused 
containers, networks and images. If you don't know what that means, just type `y` ("yes") and then `Enter`.**

The following options are available:

- `--max_file_size=int` (optional, default: `250`): max. multimedia file size allowed by SIPI, in MB (max: 100'000)
- `--prune` (optional): if set, execute `docker system prune` without asking the user
- `--no-prune` (optional): if set, don't execute `docker system prune` (and don't ask)

Example: If you start the stack with `dsp-tools start-stack --max_file_size=1000`, it will be possible to upload files 
that are up to 1 GB big. If a file bigger than `max_file_size` is uploaded, SIPI will reject it.

When your work is done, shut down DSP-API and DSP-APP with

```
dsp-tools stop-stack
```

This command deletes all Docker volumes, and removes all data that was in the database.

Some notes:

 - As long as you want to keep the data in the database, don't execute `dsp-tools stop-stack`. 
 - It is possible to leave DSP-API up for a long time. If you want to save power, you can pause Docker. When you resume 
   it, DSP-API will still be running, in the state how you left it.
 - You can also send your computer to sleep while the DSP stack is running. For this, you don't even need to pause 
   Docker.
 - This command was developed for DaSCH-internal use only. We don't offer support or troubleshooting for it.


#### When should I restart DSP-API?
After creating a data model and adding some data in your local DSP stack, you can work on DSP as if it was the live 
platform. But there are certain actions that are irreversible or can only be executed once, e.g. uploading the same JSON 
project file. If you edit your data model in the JSON file, and then you want to upload it a second time, DSP-API will 
refuse to create the same project again. So, you might want to restart the stack and start over again from a clean setup.

It is possible, however, to modify the XML data file and upload it again and again. But after some uploads, DSP is 
cluttered with data, so you might want to restart the stack.



### Advanced way

If you want to run a specific branch of DSP-API / DSP-APP, or to modify them yourself, you need to:

 - install the dependencies (check [https://github.com/dasch-swiss/dsp-api](https://github.com/dasch-swiss/dsp-api) and 
   [https://github.com/dasch-swiss/dsp-app](https://github.com/dasch-swiss/dsp-app) how to do it)
 - keep the dependencies up to date (keep in mind that dependencies might be replaced over time)
 - clone the repositories from GitHub
 - keep them up to date with `git pull`
 - execute commands from within the repositories (`make` for DSP-API, `angular` for DSP-APP)
 - take care that the repositories don't get cluttered with old data over time
