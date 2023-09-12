[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Python Docstring Formatting

## Docstring Flavors

Python uses docstrings to document code. 
A docstring is a string that is the first statement in a package, module, class or function. 
Python docstrings are written in the
[reStructuredText](https://docutils.sourceforge.io/rst.html) syntax (abbreviated as RST or reST).

There are at least 4 flavors of docstrings,
each following the [PEP 257](http://www.python.org/dev/peps/pep-0257/) conventions.
The following examples show how to document a function parameter:

Epytext:

```pydocstring
@type param1: int
@param param1: The first parameter
```

Sphinx:

```pydocstring
:param param1: The first parameter
:type: int
```

Google:

```pydocstring
Args:
    param1 (int): The first parameter
```

NumPy:

```pydocstring
Parameters
----------
param1 : int
    The first parameter
```

DSP-TOOLS uses the Google style without typing, 
as defined [here](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).


## Existing Formatters

### [pydocstyle](https://pypi.org/project/pydocstyle/)

Static analysis tool for checking compliance with Python docstring conventions.
Pydocstyle supports most [PEP 257](http://www.python.org/dev/peps/pep-0257/) conventions out of the box, 
but it should not be considered a reference implementation.
Pydocstyle seems to be the most popular docstring checker.
It supports the styles "pep257", "numpy", and "google".

### [pydocstringformatter](https://pypi.org/project/pydocstringformatter/)

A docstring formatter that follows 
[PEP 8](http://www.python.org/dev/peps/pep-0008/) and [PEP 257](http://www.python.org/dev/peps/pep-0257/) 
but makes some of the more controversial elements of those PEPs optional.
Can be configured for other styles as well. 
This project is heavily inspired by docformatter.
Supported styles: "pep257", "numpy".

### [docformatter](https://pypi.org/project/docformatter/)

Automatically formats docstrings to follow a subset of 
the [PEP 257](http://www.python.org/dev/peps/pep-0257/) conventions.
Currently, only the style "sphinx" and "epytext" are recognized, 
but "numpy" and "google" are future styles.

### [darglint](https://pypi.org/project/darglint/)

Docstring linter which checks whether a docstring's description matches the actual function/method implementation.
Supports the styles "sphinx", "google", and "numpy".
