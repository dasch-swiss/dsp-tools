[![](https://img.shields.io/pypi/v/dsp-tools.svg)](https://pypi.org/project/dsp-tools/) 
[![](https://img.shields.io/pypi/l/dsp-tools.svg)](https://pypi.org/project/dsp-tools/) 
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) 
[![](https://img.shields.io/badge/mypy-blue)](https://github.com/python/mypy) 
[![](https://img.shields.io/badge/markdownlint-darkgreen)](https://github.com/igorshubovych/markdownlint-cli) 
[![](https://img.shields.io/badge/markdown%20link%20validator-darkgreen)](https://www.npmjs.com/package/markdown-link-validator) 


# DSP-TOOLS - DaSCH Service Platform Tools

DSP-TOOLS is a command line tool that helps you to interact with the DaSCH Service Platform (DSP) API. 
This document is intended for developers who want to work with the code of DSP-TOOLS. 

| <center>Hint</center>                                                                                                 |
| :-------------------------------------------------------------------------------------------------------------------- |
| This technical document was written as a guide for developers.                                                        |
| For the end user documentation, please consult [https://docs.dasch.swiss](https://docs.dasch.swiss/latest/DSP-TOOLS). |

This README contains basic information for getting started. 
More details can be found in the [developers' documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers/).



## Quick Start

To get started quickly, without reading the details, just execute these commands.

- `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `uv sync --all-extras --dev`
- `source .venv/bin/activate`
- `pre-commit install`
- `npm install -g markdown-link-validator`
- `brew install just`

The remainder of this README explains these commands in more detail.



## Using UV to manage Python installations, virtual environments, and dependencies

Curious what uv is and why we use it? 
Check out the respective section in the
[developers' documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers/packaging/).

If you want to work on the code of DSP-TOOLS, you first have to do the following:

- Install uv with `curl -LsSf https://astral.sh/uv/install.sh | sh` 
- Execute `uv sync --all-extras --dev`, which will: 
    - Install an appropriate Python version, if it doesn't find one on your machine.
    - Create a virtual environment in the folder `.venv` (if there isn't already one).
    - Install all dependencies (dev and non-dev) from `uv.lock`. 
      If `uv.lock` doesn't exist, it installs the dependencies from `pyproject.toml` and creates a new `uv.lock`.
    - Make an editable installation of DSP-TOOLS inside the virtual environment.

There are two files defining the dependencies:

- `pyproject.toml` lists the direct dependencies, ordered in two sections:
    - `[project.dependencies]` lists the dependencies used to run the software.
    - `[tool.uv.dev-dependencies]` lists the dependencies used for developing and testing.
- `uv.lock` enables deterministic installations, by exactly pinning the versions of all (sub-)dependencies. 

If you want to install a new package, install it with `uv add package`.
If your new package is only used in test code, use `uv add --dev package` instead.

This

- Installs the package (incl. sub-dependencies) in your virtual environment,
- Adds the package to the section `[project.dependencies]` of `pyproject.toml`,
- Adds the pinned versions of the package and all sub-dependencies to `uv.lock`.

If a package is only needed for development, 
please install it with `uv add --dev package`,
so it will be added to the `[tool.uv.dev-dependencies]` section of `pyproject.toml`.

GitHub's dependabot is configured to automatically create a version bumping PR if there is an update for a dependency.
Version bumping PRs can also be created manually: run `uv lock --upgrade` and create a PR from the resulting changes.

All developers working with the DSP-TOOLS repository should regularly execute `uv self update` to update uv, 
and `uv sync` to update the dependencies from `uv.lock`.



## Using the Virtual Environment

`source .venv/bin/activate` activates the virtual environment. 
Set `.venv/bin/python` as the interpreter in your IDE, 
so that your IDE automatically activates the virtual env if you open a new terminal.

The advantage of being in a virtual environment is that the command `dsp-tools` is available, 
because `uv sync` installed an editable version of DSP-TOOLS inside the virtual environment. 
This means, that inside the `site-packages` folder of your virtual environment, 
there is a folder called `dsp_tools-[version].dist-info`, 
which contains a link to your local clone of the DSP-TOOLS repository. 
When you call `dsp-tools` from within the virtual environment, the code of your local clone will be executed.



## Publishing and Distribution

Publishing is automated with GitHub Actions. 
Please follow the 
[Pull Request Guidelines](https://docs.dasch.swiss/latest/developers/contribution/#pull-request-guidelines). 
When merging a pull request into `main`, the `release-please` action will create or update a release PR. 
This PR will follow semantic versioning and update the change log. 
Once all desired features are merged, the release can be published by merging this release pull request into `main`. 
This will trigger actions that create a release on GitHub and on PyPI.



## Testing

The tests of this repository 
are partially written in the [unittest](https://docs.python.org/3/library/unittest.html) framework,
and partially in the [pytest](https://docs.pytest.org) framework.

The following are self-contained and can be run without further requirements:

- `test/benchmarking`: Prevent that the stashing algorithm of the xmlupload becomes worse.
- `test/distribution`: 
  Make sure that the CLI entry point, all dependencies, and the resources are available on the end user's machine.
- `test/unittests`: Pure unit tests of lower-level functions.
- `test/integration`: Higher-level tests, with side effects like reading/writing operations on the file system.
- `test/e2e`: Tests interacting with a DSP-API instance, powered by test containers.

The following need a DSP stack running in the background.
A DSP stack can be started with the command 
[`dsp-tools start-stack`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#start-stack).

- `test/legacy-e2e`
  
  
Tests can be run in three different ways:

- Run all tests in a given folder: `pytest test/unittests`.
- Run only the tests inside a single file: `pytest test/unittests/test_excel2xml.py`.
- Run only the test for a single method: 
  `pytest test/unittests/test_excel2xml.py::TestExcel2xml::test_make_boolean_prop`.

This is useful in combination with the debugging mode of your IDE 
if you want to examine why a single line of code in a test method fails.



## Code Style

When contributing to the project, 
please make sure you use the same code style rules as we do. 
We use the following linters:

- [mypy](https://pypi.org/project/mypy/) (configured in `pyproject.toml`)
- [ruff](https://pypi.org/project/ruff/) (configured in `pyproject.toml`)
- [darglint](https://pypi.org/project/darglint/) (configured in `.darglint`)
- [markdown-link-validator](https://www.npmjs.com/package/markdown-link-validator) (no configuration)
- [MarkdownLint](https://github.com/igorshubovych/markdownlint-cli) (configured in `.markdownlint.yml`)
- [yamllint](https://pypi.org/project/yamllint/) (configured in `.yamllint.yml`)

These linters are integrated in the GitHub CI pipeline, 
so that every pull request is checked for code style violations.

Your code can be checked for style violations locally before they are committed:

- `just mypy`
- `just ruff-check`
- `just ruff-format-check`
- `just darglint`
- `just check-links`
- `just markdownlint`
- `yamllint .`

In addition, there are [pre-commit hooks](#pre-commit-hooks) 
that run Ruff and MarkdownLint locally before every commit.
This prevents you from committing code style violations.
Pre-commit is contained in the dependencies, 
but before the first use, the hooks must be installed with `pre-commit install`.

Depending on your IDE, there are extensions that emit warnings:


### VSCode

- **MarkdownLint** can be installed as an extension (`davidanson.vscode-markdownlint`), 
  and be configured in the VSCode settings.
- **mypy** can be installed as an extension (`matangover.mypy`), 
  and be configured in the VSCode settings.
    - This extension is different from the mypy functionality of Microsoft's Python extension `ms-python.python`,
      which only lints each file separately, leading to incomplete type checking.
- **ruff** can be installed as an extension (`charliermarsh.ruff`), 
  and be configured in the VSCode settings:
    - `settings.json` > `[python]` > `"editor.defaultFormatter": "charliermarsh.ruff"`
    - `settings.json` > `"ruff.format.args": ["--line-length=120"]`

If configured correctly, the style violations will be listed in the "Problems" tab.

Make sure to set the docstring format to "google-notypes" in the VSCode settings:
VS Code > Settings > Auto Docstring: Docstring Format > google-notypes.


### PyCharm

In PyCharm, mypy is available as [plugin](https://plugins.jetbrains.com/plugin/11086-mypy), 
and many style checks can be enabled in Settings > Editor > Inspections > Python.

Make sure to set the docstring format to "Google notypes" in the PyCharm settings:
PyCharm > Settings > Tools > Python Integrated Tools > Docstring format: Google notypes



## Pre-Commit Hooks

We use [pre-commit hooks](https://pre-commit.com/), which are configured in `.pre-commit-config.yaml`.

If you try to make a commit,
the pre-commit hooks will be executed before the commit is created.

If a hook fails, the commit will be aborted and the Git output will list the problems in your code.

If a hook modifies a file, the commit will be aborted.
You can then stage the changes made by the hook, and commit again. 



## Contributing to the Documentation

The documentation is a collection of [Markdown](https://en.wikipedia.org/wiki/Markdown) files in the `docs` folder.
They are converted to HTML with [MkDocs](https://pypi.org/project/mkdocs/).
We are gradually switching to [Semantic Line Breaks](https://sembr.org/),
so don't be confused to see unexpected line breaks.

The navigation bar and other configurations can be configured in the `mkdocs.yml` file.

After modifying the documentation, build and check the result with the following command:

```bash
mkdocs serve
```

This allows you to look at a preview of the documentation in a browser. 

Please note that this is not the final form in which the documentation will be published.
Rather, they are published together with the docs of DSP-API and DSP-APP on <https://docs.dasch.swiss/> 
by embedding all three repositories as git submodules 
into the central [dsp-docs](https://github.com/dasch-swiss/dsp-docs) repository.
If conflicting, the configurations of dsp-docs will override the configurations of the dsp-tools repository.
In rare cases, a certain syntax may be correctly rendered locally, 
but not on <https://docs.dasch.swiss/latest/DSP-TOOLS>. 
In order to keep this difference minimal, 
`mkdocs.yml` of dsp-tools should be as close as possible to the `mkdocs.yml` of dsp-docs.

During the centralized deployment process of all components of the DSP software stack,
the docs of dsp-tools get built from the latest release tag to <https://docs.dasch.swiss/latest/DSP-TOOLS>.

This means that in order to modify the contents of <https://docs.dasch.swiss/latest/DSP-TOOLS>, 
it is necessary to:

- Merge the modifications into the main branch of the dsp-tools repository,
- Release DSP-TOOLS.
