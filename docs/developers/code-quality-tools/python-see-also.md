[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# See also

## [Prospector](https://pypi.org/project/prospector/)

Prospector is a wrapper around the following tools:

- pylint
- pycodestyle
- pyflakes
- McCabe
- Dodgy (simple regex check to detect accidental SCM diff checkins or secrets hard coded into files)
- Pydocstyle
- Pyroma (checks `setup.py` files)
- Vulture
- Frosted (fork of Pyflakes)
- Mypy
- Bandit

The primary aim of Prospector is to be useful out of the box. 
A common complaint of other Python analysis tools is
that it takes a long time to filter through which errors are relevant. 
Prospector provides some default profiles, 
which hopefully will provide a good starting point and will be useful straight away.

## Pylance

Pylance (`ms-python.vscode-pylance`) is the default language support 
for the Python extension (`ms-python.python`) in Visual Studio Code.
It relies on the type checker [pyright](https://github.com/microsoft/pyright), but does much more:

- docstring
- parameter suggestion
- code completion
- auto-imports
- code navigation

## Pylama

[Pylama](https://pypi.org/project/pylama/) is a wrapper around other tools. 
As of mid-2023, it doesn't seem to be actively maintained anymore.
Pylama wraps these tools:

- pycodestyle
- pydocstyle
- PyFlakes
- McCabe
- Pylint
- Radon 
- eradicate 
- Mypy
- Vulture
