[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Special Workflows for `xmluploads`


## CLI Commands

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
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API.
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


### `ingest-xmlupload`

This command creates all resources defined in an XML file on a DSP server. 
In order for this to work, the files referenced in the XML file 
must first be uploaded with [`upload-files`](#upload-files),
and then be ingested with [`ingest-files`](#ingest-files).

The mapping CSV file that was created by [`ingest-files`](#ingest-files) 
must be present in the current working directory.

```bash
dsp-tools ingest-xmlupload [options] xml_data_file.xml
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server where DSP-TOOLS sends the data to
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `--interrupt-after=int` (optional): interrupt the upload after `int` resources have been uploaded
- `--skip-validation` (optional): skip the SHACL schema validation
- `--skip-ontology-validation` (optional): don't validate the ontology itself, only the data.
  This is intended for projects that are already on the production server
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


## Incremental `xmlupload`

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
dsp-tools xmlupload additional_data.xml
```



### 2. References to Existing Resources Via IRIs

The second case is relatively easy, too:
The file `additional_data.xml` contains references like `<resptr>http://rdfh.ch/4123/nyOODvYySV2nJ5RWRdmOdQ</resptr>`. 
Such a file can be uploaded with:

```bash
dsp-tools xmlupload additional_data.xml
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
dsp-tools id2iri additional_data.xml id2iri_mapping_[timestamp].json
```

In a second step, the newly generated XML file can be uploaded to DSP:

```bash
dsp-tools xmlupload additional_data_replaced_[timestamp].xml
```



### 4. Continue an Interrupted Xmlupload

If a xmlupload didn't finish successfully, 
some resources have already been created, while others have not.
If one of the remaining resources references an already created resource by its internal ID,
this internal ID must be replaced by the IRI of the already created resource.

Additionally, the already created resources must be removed from the XML file.
Otherwise, they would be created a second time.

In such a case, proceed as follows:

1. Initial xmlupload: `dsp-tools xmlupload data.xml`
2. A crash happens. Some resources have been uploaded, and a `id2iri_mapping_[timestamp].json` file has been written
3. Fix the reason for the crash
4. Replace the internal IDs and remove the created resources with: 
   `dsp-tools id2iri data.xml --remove-resources id2iri_mapping_[timestamp].json`
5. Upload the outputted XML file with `dsp-tools xmlupload data_replaced_[timestamp].xml`
