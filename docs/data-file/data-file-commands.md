[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)


# Validating and Uploading Data

CLI-Commands for validating and uploading your data.

## `validate-data`

This command validates an XML data file according to the ontology previously uploaded on the server. 

```bash
dsp-tools validate-data [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP-API server where DSP-TOOLS gets the ontology from
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `--ignore-duplicate-files-warning` (optional): don't check if multimedia files are referenced more than once
- `--skip-ontology-validation` (optional): don't validate the ontology itself, only the data.
  This is intended for projects that are already on the production server
- `--save-graphs` (optional): if you want to save the graphs required for the validation as turtle files. 
  This is primarily intended for development use.

Output:

- The result of the validation is printed out on the console.
- If there are more than 50 validation errors, 
  a csv called `[xml_data_file]_validation_[severity].csv` with the results is saved in the current directory.
- There are three severity levels:
    - **Error**: Will block an xmlupload.
        - Content that is wrong for various reasons.
        - For example, invalid values, empty values, data that does not conform to the definition in the data model.
    - **Warning**: Will block an xmlupload on PROD and on RDU-stage
        - During RDU work on a test server the data may be incomplete. 
          To facilitate easy testing some errors are permissible on test servers but not on a production server. 
        - For example, legal information for assets is mandatory on a production server. 
          Since a project may need time to compile all the data we allow missing legal information on test servers.
    - **Info**: Will not block an xmlupload.
        - Content that may cause errors during an upload. 
        - For example, if you reference IRIs from resources that are already in the database,
          you will get an info message.
          The reason is, that if the resource does not exist, an xmlupload will fail.


The defaults are intended for local testing: 

```bash
dsp-tools validate-data xml_data_file.xml
```

will validate the data defined in `xml_data_file.xml` on `localhost`.

In order to validate the same data 
with the ontology on a DSP server it is necessary to specify the server and provide login credentials


```bash
dsp-tools validate-data -s https://api.dasch.swiss -u 'your@email.com' -p 'password' xml_data_file.xml
```


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
- `--skip-validation` (optional): skip the SHACL schema validation
- `--ignore-duplicate-files-warning` (optional): don't check if multimedia files are referenced more than once
- `--skip-ontology-validation` (optional): don't validate the ontology itself, only the data.
  This is intended for projects that are already on the production server
- `--validation-severity` (optional, default: `info`): which severity level of messages 
  will be printed out during validation. 
  Options: `info`, `warning`, and `error` 
  (each level of severity includes the higher levels; see [`validate-data`](#validate-data) for details).

Output:

- A file named `id2iri_mapping_[timestamp].json` is written to the current working directory.
  This file should be kept if a second data delivery is added at a later point of time 
  [see here](../special-workflows/incremental-xmlupload.md).

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

The expected XML format is [documented here](./xml-data-file.md).

If an XML upload is interrupted before it finished (e.g. by hitting `Ctrl + C`), 
it can be resumed with the `resume-xmlupload` command. 
When an upload is interrupted, 
the current state of the upload is saved in a pickle file, 
which is stored in `~/.dsp-tools/xmluploads/[server]/resumable/latest.pkl`. 
If the upload should be resumed later,
this file must remain in place.


## `resume-xmlupload`

!!! warning 

    We do not guarantee that the state of an xmlupload is cleanly saved after `Ctrl + C`.
    We only guarantee this for `dsp-tools xmlupload --interrupt-after`.

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
that is documented [here](../special-workflows/incremental-xmlupload.md).
