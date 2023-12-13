[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Python Formatting

There is a variety of style checkers (tools that give a feedback) 
and auto-formatters (tools that are able to fix the formatting violations automatically).

## Existing Type Checkers and Auto-Formatters

### [pycodestyle](https://pypi.org/project/pycodestyle/)

Checks Python code against some style conventions in [PEP 8](http://www.python.org/dev/peps/pep-0008/).

### [autopep8](https://pypi.org/project/autopep8/)

Automatically fixes most of the formatting issues reported by pycodestyle.
Since PEP 8 is rather liberal, autopep8/pycodestyle don't modify code too much.

### [Black](https://pypi.org/project/black/)

A PEP 8 compliant opinionated auto-formatter with its own style, going further than autopep8/pycodestyle.
Style configuration options are deliberately limited to a minimum.
Black aims for readability and reducing git diffs.
Black is an easy-to-use tool, with sensible and useful defaults.
Its style is very elegant.

### [Ruff](https://pypi.org/project/ruff/)

Besides being a linter, Ruff is also an auto-formatter.
It is designed as a drop-in replacement for Black.

### [yapf](https://pypi.org/project/yapf/)

Auto-formatter that can be configured to support different styles.

### [isort](https://pypi.org/project/isort/)

Sorts `import` statements alphabetically, and separates them into sections, according to their type.
