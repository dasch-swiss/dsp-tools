[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Excel files for data modelling and data import

dsp-tools is able to process Excel files and output the appropriate JSON or XML file. The JSON/XML file can then be
used to create the ontology on the DSP server or import data to the DSP repository. dsp-tools can also be used to 
create a list from an Excel file.

## Create the resources for a data model from an Excel file

With dsp-tools, the `resources` section used in a data model (JSON) can be created from an Excel file. Only `XLSX` 
files are allowed. The `resources` section can be inserted into the ontology file and then be uploaded onto a DSP 
server.

**An Excel file template can be found [here](assets/templates/resources_template.xlsx). It is recommended to work from 
the template.**

The expected worksheets of the Excel file are:

- `classes`: a table with all resource classes intended to be used in the resulting JSON
- `class1`, `class2`,...: a table for each resource class named after its name

The Excel sheet must have the following format.

The worksheet called `classes` has the following format: 
![img-resources-example-1.png](assets/images/img-resources-example-1.png)

The expected columns are:

- `name` : The name of the resource
- `en`, `de`, `fr`, `it` : The labels of the resource in different languages, at least one language has to be provided
- `comment_en`, `comment_de`, `comment_fr`, `comment_it`: optional comments in the respective language 
- `super` : The base class of the resource

All other worksheets, one for each resource class, have the following format:
![img-resources-example-2.png](assets/images/img-resources-example-2.png){ width=50% }

The expected columns are:

- `Property` : The name of the property
- `Cardinality` : The cardinality, one of: `1`, `0-1`, `1-n`, `0-n`

The GUI order is given by the order in which the properties are listed in the Excel sheet.

For further information about resources, see [here](./dsp-tools-create-ontologies.md#resources).

## Create the properties for a data model from an Excel file

With dsp-tools, the `properties` section used in a data model (JSON) can be created from an Excel file. Only the first 
worksheet of the Excel file is considered and only XLSX files are allowed. The `properties` section can be inserted 
into the ontology file and then be uploaded onto a DSP server.

**An Excel file template can be found [here](assets/templates/properties_template.xlsx). It is recommended to work 
from the template.**

The Excel sheet must have the following format:
![img-properties-example.png](assets/images/img-properties-example.png)

The expected columns are:

- `name` : The name of the property
- `super` : The base property of the property
- `object` : If the property is derived from `hasValue`, the type of the property must be further specified by the 
object it takes, e.g. `TextValue`, `ListValue`, or `IntValue`. If the property is derived from `hasLinkTo`, 
the `object` specifies the resource class that this property refers to.
- `en`, `de`, `fr`, `it` : The labels of the property in different languages, at least one language has to be provided
- `comment_en`, `comment_de`, `comment_fr`, `comment_it`: optional comments in the respective language 
- `gui_element` : The GUI element for the property
- `hlist` : In case of list values: the name of the list

For further information about properties, see [here](./dsp-tools-create-ontologies.md#properties).

## Create a DSP-conform XML file from an Excel file

[not yet implemented]

## Create a list from one or several Excel files

With dsp-tools a JSON list can be created from one or several Excel files. The list can then be inserted into a JSON 
ontology and uploaded to a DSP server. The expected format of the Excel files is described 
[here](./dsp-tools-create.md#lists-from-excel). It is possible to create multilingual lists. In this case, a separate 
Excel file has to be created for each language. The data has to be in the first worksheet of the Excel file(s). 
It is important that all the Excel lists have the same structure. So, the translation(s) of a label in one Excel 
sheet has to be in the exact same cell (i.e. with the same cell index) in its own Excel sheet.

Only Excel files with file extension `.xlsx` are considered. All Excel files have to be located in the same directory. 
When calling the `excel` command, this folder is provided as an argument to the call. The language of the labels has 
to be provided in the Excel file's file name after an underline and before the file extension, p.ex. `liste_de.xlsx` 
would be considered a list with German (`de`) labels, `list_en.xlsx` a list with English (`en`) labels. The language 
has to be a valid ISO 639-1 or ISO 639-2 language code.

The following example shows how to create a JSON list from two Excel files which are in a directory called `lists`. 
The output is written to the file `list.json`.

```bash
dsp-tools excel lists list.json
```

The two Excel files `liste_de.xlsx` and `list_en.xlsx` are located in a folder called `lists`. `liste_de.xlsx` 
contains German labels for the list, `list_en.xlsx` contains the English labels.

```
lists
    |__ liste_de.xlsx
    |__ list_en.xlsx
```

For each list node, the `label`s are read from the Excel files. The language code, provided in the file name, is then 
used for the labels. As node `name`, a simplified version of the English label is taken if English is one of the 
available languages. If English is not available, one of the other languages is chosen (which one depends on the 
representation of the file order). If there are two node names with the same name, an incrementing number is appended to
the `name`.

```JSON
{
  "name": "sand",
  "labels": {
    "de": "Sand",
    "en": "sand"
  },
  "nodes": [
    {
      "name": "fine-sand",
      "labels": {
        "de": "Feinsand",
        "en": "fine sand"
      }
    },
    {
      "name": "medium-sand",
      "labels": {
        "de": "Mittelsand",
        "en": "medium sand"
      }
    },
    {
      "name": "coarse-sand",
      "labels": {
        "de": "Grobsand",
        "en": "coarse sand"
      }
    }
  ]
}
```

After the creation of the list, a validation against the JSON schema for lists is performed. An error message is 
printed out if the list is not valid. Furthermore, it is checked that no two nodes are the same.
