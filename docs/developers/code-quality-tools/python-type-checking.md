[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Python Type Checking

## Python's Typing System

The Python language allows adding type hints (see [PEP 484](http://www.python.org/dev/peps/pep-0484/)), 
but ignores them when running the code.
In this sense, type hints are similar to comments:
A Python program can still be run, even if the type hints are wrong.
The Python language leaves type checking to external tools that must be run separately.

## Existing Type Checkers

### [mypy](https://pypi.org/project/mypy/)

Mypy is the oldest and most popular static type checker.
It warns you when you use type annotations incorrectly.
Mypy is designed with gradual typing in mind. 
This means you can add type hints to your code base slowly 
and that you can always fall back to dynamic typing when static typing is not convenient.

### [pyright](https://github.com/microsoft/pyright)

Microsoft's static type checker for Python.
Via Pylance, it is included in VS Code's Python extension `ms-python.python`.

### [Pyre](https://pypi.org/project/pyre-check/)

Performant type checker by Facebook, compliant with the relevant PEP conventions.
Pyre can analyze codebases with millions of lines of code incrementally,
providing instantaneous feedback to developers as they write code.
Depends on [watchman](https://facebook.github.io/watchman/), 
a brew-installable FOSS file watching service by Facebook.
Pyre ships with Pysa, a security tool built on top of Pyre that reasons about data flows in Python applications. 
