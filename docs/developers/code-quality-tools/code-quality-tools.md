[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Code Quality Tools

There are a variety of tools that help to keep code quality high.

DSP-TOOLS uses the ones listed on this page.

The decision to use this set of tools is based on the information in the following pages.

| Task                                                            | Tool                                                               | Configuration                  |
|-----------------------------------------------------------------|--------------------------------------------------------------------|--------------------------------|
| [General formatting](./general-formatting.md)                   | [EditorConfig](https://EditorConfig.org/)                          | `.editorconfig`                |
|                                                                 | [MarkdownLint](https://github.com/igorshubovych/markdownlint-cli/) | `.markdownlint.yml`            |
| [Python formatting](./python-formatting.md)                     | [Ruff](https://pypi.org/project/ruff/)                             | `pyproject.toml`               |
| [Python docstring formatting](./python-docstring-formatting.md) | [darglint](https://pypi.org/project/darglint/)                     | `.darglint`                    |
| [Python type checking](./python-type-checking.md)               | [mypy](https://pypi.org/project/mypy/)                             | `pyproject.toml`               |
| [Python linting](./python-linting.md)                           | [Ruff](https://pypi.org/project/ruff/)                             | `pyproject.toml`               |
| [Security checks](./security.md)                                | [Dependabot](https://docs.github.com/en/code-security/dependabot)  | `.github/dependabot.yml`       |
|                                                                 | [CodeQL](https://codeql.github.com/)                               | GitHub settings                |
|                                                                 | [Gitleaks](https://gitleaks.io/) *                                 | `.gitleaks.toml`               |
|                                                                 | [Bandit](https://pypi.org/project/bandit/)                         | `.github/workflows/bandit.yml` |

(*) coming soon  
