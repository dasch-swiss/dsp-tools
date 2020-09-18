[![PyPI version](https://badge.fury.io/py/knora.svg)](https://badge.fury.io/py/knora)

# knora-py
knora-py is a python package containing

- a command line tool for data model (ontology) creation and manipulation based on JSON input file
- a gui-based local tool to directly manipulate project data, users, groups and data models on a live server
- Python3 modules that implement CRUD (Create, Read, Update, Delete) operations for projects, users, groups and
  ontologies

The package consists of:

- `knora-create-onto` A command line program to create an data model from a simple JSON description or to read a
  data model from a live knora server and dump it into a JSOn file.
- `knora-console` A small GUI app for creating projects ontologies, users and group directly on a live knora server
- a set of python3 modules

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

