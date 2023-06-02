[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Code quality tools

There is a variety of tools that help to keep the code quality high.

DSP-TOOLS uses the following:

| Task                  | Tool                                                              | Configuration            | Remarks                                        |
| --------------------- | ----------------------------------------------------------------- | ------------------------ | ---------------------------------------------- |
| General formatting    | [EditorConfig](https://EditorConfig.org)                          | `.editorconfig`          |                                                |
| Python: formatting    | [Black](https://pypi.org/project/black/)                          | `pyproject.toml`         |                                                |
| Python: type checking | [Mypy](https://pypi.org/project/mypy/)                            | `pyproject.toml`         |                                                |
| Python: linting       | [Ruff](https://pypi.org/project/ruff)                             |                          | coming soon                                    |
|                       | [Pylint](https://pypyi.org/project/pylint)                        | `pyproject.toml`         | will perhaps become redundant,<br>as Ruff matures |
| Security checks       | [Dependabot](https://docs.github.com/en/code-security/dependabot) | `.github/dependabot.yml` |                                                |
|                       | [CodeQL](https://codeql.github.com/)                              | GitHub settings          |                                                |
|                       | [Gitleaks](https://gitleaks.io/)                                  | `.gitleaks.toml`         | coming soon                                    |
|                       | [Bandit](https://pypi.org/project/bandit/)                        | `pyproject.toml`         | coming soon                                    |

The decision to use this set of tools is based on the information in the following paragraphs.

## General formatting

### [EditorConfig](https://EditorConfig.org)

Language-independent, cross-editor settings for indentation, line endings, etc.


## Python: formatters

There is a variety of style checkers (tools that give a feedback) 
and autoformatters (tools that are able to fix the formatting violations automatically):

### [pycodestyle](https://pypi.org/project/pycodestyle/)

Checks Python code against some of the style conventions in [PEP 8](http://www.python.org/dev/peps/pep-0008/).

### [autopep8](https://pypi.org/project/autopep8/)

Automatically fixes most of the formatting issues reported by pycodestyle.
Since PEP 8 is rather liberal, autopep8/pycodestyle don't modify code too much.

### [black](https://pypi.org/project/black/)

A PEP 8 compliant opinionated autoformatter with its own style, going further than autopep8/pycodestyle.
Style configuration options are deliberately limited to a minimum.
Black aims for readability and reducing git diffs.

### [yapf](https://pypi.org/project/yapf/)

Autoformatter that can be configured to support different styles.

### [isort](https://pypi.org/project/isort/)

Sorts imports alphabetically, and separates them into sections, according to their type.

TODO !!!

### [pydocstyle](https://pypi.org/project/pydocstyle/)

Static analysis tool for checking compliance with Python docstring conventions.
Pydocstyle supports most of [PEP 257](http://www.python.org/dev/peps/pep-0257/) out of the box, 
but it should not be considered a reference implementation.
Pydocstyle seems to be the most popular docstring checker.

### [pydocstringformatter](https://pypi.org/project/pydocstringformatter/)

A docstring formatter that follows 
[PEP 8](http://www.python.org/dev/peps/pep-0008/) and [PEP 257](http://www.python.org/dev/peps/pep-0257/) 
but makes some of the more controversial elements of the PEPs optional.
Can be configured for other styles as well. 
This project is heavily inspired by docformatter.


### [docformatter](https://pypi.org/project/docformatter/)

docformatter automatically formats docstrings to follow a subset of the PEP 257 conventions.
The --style argument takes a string which is the name of the parameter list style you are using. 
Currently, only sphinx and epytext are recognized, but numpy and google are future styles. 


## Python: type checkers

TODO !!!!!!!!

### [mypy](https://pypi.org/project/mypy/)

Mypy is a static type checker for Python.

Type checkers help ensure that you’re using variables and functions in your code correctly. 
With mypy, add type hints (PEP 484) to your Python programs, 
and mypy will warn you when you use those types incorrectly.
Adding type hints for mypy does not interfere with the way your program would otherwise run. 
Think of type hints as similar to comments! 
You can always use the Python interpreter to run your code, even if mypy reports errors.
Mypy is designed with gradual typing in mind. 
This means you can add type hints to your code base slowly 
and that you can always fall back to dynamic typing when static typing is not convenient.

### [pyright](https://github.com/microsoft/pyright)

Microsoft's static type checker for Python.
Via Pylance, it is included in VS Code's Python extension `ms-python.python`.

### pyre

TODO


## Python: linters

### [Pylint](https://pypi.org/project/pylint/)

Checks Python code against a very broad list of rules, 
some of which are purley formatting oriented, 
but some of which are very sophisticated code smell and error detectors.
Pylint is very slow, but perhaps the most thorough linter around. 
A big plus is that it makes an inference of actual types, 
instead of relying on type annotations.

### [Pyflakes](https://pypi.org/project/pyflakes/)

A pure error detector, without formatting checks, and without configuration options.
It is faster than Pylint, because it doesn't dig as deep as Pylint 
(it examines the syntax tree of each file individually).
If you like Pyflakes but also want stylistic checks, you want flake8, which combines Pyflakes with style checks against PEP 8 and adds per-project configuration ability.

### [Flake8](https://pypi.org/project/flake8/)

Flake8 checks Python code by wrapping the output of these tools:

- Pyflakes (pure error detector)
- pycodestyle (pure style checker)
- [McCabe](https://pypi.org/project/mccabe/) (complexity checker)

Unlike Pyflakes, Flake8 can be configured.

### [Ruff](https://pypi.org/project/ruff/)

The fastest, most promising and most exciting linter, although still in beta.
Ruff is a linter with autofix support
Near-parity with Flake8, and working on implementing pylint rules 
(see [How does Ruff compare to Pylint?](https://beta.ruff.rs/docs/faq/#how-does-ruff-compare-to-pylint)).
Ruff can be used to replace 

- Flake8 (plus dozens of plugins)
- Pyflakes
- pycodestyle
- McCabe
- isort
- pydocstyle
- yesqa     # TODO
- eradicate
- pyupgrade (automated upgrade to newer python syntax)
- autoflake (automated removal of unused imports or variables)

### [Vulture](https://pypi.org/project/vulture/)

Static code analyzer that finds unused code in Python programs. 
Vulture uses the ast module to build abstract syntax trees for all given files. 
While traversing all syntax trees it records the names of defined and used objects. 
Afterwards, it reports the objects which have been defined, but not used. 
This analysis ignores scopes and only takes object names into account.
Vulture also detects unreachable code by looking for code after `return`, `break`, `continue` and `raise` statements, 
and by searching for unsatisfiable if- and while-conditions.


## Security checks

### [Bandit](https://pypi.org/project/bandit/)

Finds common security issues in Python code.
For every single file, Bandit builds an AST, and runs plugins (i.e. tests) against the AST nodes.
Bandit supports many different plugins (i.e. tests) to detect various security issues. 

### [Dependabot](https://docs.github.com/en/code-security/dependabot)

GitHub's built-in feature to keep the supply chain secure.
Dependabot monitors vulnerabilities in dependencies used in a project 
and keep the dependencies up-to-date.

### [CodeQL](https://codeql.github.com/)

Semantic code analysis engine by GitHub.
CodeQL lets you query code as though it were data. 
Write a query to find all variants of a vulnerability, eradicating it forever. 
Then share your query to help others do the same. 
CodeQL is free for research and open source,
and can be activated in the GitHub settings of a repository.

### [Gitleaks](https://gitleaks.io/)

Secret scanner for git repositories, available as GitHub action.



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







# Docstrings

Wir benutzen Google Style Docstrings ohne typing.
Sollte eingestellt werden in PyCharm > Settings > Tools > Python Integrated Tools > Docstring format
resp. in VS Code > Auto Docstring: Docstring Format > google-notypes

<https://sphinxcontrib-napoleon.readthedocs.io/en/latest/index.html>:
RST (ReStructuredText) is great, but it creates visually dense, hard to read docstrings. 
Napoleon is a Sphinx extension that enables Sphinx to parse both NumPy and Google style docstrings

There are at least four “flavors” of docstrings in common use today; Epytext, Sphinx, NumPy, and Google. 
Each of these docstring flavors follow the PEP 257 convention requirements. 
What differs between the three docstring flavors is the reST syntax used in the parameter description of the multi-line docstring.

For example, here is how each syntax documents function arguments.

Epytext syntax:

@type num_dogs: int
@param num_dogs: the number of dogs

Sphinx syntax:

:param param1: The first parameter, defaults to 1.
:type: int

Google syntax:

Args:
    param1 (int): The first parameter.

NumPy syntax:

Parameters
----------
param1 : int
    The first parameter.

