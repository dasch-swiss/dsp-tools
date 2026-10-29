[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Code Quality Tools

DSP-TOOLS uses the tools listed on this page to keep code quality high.

| Task                                          | Tool                                                               | Configuration            |
|-----------------------------------------------|--------------------------------------------------------------------|--------------------------|
| [General formatting](./general-formatting.md) | [EditorConfig](https://EditorConfig.org/)                          | `.editorconfig`          |
|                                               | [MarkdownLint](https://github.com/igorshubovych/markdownlint-cli/) | `.markdownlint.yml`      |
| Python formatting                             | [Ruff](https://pypi.org/project/ruff/)                             | `pyproject.toml`         |
| Python docstring formatting                   | [Ruff](https://pypi.org/project/ruff/)                             | `pyproject.toml`         |
| Python type checking                          | [mypy](https://pypi.org/project/mypy/)                             | `pyproject.toml`         |
| Python linting                                | [Ruff](https://pypi.org/project/ruff/)                             | `pyproject.toml`         |
| [Security checks](./security.md)              | [Dependabot](https://docs.github.com/en/code-security/dependabot)  | `.github/dependabot.yml` |
|                                               | [CodeQL](https://codeql.github.com/)                               | GitHub settings          |
|                                               | [Gitleaks](https://gitleaks.io/) *                                 | `.gitleaks.toml`         |
|                                               | [Ruff](https://pypi.org/project/ruff/) (`S` rules)                 | `pyproject.toml`         |

(*) coming soon

Docstrings use the
[Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
without typing.
