[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# User Data in the User's Home Directory

DSP-TOOLS saves user data in the user's home directory, 
in the folder `.dsp-tools`. 
Here is an overview of its structure:

| file/folder                         | command using it | description                                                                                |
| :---------------------------------- | :--------------- | :----------------------------------------------------------------------------------------- |
| xmluploads/(server)/resumable/*.pkl | `xmlupload`      | Upload state of interrupted xmluploads                                                     |
| start-stack                         | `start-stack`    | files necessary to startup Docker containers (*)                                           |
| rosetta                             | `rosetta`        | a clone of [the rosetta test project](https://github.com/dasch-swiss/082e-rosetta-scripts) |
| logging.log, logging.log.1, ...     | several ones     | These two grow up to a predefined size, then the oldest log files are deleted              |


(*) Docker is normally not able to access files stored in the `site-packages` of a Python installation.
Therefore, it's necessary to copy the distributed `src/dsp_tools/resources/start-stack/` folder
to the user's home directory.



## How to Ship Data Files to the User

Accessing non-Python files (aka resources, aka data files) 
in the code needs special attention.

Firstly, the build tool must be told to include this folder/files in the distribution.
In our case, this is automatically done by hatchling.

Secondly, when accessing the files on the customer's machine, 
the files inside `site-packages` should be read-only 
to avoid a series of common problems 
(e.g. when multiple users share a common Python installation, 
when the package is loaded from a zip file, 
or when multiple instances of a Python application run in parallel).

Thirdly, the files can neither be accessed 
with a relative path from the referencing file,
nor with a path relative to the root of the project.

For example, if you have a structure like this:

```text
dsp-tools
├── pyproject.toml
└── src
    └── dsp_tools
        ├── schemas
        │   └── data.xsd
        ├── __init__.py
        └── dsp_tools.py
```

it is not possible to do one of the following in dsp_tools/dsp_tools.py:

```python
with open('schemas/data.xsd') as data_file:
     ...
with open('src/dsp_tools/resources/schema/data.xsd') as data_file:
     ...
```

The reason why these two approaches fail is 
that the working directory on the user's machine 
is determined by the directory where 
DSP-TOOLS is called from - 
not the directory where the distribution files are situated in.

To circumvent this problem,
it was once common to manipulate a package's `__file__` attribute 
in order to find the location of data files:

```python
import os
data_path = os.path.join(os.path.dirname(__file__), 'schemas', 'data.xsd')
with open(data_path) as data_file:
     ...
```

However, this manipulation isn't compatible with PEP 302-based import hooks, 
including importing from zip files and Python Eggs.

**The canonical way is to use [importlib.resources](https://docs.python.org/3/library/importlib.resources.html):** 

```python
from importlib.resources import files
# address "schemas" directory in module syntax: needs __init__.py
data_text = files('dsp_tools.resources.schema').joinpath('data.xsd').read_text()
# avoid module syntax when addressing "schemas" directory: no __init__.py necessary
data_text = files('dsp_tools').joinpath('resources/schema/data.xsd').read_text()
```

Note that depending on how the directory is addressed, 
an `__init__.py` file is necessary or can be omitted.

The information on this page is mainly based upon:

- <https://stackoverflow.com/a/20885799/14414188>
- <https://stackoverflow.com/a/58941536/14414188>
- <https://setuptools.pypa.io/en/latest/userguide/datafiles.html#accessing-data-files-at-runtime>
