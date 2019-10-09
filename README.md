[![PyPI version](https://badge.fury.io/py/knora.svg)](https://badge.fury.io/py/knora)

# knora-py
knora-py is a python package containing a command line tool for data model (ontology) creation, a library allowing creation of single resources and mass upload using the bulk import of data into the Knora framework.

The package consists of:
- `Knora` Python modules for accessing Knora using the API (ontology creation, data import/export etc.)
- `knora-create-ontology` A command line program to create an ontology out of a simple JSON description
- `knora-reset-triplestore` A command line program to reset the content of the ontology. Does not require
   a restart of the Knora-Stack.  

Go to [Full Documentation](https://dasch-swiss.github.io/knora-py/)

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

## Makefile for repository management tasks

The project contains a Makefile defining management tasks. Please use
`make help` to see what is available. 

## Publishing to PyPi

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
