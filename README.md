[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS - The DaSCH Service Platform Tools Repository
dsp-tools is a python package containing a command line tool for data model (ontology) creation, a library allowing
creation of single resources and mass upload using the bulk import of data into the Knora framework.

The package consists of:
- `dsplib` Python modules for accessing Knora using the API (ontology creation, data import/export etc.)
- `dsp-tools` A command line program to perfrom several operations on a DSP server:
    - create an ontology out of a simple JSON description
    - dump an existing ontology from a DSP server to a JSON file
    - Bulk-upload of data from a XML data file

Go to [Full Documentation](https://dasch-swiss.github.io/dsp-tools/)

## Install

_Please note that dsp-tools require Python 3.9 for working properly!_

To install the latest published version from PyPI, run:
```
$ pip3 install dsp-tools
```

To upgrade to the latest published version, run:
```
$ pip3 install --upgrade dsp-tools
```

## Local Development Environment

- Python3
- [Bazel](https://bazel.build)

Please consult the [https://docs.dasch.swiss/developers](https://docs.dasch.swiss/developers)
documentation on how to install these prerequisites.

## Makefile for repository management tasks

The project contains a Makefile defining management tasks. Please use
`make help` to see what is available.

To install from source, i.e., this repository, run:
```
$ make install
```

## Testing

```bash
$ make test
```

## Publishing to PyPi

Generate distribution package. Make sure you have the latest versions of `setuptools` and `wheel` installed:

```bash
$ make upgrade-dist-tools
$ make dist
```

You can install the package locally from the dist:

```bash
$ python3 -m pip install ./dist/some_name.whl
```

Upload package with `twine`,

first create `~/.pypirc` in your home folder:

```bash
[distutils] 
index-servers=pypi
[pypi] 
repository = https://upload.pypi.org/legacy/ 
username =your_username_on_pypi
```

then upload:

```bash
$ make upload
```

For local development:

```bash
$ python3 setup.py --editable .
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

### Running tests with Bazel

Run all tests:
```bash
$ bazel test //...
```

Run single test:
```bash
$ bazel test //test:test_user
```

