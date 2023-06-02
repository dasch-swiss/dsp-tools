[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Code quality tools

There is a variety of tools that help to keep the code quality high.

DSP-TOOLS uses the following:

- EditorConfig
- Formatting: Black
- Type checking: MyPy
- Linting: 
    - Ruff (coming soon)
    - Pylint (will perhaps become redundant, as Ruff grows)
- Security: 
    - vulture (coming soon)
    - bandit (coming soon)
    - Dependabot
    - CodeQL
    - Gitleaks (coming soon)

In the following, this choice is explained in more detail.

## Language-independent, cross-editor settings

- [EditorConfig](https://EditorConfig.org)


## Python: Style checkers and autoformatters

- [pycodestyle](https://pypi.org/project/pycodestyle/): 
  Checks Python code against some of the style conventions in [PEP 8](http://www.python.org/dev/peps/pep-0008/).
- [autopep8](https://pypi.org/project/autopep8/): 
  Automatically fixes most of the formatting issues reported by pycodestyle.
  Since PEP 8 is rather liberal, autopep8/pycodestyle don't modify code too much.
- [black](https://pypi.org/project/black/): 
  A PEP 8 compliant opinionated autoformatter with its own style, going further than autopep8/pycodestyle.
  Style configuration options are deliberately limited to a minimum.
  Black aims for readability and reducing git diffs.
- [yapf](https://pypi.org/project/yapf/): 
  Autoformatter that can be configured to support different styles.

### Tools specialized on parts of the code

- [isort](https://pypi.org/project/isort/): 
  Sorts imports alphabetically, and separates them into sections, according to their type.

# TODO
- [pydocstyle](https://pypi.org/project/pydocstyle/):
  static analysis tool for checking compliance with Python docstring conventions.
  pydocstyle supports most of PEP 257 out of the box, but it should not be considered a reference implementation.
- [pydocstringformatter](https://pypi.org/project/pydocstringformatter/):
  A docstring formatter that follows PEP8 and PEP257 but makes some of the more 'controversial' elements of the PEPs optional.
  Can be configured for other styles as well.
  This project is heavily inspired by docformatter.
  When this project was started docformatter did not meet all of the requirements the pylint project had for its docstring formatter 
  and was no longer actively maintained (this has changed since then). 
  Therefore, some contributors of pylint got together and started working on our own formatter to fulfill our needs.
- [docformatter](https://pypi.org/project/docformatter/): 


## Python: type checkers

# TODO
- mypy
- [pyright](https://github.com/microsoft/pyright): 
  Microsoft's static type checker for Python.
  Via Pylance, it is included in VS Code's Python extension `ms-python.python`.
- pyre


## Python: linters

- [Pylint](https://pypi.org/project/pylint/): 
  Checks Python code against a very broad list of rules, 
  some of which are purley formatting oriented, 
  but some of which are very sophisticated code smell and error detectors.
  Pylint is very slow, but perhaps the most thorough linter around. 
  A big plus is that it makes an inference of actual types, 
  instead of relying on type annotations.
- [Pyflakes](https://pypi.org/project/pyflakes/):
  A pure error detector, without formatting checks, and without configuration options.
  It is faster than Pylint, because it doesn't dig as deep as Pylint 
  (it examines the syntax tree of each file individually).
  If you like Pyflakes but also want stylistic checks, you want flake8, which combines Pyflakes with style checks against PEP 8 and adds per-project configuration ability.
- [Flake8](https://pypi.org/project/flake8/):
  Flake8 checks Python code by wrapping the output of these tools:
    - Pyflakes (pure error detector)
    - pycodestyle (pure style checker)
    - McCabe
  Unlike Pyflakes, Flake8 can be configured.
- [Ruff](https://pypi.org/project/ruff/):
  The fastest, most promising and most exciting linter, although still in beta.
  Ruff is a linter with autofix support
  Near-parity with Flake8, and working on implementing pylint rules 
  (see [How does Ruff compare to Pylint?](https://beta.ruff.rs/docs/faq/#how-does-ruff-compare-to-pylint)).
  Ruff can be used to replace 
    - Flake8 (plus dozens of plugins)
    - Pyflakes
    - pycodestyle
    - mccabe
    - isort
    - pydocstyle
    - yesqa     # TODO
    - eradicate
    - pyupgrade (automated upgrade to newer python syntax)
    - autoflake (automated removal of unused imports or variables)


## Security checks

# TODO

Vulture
[Bandit](https://pypi.org/project/bandit/) finds common security issues in Python code
Dependabot
CodeQL
[Gitleaks](https://gitleaks.io/products.html)


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







Docstrings

Wir benutzen Google Style Docstrings ohne typing.
Sollte eingestellt werden in PyCharm > Settings > Tools > Python Integrated Tools > Docstring format
resp. in VS Code > Auto Docstring: Docstring Format > google-notypes

<https://sphinxcontrib-napoleon.readthedocs.io/en/latest/index.html>:
RST (ReStructuredText) is great, but it creates visually dense, hard to read docstrings. 
Napoleon is a Sphinx extension that enables Sphinx to parse both NumPy and Google style docstrings
