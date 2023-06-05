[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Python: linters

## [Pylint](https://pypi.org/project/pylint/)

Checks Python code against a very broad list of rules, 
some of which are purley formatting oriented, 
but some of which are very sophisticated code smell and error detectors.
Pylint is very slow, but perhaps the most thorough linter around. 
A big plus is that it makes an inference of actual types, 
instead of relying on type annotations.

## [Pyflakes](https://pypi.org/project/pyflakes/)

A pure error detector, without formatting checks, and without configuration options.
It is faster than Pylint, because it doesn't dig as deep as Pylint 
(it examines the syntax tree of each file individually).
If you like Pyflakes but also want stylistic checks, you want flake8, which combines Pyflakes with style checks against PEP 8 and adds per-project configuration ability.

## [Flake8](https://pypi.org/project/flake8/)

Flake8 checks Python code by wrapping the output of these tools:

- Pyflakes (pure error detector)
- pycodestyle (pure style checker)
- [McCabe](https://pypi.org/project/mccabe/) (complexity checker)

Unlike Pyflakes, Flake8 can be configured.

## [Ruff](https://pypi.org/project/ruff/)

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

## [Vulture](https://pypi.org/project/vulture/)

Static code analyzer that finds unused code in Python programs. 
Vulture uses the ast module to build abstract syntax trees for all given files. 
While traversing all syntax trees it records the names of defined and used objects. 
Afterwards, it reports the objects which have been defined, but not used. 
This analysis ignores scopes and only takes object names into account.
Vulture also detects unreachable code by looking for code after `return`, `break`, `continue` and `raise` statements, 
and by searching for unsatisfiable if- and while-conditions.
