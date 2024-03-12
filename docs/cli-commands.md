[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# The CLI Commands of DSP-TOOLS

## Before Starting: Have in Mind the Subdomains of a DSP Server

DaSCH follows some conventions when setting up DSP servers. 
Most of the commands documented on this page
assume that you know how to address the subdomains of a DSP server.
There are three relevant URLs you should know about:

- Subdomains `admin`/`app` stand for the DSP-APP frontend that you look at in your browser
- Subdomain `api` stands for the DSP-API (where DSP-TOOLS sends its data to) 
- Subdomain `iiif` stands for the SIPI server interface (where DSP-TOOLS sends the multimedia files to)

This means that for uploading data to the DSP server 
on the domain `dasch.swiss`, 
you have to type the following:

```bash
dsp-tools xmlupload -s https://api.dasch.swiss -u 'your@email.com' -p 'password' xml_data_file.xml
```

If the user input is not correct,
DSP-TOOLS tries to guess the correct subdomains.
If the provided server is any one of the following:

```text
http(s)://admin.dasch.swiss
http(s)://app.dasch.swiss
http(s)://api.dasch.swiss
http(s)://iiif.dasch.swiss
http(s)://dasch.swiss
dasch.swiss
```

then DSP-TOOLS will treat it as `https://api.dasch.swiss`,
and derive the SIPI server URL `https://iiif.dasch.swiss` from it.

This guessing feature comes with a price, though:

- Only servers ending with `dasch.swiss` are supported.
- If a server's configuration differs from the convention described above, DSP-TOOLS will fail.



## `create`

This command reads a JSON project definition (containing one or more data models)
and creates it on a DSP server.

```bash
dsp-tools create [options] project_definition.json
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
- `-V` | `--validate-only` (optional): validate the JSON file without creating it on the DSP server
- `-l` | `--lists-only` (optional): create only the lists (prerequisite: the project exists on the server)
- `-v` | `--verbose` (optional): print more information about the progress to the console

The defaults are intended for local testing: 

```bash
dsp-tools create project_definition.json
```

This will create the project defined in `project_definition.json` on `localhost` for local viewing.

In order to create the same project
on the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools create -s https://api.dasch.swiss -u 'your@email.com' -p 'password' project_definition.json
```

The expected JSON format is [documented here](./file-formats/json-project/overview.md).



## `get`

This command retrieves a project with its data model(s) from a DSP server 
and writes it into a JSON file. 
This JSON file can then be used 
to create the same project on another DSP server. 

```bash
dsp-tools get [options] project_definition.json
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
- `-P` | `--project` (mandatory): shortcode, shortname or IRI of the project 
- `-v` | `--verbose` (optional): print more information about the progress to the console

The defaults are intended for local testing: 

```bash
dsp-tools get -P my_project project_definition.json
```

will get `my_project` from `localhost`.

In order to get a project from the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools get -s https://api.dasch.swiss -u 'your@email.com' -p 'password' -P my_project project_definition.json
```

It is possible to get a project from a DSP server without giving credentials.
But in this case, the resulting JSON file won't have a "users" section.

The expected JSON format is [documented here](./file-formats/json-project/overview.md).



## `xmlupload`

This command uploads data defined in an XML file to a DSP server. 

```bash
dsp-tools xmlupload [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `-i` | `--imgdir` (optional, default: `.`): folder from where the paths in the `<bitstream>` tags are evaluated
- `-V` | `--validate` (optional): validate the XML file without uploading it
- `--interrupt-after=int` (optional): interrupt the upload after `int` resources have been uploaded

Output:

- A file named `id2iri_mapping_[timestamp].json` is written to the current working directory.
  This file should be kept if a second data delivery is added at a later point of time 
  [see here](./incremental-xmlupload.md).

The defaults are intended for local testing: 

```bash
dsp-tools xmlupload xml_data_file.xml
```

Will upload the data defined in `xml_data_file.xml` on `localhost` for local viewing.

In order to upload the same data 
to the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools xmlupload -s https://api.dasch.swiss -u 'your@email.com' -p 'password' xml_data_file.xml
```

The expected XML format is [documented here](./file-formats/xml-data-file.md).

If an XML upload is interrupted before it finished (e.g. by hitting `Ctrl + C`), 
it can be resumed with the `resume-xmlupload` command. 
When an upload is interrupted, 
the current state of the upload is saved in a pickle file, 
which is stored in `~/.dsp-tools/xmluploads/[server]/resumable/latest.pkl`. 
If the upload should be resumed later,
this file must remain in place.



## `resume-xmlupload`

| <center>Warning</center>                                                    |
|--------------------------------------------------------------------------|
| We do not guarantee that the state of an xmlupload is cleanly saved after `Ctrl + C`. We only guarantee this for `dsp-tools xmlupload --interrupt-after`. |

This command resumes a previously interrupted XML upload.

```bash
dsp-tools resume-xmlupload [options]
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API

For this command to work,
the pickle file `~/.dsp-tools/xmluploads/[server]/resumable/latest.pkl` must exist. 
Currently, only one interrupted upload can be resumed at a time per server.



## `excel2json`

This command creates a JSON project definition file from a nested folder structure with Excel files.

```bash
dsp-tools excel2json excelfolder project_definition.json
```

The expected Excel file format and the folder structure are documented [here](./file-formats/excel2json.md).



### `excel2lists`

This command creates the "lists" section of a JSON project file from Excel files.

```bash
dsp-tools excel2lists [options] excelfolder lists_section.json
```

The following options are available:

- `-v` | `--verbose` (optional): print more information about the progress to the console

The expected Excel file format and the folder structure are documented 
[here](./file-formats/excel2json.md#the-lists-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



### `excel2resources`

This command creates the "resources" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2resources resources.xlsx resources_section.json
```

The expected Excel format is [documented here](./file-formats/excel2json.md#the-resources-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



### `excel2properties`

This command creates the "properties" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2properties properties.xlsx properties_section.json
```

The expected Excel format is [documented here](./file-formats/excel2json.md#the-properties-section).

| <center>Hint</center>                                                    |
|--------------------------------------------------------------------------|
| The command [`excel2json`](#excel2json) might be more convenient to use. |



## `excel2xml`

This command creates an XML file
from an Excel/CSV file that is already structured according to the DSP specifications.
This is mostly used for DaSCH internal data migration.

```bash
dsp-tools excel2xml data_source.xlsx project_shortcode ontology_name
```

Arguments:

- data_source.xlsx (mandatory): path to the CSV or XLS(X) file containing the data
- project_shortcode (mandatory): shortcode of the project that this data belongs to
- ontology_name (mandatory): name of the ontology that the data belongs to

The expected Excel format is [documented here](./file-formats/excel2xml.md).

If your data source is not yet structured according to the DSP specifications, 
you need a custom Python script for the data transformation. 
For this, you might want to import the module `excel2xml` into your Python script, 
which is described [here](./excel2xml-module.md).



## `id2iri`

This command replaces internal IDs of an XML file
(`<resptr>` tags and salsah-links inside `<text>` tags)
by IRIs provided in a mapping file.

```bash
dsp-tools id2iri xmlfile.xml mapping.json
```

The following options are available:

- `-r` | `--remove-resources` (optional): remove resources if their ID is in the mapping 

The output file is written to `[original name]_replaced_[timestamp].xml`.

If the flag `--remove-resources` is set,
all resources of which the ID is in the mapping are removed from the XML file.
This prevents doubled resources on the DSP server,
because normally, the resources occurring in the mapping already exist on the DSP server.

This command cannot be used isolated, 
because it is part of a bigger procedure 
that is documented [here](./incremental-xmlupload.md).



## `start-stack`

This command runs a local instance of DSP-API and DSP-APP.

```bash
dsp-tools start-stack
```

DSP-TOOLS will ask you for permission to clean Docker with a `docker system prune`.
This will remove all unused containers, networks and images.
If you don't know what that means, just type `y` ("yes") and then `Enter`.

The following options are available:

- `--max_file_size=int` (optional, default: `2000`): max. multimedia file size allowed by SIPI, in MB (max: 100'000)
- `--latest` (optional): 
  instead of the latest deployed version,
  use the latest development version of DSP-API (from the `main` branch)
- `--prune` (optional): execute `docker system prune` without asking
- `--no-prune` (optional): don't execute `docker system prune` (and don't ask)

Example: If you start the stack with `dsp-tools start-stack --max_file_size=1000`, 
it will be possible to upload files that are up to 1 GB big. 
If a file bigger than `max_file_size` is uploaded, 
SIPI will reject it.

More help for this command can be found [here](./start-stack.md).



## `stop-stack`

When your work is done, shut down DSP-API and DSP-APP with

```bash
dsp-tools stop-stack
```

This deletes all Docker volumes, and removes all data that was in the database.



## `template`

This command creates a template repository with a minimal JSON and XML file.

```bash
dsp-tools template
```



## `rosetta`

Clone the most up to date [rosetta repository](https://github.com/dasch-swiss/082e-rosetta-scripts)
from GitHub into ~/.dsp-tools,
create its data model
and upload its XML file.

```bash
dsp-tools rosetta
```

A DSP stack must be running before executing this command.
