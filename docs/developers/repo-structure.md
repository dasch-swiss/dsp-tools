# Structure of the DSP-TOOLS repository

## Overview

```text
dsp-tools
├── docs                    markdown files containing the documentation, published on docs.dasch.swiss
├── src
│   └── dsp_tools
│       ├── cli.py          CLI entry point
│       ├── utils           functions called by the CLI entry point
│       ├── models          python classes used by the "utils" functions
│       ├── fast_xmlupload  functions for the 3 commands `process-files`, `upload-files`, `fast-xmlupload`
│       ├── excel2xml.py    CLI command + library to create a XML file
│       ├── import_scripts  example repo for excel2json and import scripts (git submodule, https://github.com/dasch-swiss/00A1-import-scripts)
│       └── resources       non-python files included in the distribution
├── test
│   ├── e2e                 tests that need a DSP stack running
│   └── unittests           tests that don't need a DSP stack running
├── testdata                files necessary for the tests to run
└── pyproject.toml          project metadata, definition of pip-dependencies, config for many tools
```

## Interdependence of the modules

![](../assets/pyreverse/packages.dot.png)

## Interdependence of the classes

![](../assets/pyreverse/classes.dot.png)
