[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Excel files for data modelling and data import

dsp-tools is able to process Excel files and output the appropriate JSON or XML file. The JSON/XML file can then be
used to create the ontology on the DSP server or import data to the DSP repository. dsp-tools can also be used to 
create a list from an Excel file.




## Create the resources for a data model from an Excel file

With dsp-tools, the `resources` section used in a data model (JSON) can be created from an Excel file. The command for 
this is documented [here](./dsp-tools-usage.md#create-the-resources-section-of-a-json-project-file-from-an-excel-file). 
Only `XLSX` files are allowed. The `resources` section can be inserted into the ontology file and then be uploaded onto 
a DSP server.

**An Excel file template can be found [here](assets/templates/resources_template.xlsx). It is recommended to work from 
the template.**

The expected worksheets of the Excel file are:

- `classes`: a table with all resource classes intended to be used in the resulting JSON
- `class1`, `class2`,...: a table for each resource class named after its name

The worksheet called `classes` must have the following structure: 
![img-resources-example-1.png](assets/images/img-resources-example-1.png)

The expected columns are:

- `name` (mandatory): The name of the resource
- `en`, `de`, `fr`, `it`, `rm`: The labels of the resource in different languages, at least one language has to be provided
- `comment_en`, `comment_de`, `comment_fr`, `comment_it`, `comment_rm` (optional): comments in the respective language 
- `super` (mandatory): The base class(es) of the resource, separated by commas

The optional columns may be omitted in the Excel.

All other worksheets, one for each resource class, have the following structure:
![img-resources-example-2.png](assets/images/img-resources-example-2.png){ width=50% }

The expected columns are:

- `Property` (mandatory): The name of the property
- `Cardinality` (mandatory): The cardinality, one of: `1`, `0-1`, `1-n`, `0-n`

The GUI order is given by the order in which the properties are listed in the Excel sheet.

For further information about resources, see [here](./dsp-tools-create-ontologies.md#resources).




## Create the properties for a data model from an Excel file

With dsp-tools, the `properties` section used in a data model (JSON) can be created from an Excel file. The command for 
this is documented [here](./dsp-tools-usage.md#create-the-properties-section-of-a-json-project-file-from-an-excel-file). 
Only the first worksheet of the Excel file is considered and only XLSX files are allowed. The `properties` section can 
be inserted into the ontology file and then be uploaded onto a DSP server.

**An Excel file template can be found [here](assets/templates/properties_template.xlsx). It is recommended to work 
from the template.**

The Excel sheet must have the following structure:
![img-properties-example.png](assets/images/img-properties-example.png)

The expected columns are:

- `name` (mandatory): The name of the property
- `super` (mandatory): The base property/ies of the property, separated by commas
- `object` (mandatory): If the property is derived from `hasValue`, the type of the property must be further specified by the 
object it takes, e.g. `TextValue`, `ListValue`, or `IntValue`. If the property is derived from `hasLinkTo`, 
the `object` specifies the resource class that this property refers to.
- `en`, `de`, `fr`, `it`, `rm`: The labels of the property in different languages, at least one language has to be provided
- `comment_en`, `comment_de`, `comment_fr`, `comment_it`, `comment_rm` (optional): comments in the respective language 
- `gui_element` (mandatory): The GUI element for the property
- `gui_attributes` (optional): The gui_attributes in the form "attr: value, attr: value". 

The optional columns may be omitted in the Excel.  
For backwards compatibility, files containing a column `hlist` are valid, but deprecated.

For further information about properties, see [here](./dsp-tools-create-ontologies.md#properties).




## Create the "lists" section of a JSON project file from Excel files

With dsp-tools, the "lists" section of a JSON project file can be created from one or several Excel files. The lists can 
then be inserted into a JSON project file and uploaded to a DSP server. The command for this is documented 
[here](./dsp-tools-usage.md#create-the-lists-section-of-a-json-project-file-from-excel-files). 

The following example shows how to create the "lists" section from the two Excel files `Listen_de.xlsx` and 
`lists_en.xlsx` which are in a directory called `listfolder`:

```bash
dsp-tools excel2lists listfolder lists.json
```

The Excel sheets must have the following structure:
![img-list-english-example.png](assets/images/img-list-english-example.png)
![img-list-german-example.png](assets/images/img-list-german-example.png)

Some notes:

- The data must be in the first worksheet of each Excel file.
- It is important that all Excel files have the same structure. So, the translation of a label in the second Excel 
  file has to be in the exact same cell as the original in the first Excel sheet.
- Only Excel files with file extension `.xlsx` are considered. 
- The language of the labels has to be provided in the file name after an underline and before the file extension, e.g. 
  `Listen_de.xlsx` / `lists_en.xlsx`. 
- The language has to be one of {de, en, fr, it, rm}.
- As node name, a simplified version of the English label is taken. If English is not available, one of the other 
  languages is taken.
- If there are two nodes with the same name, an incrementing number is appended to `name`.
- After the creation of the list, a validation against the JSON schema for lists is performed. An error message is 
  printed out if the list is not valid.

**It is recommended to work from the following templates:  
[lists_en.xlsx](assets/templates/lists_en.xlsx): File with the English labels  
[Listen_de.xlsx](assets/templates/Listen_de.xlsx): File with the German labels**

The output of the above command, with the above files,   looks as follows:

```JSON
{
    "lists": [
        {
            "name": "colors",
            "labels": {
                "de": "Farben",
                "en": "colors"
            },
            "comments": {
                "de": "Farben",
                "en": "colors"
            },
            "nodes": [
                {
                    "name": "red",
                    "labels": {
                        "de": "rot",
                        "en": "red"
                    }
                },
                ...
            ]
        },
        {
            "name": "category",
            "labels": {
                "de": "Kategorie",
                "en": "category"
            },
            "comments": {
                "de": "Kategorie",
                "en": "category"
            },
            "nodes": [
                {
                    "name": "artwork",
                    "labels": {
                        "de": "Kunstwerk",
                        "en": "artwork"
                    }
                },
                ...
            ]
        },
        {
            "name": "faculties-of-the-university-of-basel",
            "labels": {
                "de": "Fakultäten der Universität Basel",
                "en": "Faculties of the University of Basel"
            },
            "comments": {
                "de": "Fakultäten der Universität Basel",
                "en": "Faculties of the University of Basel"
            },
            "nodes": [
                {
                    "name": "faculty-of-science",
                    "labels": {
                        "de": "Philosophisch-Naturwissenschaftliche Fakultät",
                        "en": "Faculty of Science"
                    }
                },
                ...
            ]
        }
    ]
}
```



## Create a DSP-conform XML file from an Excel/CSV file

There are two use cases for a transformation from Excel/CSV to XML: 

 - The CLI command `dsp-tools excel2xml` creates an XML file from an Excel/CSV file which is already structured 
   according to the DSP specifications. This is mostly used for DaSCH-interal data migration.
 - The module `excel2xml` can be imported into a custom Python script that transforms any tabular data into an XML. This
   use case is more frequent, because data from research projects have a variety of formats/structures. The module 
   `excel2xml` is documented [here](./dsp-tools-excel2xml.md).


### CLI command `excel2xml`

The command line tool is used as follows:
```bash
dsp-tools excel2xml data-source.xlsx 1234 shortname
```

There are no flags/options for this command.

The Excel file must be structured as in this image:
![img-excel2xml.png](assets/images/img-excel2xml.png)

Some notes:

 - The special tags `<annotation>`, `<link>`, and `<region>` are represented as resources of restype `Annotation`, 
`LinkObj`, and `Region`. 
 - The columns "ark" and "iri" are only used for DaSCH-internal data migration.
