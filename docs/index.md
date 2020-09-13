[![PyPI version](https://badge.fury.io/py/knora.svg)](https://badge.fury.io/py/knora)

# knora-py
knora-py is a python package containing a command line tool for data model (ontology) creation, a library allowing creation of single resources and mass upload using the bulk import of data into the Knora framework.

The package consists of:

- `Knora` Python3 library modules for accessing Knora using the API (ontology creation, data import/export etc.)
- `knora-create-onto` A command line program to create an ontology out of a simple JSON description
- `knora-xml-import` A command line programm to import data into Knora using gthe API
- `knora-reset-triplestore` A command line program to reset the content of the ontology. Does not require
   a restart of the Knora-Stack.
  

## Install

To install the latest version published on PyPI run:
```
$ pip3 install knora
```

To update to the latest version run:
```
$ pip3 install --upgrade knora
```

To install from source, i.e. this repository run:
```
$ python3 setup.py install
```

## Importing data into the triple store using the library
For importing data, you should consider using the `knora-xml-knora` command line tool
which reads and validates a simple XML file contining the data too be imported. However,
You can use the functioons and methods of knora-py directly in your python
script if yoou prefer so.

In order to import data, the data has to be read and reformatted. Reading the data
depends on the dta source and has to be developed by the user. However Knora offers some
simple methods to add the resource by resource to the Knora backend. Basically You need
- to create a _Knora()_ access instance
- get the Ontology schema with a method provided by the Knora instance
- call repeatedly the method _create_resource()_.

### Creating a Knora access instance
First You have to import some libraries:
```python
from typing import List, Set, Dict, Tuple, Optional
import json
from jsonschema import validate
from knora import KnoraError, KnoraStandoffXml, Knora, Sipi

```
Then You are ready to create the Knora access isntance. You need to know the server URL of Knora and the login credentials to do so:
```python
con = Knora(args.server) #  Create the Knora access instance
con.login(args.user, args.password) #  Perform a login

```

### Getting the ontology schema
The next step is to fetch the ontology (data model) from the Knora server. You need to know
the project code (usually a _string_ in the form XXXX, where X are characters 0-9, A-F) and
the name of the ontology.  
_Note_: This works only with projects that use a single ontology. Support for projects using
several user defined ontologies has not yet been implemented.
```python
schema = con.create_schema(args.projectcode, args.ontoname)
```

### Creating resources
Now You are ready to create the resources (see [create_resource()](#https://github.com/dhlab-basel/knora-py/tree/master/knora#create_resource) for details of using this method):
```python
inst1_info = con.create_resource(schema, "object1", "obj1_inst1", {
    "textprop": "Dies ist ein Text!",
    "intprop": 7,
    "listprop": "options:opt2",
    "dateprop": "1966:CE:1967-05-21",
    "decimalprop": {'value': "3.14159", 'comment': "Die Zahl PI"},
    "geonameprop": "2661604",
    "richtextprop": {
        'value': KnoraStandoffXml("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<text><p><strong>this is</strong> text</p> with standoff</text>"),
        'comment': "Text mit markup"
    },
    "intervalprop": "13.57:15.88"
})
```
THe call to _create_resource()_ returns a python Dict as follows:
```python
{
  'ark': 'http://0.0.0.0:3336/ark:/72163/1/00FE/HJD5LCVFS=qzUPK2=LgX1wZ',
  'iri': 'http://rdfh.ch/00FE/HJD5LCVFS-qzUPK2-LgX1w',
  'vark': 'http://0.0.0.0:3336/ark:/72163/1/00FE/HJD5LCVFS=qzUPK2=LgX1wZ.20190620T221223429441Z'
}
```
The `iri` can be used to reference this newly created resource in later calls.

### Creating resources with attached images

In order to create a StillImageRepresentation, that is a resource that is connected to an image,
YOu first have to upload the image usiing Sipi. For this YOu create first an instance of Sipi:
```python
sipi = Sipi(args.sipi, con.get_token())
```
The access token is taken from the Knora access instance using the method _get_tokeen()_. The Sipi
instance is then able to upload images:
```python
res = sipi.upload_image('example.tif')
```
The parameter to _upload_image()_ is the path to the image file. Currently J2K, TIF, PNG and JPG-imges are supported.

Now You are read to create the resource:
```python
fileref = res['uploadedFiles'][0]['internalFilename']
inst2_info = con.create_resource(
  schema,
  "object2",
  "obj2_inst1", {
    "titleprop": "Stained glass",
    "linkprop": inst1_info['iri']
  },
  fileref)
```
Please note that above example creates a resource that has a link to another resource. It
uses a link property defined in this example ontology as _linkprop_.

### Complete example

The complete example looks as follows:
```python
import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
from knora import KnoraError, KnoraStandoffXml, Knora, Sipi


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
parser.add_argument("-S", "--sipi", type=str, default="http://0.0.0.0:1024", help="URL of SIPI server")
parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
parser.add_argument("-p", "--password", default="test", help="The password for login")
parser.add_argument("-P", "--projectcode", default="00FE", help="Project short code")
parser.add_argument("-O", "--ontoname", default="kpt", help="Shortname of ontology")

args = parser.parse_args()


con = Knora(args.server)
con.login(args.user, args.password)

schema = con.create_schema(args.projectcode, args.ontoname)

inst1_info = con.create_resource(
  schema,
  "object1",
  "obj1_inst1", {
  "textprop": "Dies ist ein Text!",
  "intprop": 7,
  "listprop": "options:opt2",
  "dateprop": "1966:CE:1967-05-21",
  "decimalprop": {'value': "3.14159", 'comment': "Die Zahl PI"},
  "geonameprop": "2661604",
  "richtextprop": {
    'value': KnoraStandoffXml("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<text><p><strong>this is</strong> text</p> with standoff</text>"),
    'comment': "Text mit markup"
  },
  "intervalprop": "13.57:15.88"
})
pprint(inst1_info)

#first upload image to SIPI
sipi = Sipi(args.sipi, con.get_token())
res = sipi.upload_image('example.tif')
pprint(res)

fileref = res['uploadedFiles'][0]['internalFilename']
inst2_info = con.create_resource(
  schema,
  "object2",
  "obj2_inst1", {
    "titleprop": "Stained glass",
    "linkprop": inst1_info['iri']
  },
  fileref)
pprint(inst2_info)
```

## Resetting the triplestore with `knora-reset-triplestore`
This script reads a JSON file containing the data model (ontology) definition,
connects to the Knora server and creates the data model.

### Usage:

```bash
$ knora-reset-triplestore
```
It supports the following options:

- _"-s server" | "--server server"_: The URl of the Knora server [default: localhost:3333]
- _"-u username" | "--user username"_: Username to log into Knora [default: root@example.com]
- _"-p password" | "--password password"_: The password for login to the Knora server [default: test]

For resetting of the triplestore through Knora-API to work, it is necessary to start the Knora-API server
with a configuration parameter allowing this operation (e.g., `KNORA_WEBAPI_ALLOW_RELOAD_OVER_HTTP`
environment variable or the corresponding setting in `application.conf`).

## Bulk data import
In order to make a bulk data import, a properly formatted XML file has to be created. The python module "knora" contains
classes and methods to facilitate the creation of such a XML file.

## Requirements

To install the requirements:

```bash
$ pip3 install -r requirements.txt
```


To generate a "requirements" file (usually requirements.txt), that you commit with your project, do:

```bash
$ pip3 freeze > requirements.txt
```

## Publishing

Generate distribution package. Make sure you have the latest versions of `setuptools` and `wheel` installed:

```bash
$ python3 -m pip install --upgrade pip setuptools wheel
$ python3 setup.py sdist bdist_wheel
```

You can install the package locally from the dist:

```bash
$ python3 -m pip ./dist/some_name.whl
```

Upload package with `twine`,

first create `~/.pypirc`:

```bash
[distutils] 
index-servers=pypi
[pypi] 
repository = https://upload.pypi.org/legacy/ 
username =your_username_on_pypi
```

then upload:

```bash
$ python3 -m pip install --upgrade tqdm twine
$ python3 -m twine upload dist/*
```

For local development:

```bash
$ python3 setup.py develop
```

## Testing

```bash
$ pip3 install pytest
$ pip3 install --editable .
$ pytest
```

## Requirements

To install the requirements:

```bash
$ pip3 install -r requirements.txt
```


To generate a "requirements" file (usually requirements.txt), that you commit with your project, do:

```bash
$ pip3 freeze > requirements.txt
```

