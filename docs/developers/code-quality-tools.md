[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Code quality tools

There is a variety of tools that help to keep the code quality high.

DSP-TOOLS uses the following:

- EditorConfig
- Security: 
    - vulture (coming soon)
    - bandit (coming soon)
    - Dependabot
    - CodeQL
- Formatting: Black
- Type checking: MyPy
- Linting: 
    - Ruff (coming soon)
    - Pylint (will perhaps become redundant, as Ruff grows)


## Language-independent, cross-editor settings

- [EditorConfig](https://EditorConfig.org)

## Security checks

[Bandit](https://pypi.org/project/bandit/) finds common security issues in Python code
Dependabot
CodeQL
[Gitleaks](https://gitleaks.io/products.html)

## Python: autoformatters

- [pycodestyle](https://pypi.org/project/pycodestyle/): 
  Checks Python code against some of the style conventions in [PEP 8](http://www.python.org/dev/peps/pep-0008/).
- [autopep8](https://pypi.org/project/autopep8/): 
  Automatically fixes most of the formatting issues reported by pycodestyle.
  Since PEP 8 is rather liberal, autopep8/pycodestyle don't modify code too much.
- [black](https://pypi.org/project/black/): 
  A PEP 8 compliant opinionated formatter with its own style, going further than autopep8/pycodestyle.
  Style configuration options are deliberately limited to a minimum.
  Black aims for readability and reducing git diffs.
- [isort](https://pypi.org/project/isort/): 
  Sorts imports alphabetically, and separates them into sections, according to their type.
- [yapf](https://pypi.org/project/yapf/): 
  Autoformatter that can be configured to support different styles. 

## Python: type checkers

- mypy
- [pyright](https://github.com/microsoft/pyright): 
  Microsoft's static type checker for Python.
  Via Pylance, it is included in VS Code's Python extension `ms-python.python`.
- pyre

## Python: linters

- pylint
- Flake8
- Ruff
a linter with autofix support
Near-parity with Flake8
Ruff's own recommendation: Use Ruff together with Black and a type checker 
VS Code plugin
Ruff works on implementing pylint rules, but isn't there yet (as of May 2023)
Ruff can be used to replace 
- Flake8 (plus dozens of plugins)
- Pyflakes
- pycodestyle
- mccabe
- isort,
- pydocstyle, 
- yesqa, 
- eradicate, 
- pyupgrade (automated upgrade to newer python syntax)
- autoflake (automated removal of unused imports or variables)


## See also

### Pylance

Pylance (`ms-python.vscode-pylance`) is the default language support 
for the Python extension (`ms-python.python`) in Visual Studio Code.
It relies on the type checker [pyright](https://github.com/microsoft/pyright), but does much more:

- docstring
- parameter suggestion
- code completion
- auto-imports
- code navigation

### Pylama

[Pylama](https://pypi.org/project/pylama/) is a wrapper around other tools. 
As of mid-2023, it seems to be poorly maintained, and slowly dying.
Pylama wraps these tools:

- pycodestyle
- pydocstyle
- PyFlakes
- Mccabe
- Pylint
- Radon 
- eradicate 
- Mypy
- Vulture





Pylint
Very broad list of rules, some rather formatting oriented, some very sophisticated code smell detectors
very slow, but very thorough
inference of actual types, instead of relying on type annotations
Advised linters alongside pylint:

- linters: ruff/flake8
- type checkers: mypy/pyright/pyre
- security: bandit
- autoformatters: black
- pydocstringformatter (automated pep257)





Pyflakes


Flake8
flake8 am meisten empfohlen, weil es ist zugleich ein static analysis tool (findet bugs) und style checker (findet inkonsistenzen in der formattierung)
als CLI zeigt es eine Liste mit Beanstandungen
Flake8 is a wrapper around these tools:
    PyFlakes
    pycodestyle
    McCabe
Flake8 runs all the tools by launching the single flake8 command. It displays the warnings in a per-file, merged output.


pydocstyle



Docstrings

Wir benutzen Google Style Docstrings ohne typing.
Sollte eingestellt werden in PyCharm > Settings > Tools > Python Integrated Tools > Docstring format
resp. in VS Code > Auto Docstring: Docstring Format > google-notypes

<https://sphinxcontrib-napoleon.readthedocs.io/en/latest/index.html>:
RST (ReStructuredText) is great, but it creates visually dense, hard to read docstrings. 
Napoleon is a Sphinx extension that enables Sphinx to parse both NumPy and Google style docstrings
