[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Python Linting

## Existing Linters

### [Pylint](https://pypi.org/project/pylint/)

Checks Python code against a very broad list of rules, 
some of which are purely formatting oriented, 
but some of which are very sophisticated code smell and error detectors.
Pylint is very slow, but perhaps the most thorough linter around. 
A big plus is that it makes an inference of actual types, 
instead of relying on type annotations.

### [Pyflakes](https://pypi.org/project/pyflakes/)

A pure error detector, without formatting checks, and without configuration options.
It is faster than Pylint, because it doesn't dig as deep
(e.g., it examines the syntax tree of each file individually).

### [Flake8](https://pypi.org/project/flake8/)

Flake8 checks Python code by wrapping the output of these tools:

- Pyflakes (pure error detector)
- pycodestyle (pure style checker)
- McCabe (complexity checker)

Unlike Pyflakes, Flake8 can be configured.

### [Ruff](https://pypi.org/project/ruff/)

The fastest, most promising and most exciting linter, although still in beta.
Ruff is a linter with autofix support.
It has near-parity with Flake8, and they are working on implementing pylint rules as well
(see [How Does Ruff's Linter Compare to Pylint?](
    https://docs.astral.sh/ruff/faq/#how-does-ruffs-linter-compare-to-pylint)).
Ruff can be used to replace 

- Flake8 (wrapper around Pyflakes, pycodestyle, and McCabe) plus dozens of plugins
- Pyflakes (error detector)
- pycodestyle (checks formatting for violations of PEP 8)
- McCabe (complexity checker)
- isort (sorts imports alphabetically)
- pydocstyle (docstring checker)
- yesqa (tool to remove unnecessary `# noqa` comments)
- eradicate (removes commented-out code)
- pyupgrade (automated upgrade to newer python syntax)
- autoflake (automated removal of unused imports or variables)

Additionally, Ruff's formatter can be used to replace Black.

### [Vulture](https://pypi.org/project/vulture/)

Static code analyzer that finds unused code in Python programs. 
Vulture uses the ast module to build abstract syntax trees for all given files. 
While traversing all syntax trees it records the names of defined and used objects. 
Afterwards, it reports the objects which have been defined, but not used. 
This analysis ignores scopes and only takes object names into account.
Vulture also detects unreachable code by looking for code after `return`, `break`, `continue` and `raise` statements, 
and by searching for unsatisfiable if- and while-conditions.
