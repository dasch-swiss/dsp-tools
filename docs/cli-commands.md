[![DSP-TOOLS](https://img.shields.io/github/v/release/dasch-swiss/dsp-tools?include_prereleases&label=DSP-TOOLS)](https://github.com/dasch-swiss/dsp-tools)

# The CLI commands of DSP-TOOLS

## Before starting: Have in mind the subdomains of a DSP server

DaSCH follows some conventions when setting up DSP servers. 
Most of the commands documented on this page
assume that you know how to address the subdomains of a DSP server.
There are three relevant URLs you should know about:

 - Subdomain `admin` stands for the DSP-APP frontend that you look at in your browser
 - Subdomain `api` stands for the DSP-API (where DSP-TOOLS sends its data to) 
 - Subdomain `iiif` stands for the SIPI server interface (where DSP-TOOLS sends the multimedia files to)

This means that for uploading data to a DSP server 
on the domain `dasch.swiss`, 
you have to type the following:

```bash
dsp-tools xmlupload -s https://api.dasch.swiss -u root@example.com -p test -S https://iiif.dasch.swiss xml_data_file.xml
```



## `create`

This command reads a JSON project definition (containing one or more data models)
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

The expected JSON format is [documented here](./file-formats/json-project-overview.md).



## `get`

This command retrieves a project with its data model(s) from a DSP server 
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

The expected JSON format is [documented here](./file-formats/json-project-overview.md).



## `xmlupload`

This command uploads data defined in an XML file to a DSP server. 

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

Output:

- A file named `id2iri_mapping_[timestamp].json` is written to the current working directory.
  This file should be kept if data is later added with the [`--incremental` option](./incremental-xmlupload.md)

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

The expected XML format is [documented here](./file-formats/xml-data-file.md).



## `excel2json`

This command creates a JSON project file from a nested folder structure with Excel files.

``` 
dsp-tools excel2json data_model_files project.json
```

The expected Excel file format and the folder structure are documented [here](./file-formats/excel2json.md).



### `excel2lists`

This command creates the "lists" section of a JSON project file from Excel files.

```bash
dsp-tools excel2lists [options] folder output.json
```

The following options are available:

- `-v` | `--verbose` (optional): If set, more information about the progress is printed to the console.

The expected Excel file format and the folder structure are documented [here](./file-formats/excel2json.md#lists-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



### `excel2resources`

This command creates the "resources" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2resources excel_file.xlsx output_file.json
```

The expected Excel format is [documented here](./file-formats/excel2json.md#resources-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



### `excel2properties`

This command creates the "properties" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2properties excel_file.xlsx output_file.json
```

The expected Excel format is [documented here](./file-formats/excel2json.md#properties-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



## `excel2xml`

This command converts an Excel/CSV file
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

The expected Excel format is [documented here](./file-formats/excel2xml.md).

If your data source is not yet structured according to the DSP specifications, 
you need a custom Python script for the data transformation. 
For this, you might want to import the module `excel2xml` into your Python script, 
which is described [here](./excel2xml-module.md).



## `id2iri`

This command reads an XML file, 
and replaces the internal IDs contained in its `<resptr>` tags
by the respective IRIs from the JSON mapping file.

```bash
dsp-tools id2iri xml_file.xml mapping_file.json --outfile xml_file_replaced.xml
```

The following options are available:

- `--outfile` (optional, default: `id2iri_replaced_[timestamp].xml`): path to the output file

This command cannot be used isolated, 
because it is part of a bigger procedure 
that is documented [here](./incremental-xmlupload.md).




## `start-stack` / `stop-stack`

This command runs DSP-API and DSP-APP on a local machine.

```bash
dsp-tools start-stack
```

dsp-tools will ask you for permission to clean Docker with a `docker system prune`. This will remove all unused 
containers, networks and images. If you don't know what that means, just type `y` ("yes") and then `Enter`.

The following options are available:

- `--max_file_size=int` (optional, default: `250`): max. multimedia file size allowed by SIPI, in MB (max: 100'000)
- `--prune` (optional): if set, execute `docker system prune` without asking the user
- `--no-prune` (optional): if set, don't execute `docker system prune` (and don't ask)

Example: If you start the stack with `dsp-tools start-stack --max_file_size=1000`, 
it will be possible to upload files that are up to 1 GB big. 
If a file bigger than `max_file_size` is uploaded, 
SIPI will reject it.

When your work is done, shut down DSP-API and DSP-APP with

```bash
dsp-tools stop-stack
```

This deletes all Docker volumes, and removes all data that was in the database.

More help for this command can be found [here](./start-stack.md).
