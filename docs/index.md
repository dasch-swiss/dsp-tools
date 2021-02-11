[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# dsp-tools
dsp-tools is a python package containing

- a command line tool for data model (ontology) creation and manipulation based on JSON input file
- Python3 modules that implement CRUD (Create, Read, Update, Delete) operations for projects, users, groups and
  ontologies

The package consists of:

- `dsplib` Python modules for accessing Knora using the API (ontology creation, data import/export etc.)
- `dsp-tools` A command line program to perfrom several operations on a DSP server:
    - create an ontology out of a simple JSON description
    - dump an existing ontology from a DSP server to a JSON file
    - Bulk-upload of data from a XML data file

# Install

To install the latest version published on PyPI run:
```
$ pip3 install dsp-tools
```

To update to the latest version run:
```
$ pip3 install --upgrade dsp-tools
```

# Developer

## Makefile

There is a helping `Makefile` for all of the following tasks (and more).  
It is self-explanatory and a simple `make` will print its available targets.

## Install from source

To install from source, i.e. this repository run:
```
$ python3 setup.py install
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

## Testing

```bash
$ pip3 install pytest
$ pip3 install --editable .
$ pytest
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

## Contributing to the documentation

The documentation is a collection of [markdown](https://en.wikipedia.org/wiki/Markdown) in the `docs` sub-folder.  
After updates, it is possible to build and check the result with the commands:

```
$ make build-docs
$ make serve-docs 
```

