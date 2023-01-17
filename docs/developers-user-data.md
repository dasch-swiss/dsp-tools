[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# User data in the folder `.dsp-tools`

DSP-TOOLS saves user data in the user's home directory, in the folder `.dsp-tools`. Here is an overview of its 
structure:

| folder     | command using it | description                                  |
|:-----------|:-----------------|:---------------------------------------------|
| xmluploads | `xmlupload`      | saves id2iri mappings and error reports      |
| docker     | `start-stack`    | files necessary to startup Docker containers |

Typically, existing programs manipulate a package’s __file__ attribute in order to find the location of data files. For example, if you have a structure like this:

project_root_directory
├── setup.py        # and/or setup.cfg, pyproject.toml
└── src
    └── mypkg
        ├── data
        │   └── data1.txt
        ├── __init__.py
        └── foo.py

Then, in mypkg/foo.py, you may try something like this in order to access mypkg/data/data1.txt:

import os
data_path = os.path.join(os.path.dirname(__file__), 'data', 'data1.txt')
with open(data_path, 'r') as data_file:
     ...

However, this manipulation isn’t compatible with PEP 302-based import hooks, including importing from zip files and Python Eggs. It is strongly recommended that, if you are using data files, you should use importlib.resources to access them. In this case, you would do something like this:

from importlib.resources import files
data_text = files('mypkg.data').joinpath('data1.txt').read_text()


Files inside the package directory should be read-only to avoid a series of common problems (e.g. when multiple users share a common Python installation, when the package is loaded from a zip file, or when multiple instances of a Python application run in parallel).

If your Python package needs to write to a file for shared data or configuration, you can use standard platform/OS-specific system directories, such as ~/.local/config/$appname or /usr/share/$appname/$version (Linux specific) [2]. A common approach is to add a read-only template file to the package directory that is then copied to the correct system directory if no pre-existing file is found.

[tool.poetry]
include = [
    "src/dsp_tools/schemas/*",
    "src/dsp_tools/docker/*"
]

Thanks to PEP 420, since Python 3.3 you don't need an __init__.py for a directory to be considered a package. 
Therefore, it's not necessary to have an __init__.py inside a resources folder.

But https://stackoverflow.com/a/58941536/14414188 claims that __init__.py is necessary?