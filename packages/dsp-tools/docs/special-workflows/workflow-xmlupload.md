[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Special Workflows for `xmluploads`


## CLI Commands

This new workflow consists of 3 commands:

- [`upload-files`](#upload-files): upload all files that are referenced in an XML file to a DSP server
- [`ingest-files`](#ingest-files): kick off the ingest process, and retrieve the mapping CSV when it is finished
- [`ingest-xmlupload`](#ingest-xmlupload): create the resources contained in the XML file, using the mapping CSV

[`delete-data-import`](#delete-data-import) deletes a bulk data import that `ingest-xmlupload` left on the server.


### `upload-files`

This command uploads all files referenced in the `<bitstream>` tags of an XML file to a server
(without any processing/ingesting).

```bash
uvx dsp-tools upload-files [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API.
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `-i` | `--imgdir` (optional, default: `.`): folder from where the paths in the `<bitstream>` tags are evaluated
- `--suppress-update-prompt` (optional): don't check for or warn about an outdated version of DSP-TOOLS 
  (useful in non-interactive contexts, e.g. when the Terminal output is piped into a file)

The defaults are intended for local testing: 

```bash
uvx dsp-tools upload-files xml_data_file.xml
```

will upload the files referenced in the `<bitstream>` tags of `xml_data_file.xml` onto `localhost`, for local viewing.

In order to upload the same data to the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
uvx dsp-tools upload-files -s https://api.dasch.swiss -u '<shortname>@admin.dasch.swiss' -p 'password' xml_data_file.xml
```

On production, use the [project admin account](../production-account.md) of the project.

The expected XML format is [documented here](../data-file/xml-data-file.md).


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
uvx dsp-tools ingest-files [options] <shortcode>
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `--suppress-update-prompt` (optional): don't check for or warn about an outdated version of DSP-TOOLS 
  (useful in non-interactive contexts, e.g. when the Terminal output is piped into a file)

The defaults are intended for local testing: 

```bash
uvx dsp-tools ingest-files 082E
```

will ingest the files of the project `082E` on `localhost` for local viewing.

In order to ingest the same data on the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
uvx dsp-tools ingest-files -s https://api.dasch.swiss -u '<shortname>@admin.dasch.swiss' -p 'password' 082E
```

On production, use the [project admin account](../production-account.md) of the project.


### `ingest-xmlupload`

This command creates all resources defined in an XML file on a DSP server, as one bulk data import.
In order for this to work, the files referenced in the XML file 
must first be uploaded with [`upload-files`](#upload-files),
and then be ingested with [`ingest-files`](#ingest-files).

The mapping CSV file that was created by [`ingest-files`](#ingest-files) 
must be present in the current working directory.

```bash
uvx dsp-tools ingest-xmlupload [options] xml_data_file.xml
```

!!! Attention

    Only system admins can run `ingest-xmlupload`.
    The credentials of a project admin or a project member are not enough.

The most frequently used options are:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) of a system admin
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `--on-behalf-of-user` (mandatory): email or username of the user who becomes the creator of the resources.
  This user must be an active member of the project with create rights, and must not be a system admin.
  On a production-like server, DSP-TOOLS asks for confirmation 
  unless the user is `<shortname>@admin.dasch.swiss`.
- `--skip-validation` (optional): skip the SHACL validation of the data before the import
- `--no-iiif-uri-validation` (optional): do not validate the IIIF URIs
- `--skip-ontology-validation` (optional): validate only the data, not the data model

!!! info "The on-behalf-of user decides the default permissions"

    The data belongs to the on-behalf-of user, not to the system admin who runs the command.
    If a resource or a value in the XML file has no permissions, 
    DSP-API gives it the default permissions of the project for the role of this user
    (see [Permissions](../permissions-guide.md)).
    Thus, a project admin and a project member as on-behalf-of user can lead to different permissions.
    If the project has no default permissions for the role of this user, 
    the data gets `CR knora-admin:Creator`: apart from admins, only the on-behalf-of user can see and change it.

To see all possible options, type `uvx dsp-tools ingest-xmlupload --help`.

The defaults are intended for local testing: 

```bash
uvx dsp-tools ingest-xmlupload --on-behalf-of-user 'user@example.com' xml_data_file.xml
```

will create the resources contained in `xml_data_file.xml` on `localhost` for local viewing.

In order to create the same resources on the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
uvx dsp-tools ingest-xmlupload -s https://api.dasch.swiss -u 'system-admin@example.com' -p 'password' \
    --on-behalf-of-user '<shortname>@admin.dasch.swiss' xml_data_file.xml
```


#### Precondition

As of November 2026, DSP-API accepts a bulk data import only if the project holds no data, except list nodes.
The ontologies of the project must exist.
Use `ingest-xmlupload` only for the first import of data into a project.


#### What Happens

DSP-TOOLS validates the data, then sends all resources to the server in one bulk data import.
The server creates the resources, values, and files together, or none of them.
If a resource has a preset IRI or ARK in the XML file, DSP-TOOLS keeps it. 
It must belong to the project.

DSP-TOOLS writes these files to `~/.dsp-tools/data-imports/<server>/`:

| File                                 | Content                                                                |
| ------------------------------------ | ---------------------------------------------------------------------- |
| `<shortcode>_<timestamp>_payload.jsonld` | the data that DSP-TOOLS sends to the server (the payload)              |
| `<shortcode>_<timestamp>_id2iri.json`| the mapping of internal IDs to IRIs, written before the data is sent   |
| `<shortcode>_<import_id>_error.txt`  | the error message of the server, written only if the import fails      |

After a successful import, DSP-TOOLS removes the payload and the `_id2iri.json` file.
It writes the mapping of internal IDs to IRIs to `id2iri_<shortcode>_<server>_<timestamp>.json` 
in the current working directory.


#### If the Import Fails

If the server reports an error, DSP-TOOLS prints the first lines of the error message, 
writes the full message to the `_error.txt` file, 
and deletes the import task on the server.
If the server sends no error message, DSP-TOOLS writes no file.
The payload and the `_id2iri.json` file stay in the folder.
The project holds no data after a failed import. 
Correct the problem and run `ingest-xmlupload` again.


#### If the Command Is Interrupted

If you hit `Ctrl + C`, or the connection to the server is lost, 
the import task can stay on the server, and it can still complete.
DSP-TOOLS keeps the payload and the `_id2iri.json` file, 
and prints the ID of the import task and the command to delete it.
An import task blocks further imports of the project until it is deleted.
Use [`delete-data-import`](#delete-data-import) to delete it.
If the task completed, the data is on the server, and the `_id2iri.json` file holds the mapping of internal IDs to IRIs.
Otherwise, delete the task and run `ingest-xmlupload` again: it has no resume.


### `delete-data-import`

This command deletes a bulk data import task from a DSP server.

```bash
uvx dsp-tools delete-data-import [options] shortcode import_id
```

- `shortcode`: the shortcode of the project
- `import_id`: the ID of the import task, as printed by `ingest-xmlupload`
- `-s` | `--server`, `-u` | `--user`, `-p` | `--password`: as for `ingest-xmlupload`

Only system admins can run this command.
It does not delete an import that is still running.
If the import failed, the command prints the first lines of the error message,
and writes the full message to `<shortcode>_<import_id>_error.txt`
in `~/.dsp-tools/data-imports/<server>/` before it deletes the task.


## Incremental `xmlupload`

`ingest-xmlupload` has no incremental upload.

When uploading data with the [`xmlupload`](../data-file/data-file-commands.md#xmlupload) command,
resources can reference each other with an internal ID,
e.g. in the `<resptr>` tag.
Once the data is in DSP,
the resources cannot be referenced by their internal ID anymore.
Instead, the resource's IRI which was generated by the DSP has to be used.
After a successful `xmlupload`, 
the mapping of internal IDs to their respective IRIs 
is written to a file called `id2iri_mapping_[timestamp].json`.

The mapping is necessary if at a later point in time additional data should be uploaded.
Depending on the type of references the additional data contains,
there are 4 different ways how new data has to be uploaded:

1. no references to existing resources: normal xmlupload
2. references to existing resources via IRIs: incremental xmlupload
3. references to existing resources via internal IDs: first id2iri, then incremental xmlupload
4. continue an interrupted xmlupload: first id2iri, then incremental xmlupload



### 1. No References to Existing Resources

The first case is the simplest one:
No mapping is required, and the additional data can be uploaded with:

```bash
uvx dsp-tools xmlupload additional_data.xml
```



### 2. References to Existing Resources Via IRIs

The second case is relatively easy, too:
The file `additional_data.xml` contains references like `<resptr>http://rdfh.ch/4123/nyOODvYySV2nJ5RWRdmOdQ</resptr>`. 
Such a file can be uploaded with:

```bash
uvx dsp-tools xmlupload additional_data.xml
```



### 3. References to Existing Resources Via Internal IDs

The third case, however, is a bit more complicated:
The file `additional_data.xml` contains references like `<resptr>book_1</resptr>`,
or `<text><a class="salsah-link" href="IRI:book_1:IRI">link to book_1</a></text>`,
where `book_1` was the internal ID of a resource that had previously been uploaded to DSP.

Before such an XML file can be uploaded,
the internal IDs must be replaced with their respective IRIs.
That's where the JSON mapping file comes in:
It contains a mapping from `book_1` to `http://rdfh.ch/4123/nyOODvYySV2nJ5RWRdmOdQ`.

As a first step, 
a new file must be generated 
with the [`id2iri` command](../data-file/data-file-commands.md#id2iri):

```bash
uvx dsp-tools id2iri additional_data.xml id2iri_mapping_[timestamp].json
```

In a second step, the newly generated XML file can be uploaded to DSP:

```bash
uvx dsp-tools xmlupload additional_data_replaced_[timestamp].xml
```



### 4. Continue an Interrupted Xmlupload

If a xmlupload didn't finish successfully, 
some resources have already been created, while others have not.
If one of the remaining resources references an already created resource by its internal ID,
this internal ID must be replaced by the IRI of the already created resource.

Additionally, the already created resources must be removed from the XML file.
Otherwise, they would be created a second time.

In such a case, proceed as follows:

1. Initial xmlupload: `uvx dsp-tools xmlupload data.xml`
2. A crash happens. Some resources have been uploaded, and a `id2iri_mapping_[timestamp].json` file has been written
3. Fix the reason for the crash
4. Replace the internal IDs and remove the created resources with: 
   `uvx dsp-tools id2iri data.xml --remove-resources id2iri_mapping_[timestamp].json`
5. Upload the outputted XML file with `uvx dsp-tools xmlupload data_replaced_[timestamp].xml`



