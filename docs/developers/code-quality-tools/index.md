[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Code quality tools

There is a variety of tools that help to keep the code quality high.

DSP-TOOLS uses the following:

| Task                                                            | Tool                                                              | Configuration            |
| --------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------ |
| [General formatting](./other-formatters.md)                     | [EditorConfig](https://EditorConfig.org)                          | `.editorconfig`          |
| [Markdown: formatting](./other-formatters.md)                   | [markdownlint](https://github.com/igorshubovych/markdownlint-cli) | `.markdownlint.yml`      |
| [Python: formatting](./python-formatters.md)                    | [Black](https://pypi.org/project/black/)                          | `pyproject.toml`         |
| [Python: docstring formatter](./python-docstring-formatters.md) | pydocstyle                                                        |                          |
| Python: type checking                                           | [Mypy](https://pypi.org/project/mypy/)                            | `pyproject.toml`         |
| Python: linting                                                 | [Ruff](https://pypi.org/project/ruff) *                           |                          |
|                                                                 | [Pylint](https://pypyi.org/project/pylint) **                     | `pyproject.toml`         |
| Security checks                                                 | [Dependabot](https://docs.github.com/en/code-security/dependabot) | `.github/dependabot.yml` |
|                                                                 | [CodeQL](https://codeql.github.com/)                              | GitHub settings          |
|                                                                 | [Gitleaks](https://gitleaks.io/) *                                | `.gitleaks.toml`         |
|                                                                 | [Bandit](https://pypi.org/project/bandit/) *                      | `pyproject.toml`         |

* coming soon
** will perhaps become redundant, as Ruff matures

The decision to use this set of tools is based on the information in the following pages.













