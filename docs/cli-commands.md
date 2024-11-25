[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# The CLI Commands of DSP-TOOLS

## Before Starting: Have in Mind the Subdomains of a DSP Server

DaSCH follows some conventions when setting up DSP servers. 
Most of the commands documented on this page
assume that you know how to address the subdomains of a DSP server.
There are three relevant URLs you should know about:

- Subdomains `admin`/`app` stand for the DSP-APP frontend that you look at in your browser
- Subdomain `api` stands for the DSP-API (where DSP-TOOLS sends its data to) 
- Subdomain `ingest` stands for the ingest server interface (where DSP-TOOLS uploads multimedia files to)

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
http(s)://ingest.dasch.swiss
http(s)://dasch.swiss
dasch.swiss
```

then DSP-TOOLS will treat it as `https://api.dasch.swiss`,
and derive the ingest server URL `https://ingest.dasch.swiss` from it.

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
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

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
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

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
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)
- `--no-iiif-uri-validation` (optional): don't check if the IIIF links are valid URLs that can be reached online.

Output:

- A file named `id2iri_mapping_[timestamp].json` is written to the current working directory.
  This file should be kept if a second data delivery is added at a later point of time 
  [see here](./incremental-xmlupload.md).

The defaults are intended for local testing: 

```bash
dsp-tools xmlupload xml_data_file.xml
```

will upload the data defined in `xml_data_file.xml` on `localhost` for local viewing.

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

| <center>Warning</center>                                                                                                                                  |
| --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| We do not guarantee that the state of an xmlupload is cleanly saved after `Ctrl + C`. We only guarantee this for `dsp-tools xmlupload --interrupt-after`. |

This command resumes a previously interrupted `xmlupload` or `ingest-xmlupload`.

```bash
dsp-tools resume-xmlupload [options]
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `--skip-first-resource` (optional): the `xmlupload` should skip the first saved resource. 
  This is not implemented for stashed links.
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

For this command to work,
the pickle file `~/.dsp-tools/xmluploads/[server]/resumable/latest.pkl` must exist. 
Currently, only one interrupted upload can be resumed at a time per server.



## New workflow for xmlupload

| <center>Warning</center>                                          |
| ----------------------------------------------------------------- |
| These commands are experimental. They might change in the future. |

This new workflow consists of 3 commands:

- [`upload-files`](#upload-files): upload all files that are referenced in an XML file to a DSP server
- [`ingest-files`](#ingest-files): kick off the ingest process, and retrieve the mapping CSV when it is finished
- [`ingest-xmlupload`](#ingest-xmlupload): create the resources contained in the XML file, using the mapping CSV


### `upload-files`

This command uploads all files referenced in the `<bitstream>` tags of an XML file to a server
(without any processing/ingesting).

```bash
dsp-tools upload-files [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `-i` | `--imgdir` (optional, default: `.`): folder from where the paths in the `<bitstream>` tags are evaluated
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The defaults are intended for local testing: 

```bash
dsp-tools upload-files xml_data_file.xml
```

will upload the files referenced in the `<bitstream>` tags of `xml_data_file.xml` onto `localhost`, for local viewing.

In order to upload the same data to the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools upload-files -s https://api.dasch.swiss -u 'your@email.com' -p 'password' xml_data_file.xml
```

The expected XML format is [documented here](./file-formats/xml-data-file.md).


### `ingest-files`

This command kicks off the ingest process on the server, and waits until it has completed.
Then, it saves the mapping CSV in the current working directory.
The mapping CSV contains a mapping from the original file paths on your machine 
to the internal filenames of the ingested files on the target server.
This mapping is necessary for the next step ([`ingest-xmlupload`](#ingest-xmlupload)).

In order for this to work, the files of the indicated project 
must first be uploaded with [`upload-files`](#upload-files).

**This command might take hours or days until it returns,**
**because it waits until the ingest process on the server has completed.**
**Instead of waiting, you might also kill this process, and execute it again later.**

```bash
dsp-tools ingest-files [options] <shortcode>
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The defaults are intended for local testing: 

```bash
dsp-tools ingest-files 082E
```

will ingest the files of the project `082E` on `localhost` for local viewing.

In order to ingest the same data on the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools ingest-files -s https://api.dasch.swiss -u 'your@email.com' -p 'password' 082E
```


## `ingest-xmlupload`

This command creates all resources defined in an XML file on a DSP server. 
In order for this to work, the files referenced in the XML file 
must first be uploaded with [`upload-files`](#upload-files),
and then be ingested with [`ingest-files`](#ingest-files).

The mapping CSV file that was created by [`ingest-files`](#ingest-files) 
must be present in the current working directory.

```bash
dsp-tools xmlupload [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `--interrupt-after=int` (optional): interrupt the upload after `int` resources have been uploaded
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The defaults are intended for local testing: 

```bash
dsp-tools ingest-xmlupload xml_data_file.xml
```

will create the resources contained in `xml_data_file.xml` on `localhost` for local viewing.

In order to create the same resources on the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools ingest-xmlupload -s https://api.dasch.swiss -u 'your@email.com' -p 'password' xml_data_file.xml
```



## `excel2json`

This command creates a JSON project definition file from a nested folder structure with Excel files.
It will be deprecated in favor of [`new-excel2json`](#new-excel2json) in the future.

```bash
dsp-tools excel2json excelfolder project_definition.json
```

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The expected Excel file format and the folder structure are documented [here](./file-formats/excel2json.md).


### `excel2lists`

This command creates the "lists" section of a JSON project file from Excel files.
It will be deprecated in favor of `new-excel2lists` in the future.

```bash
dsp-tools excel2lists [options] excelfolder lists_section.json
```

The following options are available:

- `-v` | `--verbose` (optional): print more information about the progress to the console
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The expected Excel file format and the folder structure are documented 
[here](./file-formats/excel2json.md#the-lists-section).

| <center>Hint</center>                                                    |
| ------------------------------------------------------------------------ |
| The command [`excel2json`](#excel2json) might be more convenient to use. |


### `excel2resources`

This command creates the "resources" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2resources resources.xlsx resources_section.json
```

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The expected Excel format is [documented here](./file-formats/excel2json.md#the-resources-section).

| <center>Hint</center>                                                    |
| ------------------------------------------------------------------------ |
| The command [`excel2json`](#excel2json) might be more convenient to use. |



### `excel2properties`

This command creates the "properties" section of a JSON project file from an Excel file.

```bash
dsp-tools excel2properties properties.xlsx properties_section.json
```

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The expected Excel format is [documented here](./file-formats/excel2json.md#the-properties-section).

| <center>Hint</center>                                                    |
| ------------------------------------------------------------------------ |
| The command [`excel2json`](#excel2json) might be more convenient to use. |



## `new-excel2json`

This command creates a JSON project definition file from a nested folder structure with Excel files.
The Excel format for the `lists` section has been adapted compared to the previous [`excel2json`](#excel2json) command.
This command is still under development, and might be less stable than `excel2json`.

```bash
dsp-tools new-excel2json excelfolder project_definition.json
```

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The expected Excel file format and the folder structure are documented 
[here](./file-formats/excel2json.md#the-folder-structure-for-new-excel2json).


### `new-excel2lists`

This command creates the "lists" section of a JSON project file from Excel files.
The Excel format for the `lists` section has been adapted compared to the previous `excel2lists` command.
This command is still under development, and might be less stable than `excel2lists`.

```bash
dsp-tools new-excel2lists excelfolder lists_section.json
```

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The expected Excel file format and the folder structure are documented 
[here](./file-formats/excel2json.md#the-lists-section-for-new-excel2json-and-new-excel2lists).



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

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

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
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

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

- `--max_file_size=int` (optional, default: `2000`): max. multimedia file size allowed, in MB (max: 100'000)
- `--latest` (optional): 
  instead of the latest deployed version,
  use the latest development version (from the `main` branch)
  of the backend components (api, sipi, fuseki, ingest)
- `--prune` (optional): execute `docker system prune` without asking
- `--no-prune` (optional): don't execute `docker system prune` (and don't ask)
- `--with-test-data` (optional): start the stack with some test data
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

Example: If you start the stack with `dsp-tools start-stack --max_file_size=1000`, 
it will be possible to upload files that are up to 1 GB big. 
If a file bigger than `max_file_size` is uploaded, 
the upload will be rejected.

More help for this command can be found [here](./start-stack.md).

!!! note "Login credentials for DSP-APP"

    To gain system administration rights inside a locally running DSP-APP, 
    login with username `root@example.com` and password `test`.


## `stop-stack`

When your work is done, shut down DSP-API and DSP-APP with

```bash
dsp-tools stop-stack
```

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

This deletes all Docker volumes, and removes all data that was in the database.



## `template`

This command creates a template repository with a minimal JSON and XML file.

```bash
dsp-tools template
```

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)



## `rosetta`

Clone the most up to date [rosetta repository](https://github.com/dasch-swiss/082e-rosetta-scripts)
from GitHub into ~/.dsp-tools,
create its data model
and upload its XML file.

```bash
dsp-tools rosetta
```

The following options are available:

- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

A DSP stack must be running before executing this command.
