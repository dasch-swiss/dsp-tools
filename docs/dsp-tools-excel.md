[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Excel files for data modelling and data import
dsp-tools is able to process Excel files and output the appropriate JSON or XML file. The JSON/XML file can then
be used to create the ontology on the DSP server or import data to the DSP repository. dsp-tools can also be used to
create a list from an Excel file.

## Create the data model JSON from an Excel file
[not yet implemented]

## Create a DSP-conform XML file from an Excel file
[not yet implemented]

## Create a list from one or several Excel files
With dsp-tools a list can be created from one or several Excel files. The expected format of the Excel files is described 
[here](./dsp-tools-create.md#lists-from-excel). It is possible to create multilingual lists. Therefore, an Excel file for each 
language has to be created. The data has to be in the first worksheet of the Excel file and all Excel files have to be in the 
same directory. When calling the `excel` command, this folder has to be provided as an argument to the call. 

The following example shows how to create a JSON list from two Excel files which are in a directory called `lists`. The output is
written to the file `list.json`.
```bash
dsp-tools excel lists list.json
```

The two Excel files `liste_de.xlsx` and `list_en.xlsx` are in the folder called `lists`:
```
lists
    |__ liste_de.xlsx
    |__ list_en.xlsx
```

For each list node, the `label`s are read from the Excel files. The language attribute is taken from the filename(s) after the 
last underline `_`. So, in case of `liste_de.xlsx` the language attribute `de` is taken for all the node labels in the Excel 
file. The language attribute has to be a valid ISO 639-1 or ISO 639-2 code. The language code is then used for the labels like 
this:
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
}, ...
```

As node `name`, a simplified version of the English label is taken, if English is one of the available languages. If English 
is not available, one of the other languages is chosen (which one depends on the representation of the file order). If there are 
two node names with the same name, an incrementing number is appended to the name.

After the creation of the list, a validation against the XSD schema for lists is performed. An error message ist printed out 
if the list is not valid. Furthermore, it is checked that no two nodes are the same.

