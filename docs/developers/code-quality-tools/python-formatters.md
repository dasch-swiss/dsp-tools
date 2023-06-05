[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Python: formatters

There is a variety of style checkers (tools that give a feedback) 
and autoformatters (tools that are able to fix the formatting violations automatically):

## [pycodestyle](https://pypi.org/project/pycodestyle/)

Checks Python code against some of the style conventions in [PEP 8](http://www.python.org/dev/peps/pep-0008/).

## [autopep8](https://pypi.org/project/autopep8/)

Automatically fixes most of the formatting issues reported by pycodestyle.
Since PEP 8 is rather liberal, autopep8/pycodestyle don't modify code too much.

## [black](https://pypi.org/project/black/)

A PEP 8 compliant opinionated autoformatter with its own style, going further than autopep8/pycodestyle.
Style configuration options are deliberately limited to a minimum.
Black aims for readability and reducing git diffs.

## [yapf](https://pypi.org/project/yapf/)

Autoformatter that can be configured to support different styles.

## [isort](https://pypi.org/project/isort/)

Sorts imports alphabetically, and separates them into sections, according to their type.
