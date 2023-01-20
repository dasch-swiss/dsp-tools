[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Incremental xmlupload

When uploading data with `dsp-tools xmlupload`,
resources can reference each other with an internal ID,
e.g. in the `<resptr>` tag.
Once the data is in DSP,
the resources cannot be referenced by their internal ID anymore.
Instead, the resource's IRI has to be used.
After a successful `xmlupload`, 
the mapping of internal IDs to their respective IRIs 
is written to a file called `id2iri_mapping_[timestamp].json`.

What is this mapping used for?
It can happen that at a later point of time,
additional data is uploaded.
Depending on what kind of references the additional data contains,
there are 3 cases how this can happen:

1. no references to existing resources: normal xmlupload
2. references to existing resources via IRIs: incremental xmlupload
3. references to existing resources via internal IDs: first id2iri, then incremental xmlupload



## 1. No references to existing resources

The first case is the simplest one. 
Nothing has to be considered. 
The additional data can be uploaded with 

```bash
dsp-tools xmlupload additional_data.xml
```



## 2. References to existing resources via IRIs

The second case is relatively easy, too:
The file `additional_data.xml` contains references like `<resptr>http://rdfh.ch/4123/nyOODvYySV2nJ5RWRdmOdQ</resptr>`. 
Such a file can be uploaded with 

```bash
dsp-tools xmlupload --incremental additional_data.xml
```



## 3. References to existing resources via internal IDs

The third case, however, is a bit more complicated:
The file `additional_data.xml` contains references like `<resptr>book_1</resptr>`,
where `book_1` was the internal ID of a resource that had previously been uploaded to DSP.
Before such an XML file can be uploaded,
its internal IDs need to be replaced by their respective IRIs.
That's where the JSON mapping file comes in:
It contains a mapping from `book_1` to `http://rdfh.ch/4123/nyOODvYySV2nJ5RWRdmOdQ`.



### id2iri

As a first step, 
a new file must be generated 
with the [`id2iri` command](./cli-commands.md#id2iri),
like this:

```bash
dsp-tools id2iri additional_data.xml id2iri_mapping_[timestamp].json --outfile additional_data_replaced.xml
```

| <center>Important</center>                                                                                                                                                              |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Only internal IDs inside the `<resptr>` tag are replaced. Salsah-links inside text properties (e.g. `<a class="salsah-link" href="IRI:book_1:IRI">link to an ID</a>`) are NOT replaced. |



### incremental xmlupload

As second step, the newly generated XML file can be uploaded to DSP:

```bash
dsp-tools xmlupload --incremental additional_data_replaced.xml
```

| <center>Important</center>                                                                                                                      |
|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Internal IDs and IRIs cannot be mixed within the same file. An XML file uploaded with the incremental option must not contain any internal IDs. |
