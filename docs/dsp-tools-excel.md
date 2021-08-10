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
With dsp-tools a JSON list can be created from one or several Excel files. The list can then be inserted into a JSON ontology 
and uploaded to a DSP server. The expected format of the Excel files is described [here](./dsp-tools-create.md#lists-from-excel). 
It is possible to create multilingual lists. In this case, a separate Excel file has to be created for each language. The data 
has to be in the first worksheet of the Excel file(s). It is important that all the Excel lists have the same structure. So, 
the translation(s) of a label in one Excel sheet has to be in the exact same cell (i.e. with the same cell index) in its own 
Excel sheet.

Only Excel files with file extension `.xlsx` are considered. All Excel files have to be located in the same directory. When 
calling the `excel` command, this folder is provided as an argument to the call. The language of the labels has to be provided in 
the Excel file's file name after an underline and before the file extension, p.ex. `liste_de.xlsx` would be considered a list with 
German (`de`) labels, `list_en.xlsx` a list with English (`en`) labels. The language has to be a valid ISO 639-1 or ISO
639-2 language code.

The following example shows how to create a JSON list from two Excel files which are in a directory called `lists`. The output is
written to the file `list.json`.

```bash
dsp-tools excel lists list.json
```

The two Excel files `liste_de.xlsx` and `list_en.xlsx` are located in a folder called `lists`. `liste_de.xlsx` contains German 
labels for the list, `list_en.xlsx` contains the English labels.

```
lists
    |__ liste_de.xlsx
    |__ list_en.xlsx
```

For each list node, the `label`s are read from the Excel files. The language code, provided in the file name, is then used for 
the labels. As node `name`, a simplified version of the English label is taken if English is one of the available languages. If
English is not available, one of the other languages is chosen (which one depends on the representation of the file order). If
there are two node names with the same name, an incrementing number is appended to the `name`.

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

After the creation of the list, a validation against the JSON schema for lists is performed. An error message ist printed out if 
the list is not valid. Furthermore, it is checked that no two nodes are the same.
