[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# See Also

## [Prospector](https://pypi.org/project/prospector/)

Prospector is a wrapper around the following tools:

- pylint (very through linter and error detector)
- pycodestyle (checks formatting for violations of PEP 8)
- Pyflakes (error detector)
- McCabe (complexity checker)
- Dodgy (simple regex check to detect accidental SCM diff checkins or secrets hard coded into files)
- Pydocstyle (docstring checker)
- Pyroma (checks `setup.py` files)
- Vulture (finds unused code)
- Frosted (fork of Pyflakes)
- Mypy (type checker)
- Bandit (finds common security issues)

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

## [Pylama](https://pypi.org/project/pylama/)

Pylama is a wrapper around other tools. 
As of mid-2023, it doesn't seem to be actively maintained anymore.
Pylama wraps these tools:

- pycodestyle (checks formatting for violations of PEP 8)
- pydocstyle (docstring checker)
- PyFlakes (error detector)
- McCabe (complexity checker)
- Pylint (very through linter and error detector)
- Radon (computes various metrics from source code, such as McCabe's complexity, SLOC, Halstead metrics, etc.)
- eradicate (removes commented-out code)
- Mypy (type checker)
- Vulture (finds unused code)
