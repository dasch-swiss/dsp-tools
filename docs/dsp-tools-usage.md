[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Installation and usage

dsp-tools is a Python package with a command line tool that helps you to interact with a DaSCH Service Platform (DSP) 
server. The following paragraphs give you an overview how to install and use dsp-tools.




## Installation

To install the latest version, run:

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
dsp-tools excel2json data_model_files project.json
```

The expected file and folder structures are described [here](./dsp-tools-excel2json.md#json-project-file-from-excel).




### Create the "lists" section of a JSON project file from Excel files

```bash
dsp-tools excel2lists [options] folder output.json
```

The following options are available:

- `-v` | `--verbose` (optional): If set, more information about the progress is printed to the console.

The expected Excel format is [documented here](./dsp-tools-excel2json.md#lists-section).

**Tip: The command [`excel2json`](#create-a-json-project-file-from-excel-files) might be more convenient to use.**



### Create the "resources" section of a JSON project file from an Excel file

```bash
dsp-tools excel2resources excel_file.xlsx output_file.json
```

The command is used to create the resources section of an ontology from an Excel file. Therefore, an Excel file has to
be provided with the data in the first worksheet of the Excel file.

The expected Excel format is [documented here](./dsp-tools-excel2json.md#resources-section).

**Tip: The command [`excel2json`](#create-a-json-project-file-from-excel-files) might be more convenient to use.**




### Create the "properties" section of a JSON project file from an Excel file

```bash
dsp-tools excel2properties excel_file.xlsx output_file.json
```

The command is used to create the properties section of an ontology from an Excel file. Therefore, an Excel file has to
be provided with the data in the first worksheet of the Excel file.

The expected Excel format is [documented here](./dsp-tools-excel2json.md#properties-section).

**Tip: The command [`excel2json`](#create-a-json-project-file-from-excel-files) might be more convenient to use.**



## Create an XML file from Excel/CSV

If your data source is already structured according to the DSP specifications, but it is not in XML format yet, the 
command `excel2xml` will transform it into XML. This is mostly used for DaSCH-interal data migration.

```bash
dsp-tools excel2xml data-source.xlsx project_shortcode ontology_name
```

Arguments:

 - data-source.xlsx (mandatory): An Excel/CSV file that is structured as explained below
 - project_shortcode (mandatory): The four-digit hexadecimal shortcode of the project
 - ontology_name (mandatory): the name of the ontology that the data belongs to

The Excel file must be structured as in this image:  
![img-excel2xml.png](assets/images/img-excel2xml.png)

Some notes:

 - The special tags `<annotation>`, `<link>`, and `<region>` are represented as resources of restype `Annotation`, 
`LinkObj`, and `Region`. 
 - The columns "ark", "iri", and "creation_date" are only used for DaSCH-internal data migration.
 - If `file` is provided, but no `file permissions`, an attempt will be started to deduce them from the resource 
   permissions (`res-default` --> `prop-default` and `res-restricted` --> `prop-restricted`). If this attempt is not 
   successful, a `BaseError` will be raised.

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



## Start a DSP stack on your local machine 

DSP-API is the heart of the DaSCH service platform. It is a server application for storing data from the Humanities.

DSP-APP is a generic user interface for the user to look at and work with data stored in DSP-API. It's a server 
application, too.

For testing purposes, it is sometimes necessary to run DSP-API and DSP-APP on a local machine. There are two ways to 
do this:

 - simple: run `dsp-tools start-stack`
 - advanced: execute commands from within the DSP-API/DSP-APP repositories

Here's an overview:

|                             | simple                      | advanced                                                         |
|-----------------------------|-----------------------------|------------------------------------------------------------------|
| target group                | researchers, RDU employees  | developers of DSP-API or DSP-APP                                 |
| how it works                | run `dsp-tools start-stack` | execute commands from within the DSP-API/DSP-APP repositories    |
| software dependencies       | Docker, Python, dsp-tools   | XCode command line tools, Docker, sbt, Java, Angular, node, yarn |
| mechanism in the background | run Docker containers       | build DSP-API and DSP-APP from a branch in the repository        |
| available versions          | latest deployed versions    | any commit from any branch, or locally modified working tree     |
| caveats                     |                             | dependencies must be kept up to date                             |



### Simple way: `dsp-tools start-stack`

The only prerequisites for this is that your Docker Desktop is running, and that you have Python and dsp-tools 
installed.

```
dsp-tools start-stack
```

This calls Docker commands to start up the latest deployed versions of DSP-API and DSP-APP, i.e. the versions that are 
running on [https://admin.dasch.swiss](https://admin.dasch.swiss). When your work is done, shut down DSP-API and 
DSP-APP with

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
 - **To keep Docker clean, this command regularly executes `docker system prune -f`. It is assumed that people using 
   the simple way don't use Docker for other purposes.**


#### When should I restart DSP-API?
After creating a data model and adding some data in your local DSP stack, you can make experiments and do your stuff. 
But there are certain actions that are destructive or that cannot be undone. There are also steps that can only be 
executed once, e.g. uploading the same JSON project file. If you edit your data model in the JSON file, and then you 
want to upload it a second time, the API will not allow this: You have to shut it down and restart.

It is possible, however, to modify the XML data file and upload it again and again. But after some uploads, you are 
cluttered with data, and you want to restart the stack.



### Advanced way

If you want to run a branch of DSP-API/DSP-APP, or to modify them yourself, you need to 

 - install the dependencies (XCode command line tools, Docker, sbt, Java, Angular, node, yarn)
 - keep the dependencies up to date (they might also change over time)
 - clone the repositories from GitHub
 - keep them up to date with `git pull`
 - execute commands from within the repositories (`make` for DSP-API, `angular` for DSP-APP)
 - take care that the repositories don't get cluttered with old data over time
