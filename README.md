[![](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools) 
[![](https://img.shields.io/pypi/pyversions/dsp-tools.svg)](https://pypi.org/project/dsp-tools/) 
[![](https://img.shields.io/badge/Python%20code%20style-black-000000.svg)](https://github.com/psf/black) 
[![](https://img.shields.io/badge/Python%20linting-pylint-darkgreen)](https://github.com/pylint-dev/pylint) 
[![](https://img.shields.io/badge/Python%20typing-mypy-darkgreen)](https://github.com/python/mypy) 
[![](https://img.shields.io/badge/Markdown%20linting-markdownlint-darkgreen)](
  https://github.com/igorshubovych/markdownlint-cli) 
[![](https://img.shields.io/badge/Link%20validation-markdown%20link%20validator-darkgreen)](
  https://www.npmjs.com/package/markdown-link-validator)


# DSP-TOOLS - DaSCH Service Platform Tools

DSP-TOOLS is a command line tool that helps you to interact with the DaSCH Service Platform API. 
This document is intended for developers who want to work with the code of DSP-TOOLS. 

| <center>Hint</center>                                                                                                                                                                |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| This technical document was written as a guide for developers. For the end user documentation, please consult [https://docs.dasch.swiss](https://docs.dasch.swiss/latest/DSP-TOOLS). |

This README contains basic information for getting started. 
More details can be found in the 
[developers documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers/index/).



## Quick start

To get started quickly, without reading the details, just execute these commands:

- `curl -sSL https://install.python-poetry.org | python3 -`
- `poetry self add poetry-exec-plugin`
- `poetry install`
- `poetry shell`
- `pre-commit install`
- `brew install imagemagick ffmpeg`

To learn more about the meaning of these commands, read the remainder of this README.



## Using poetry for dependency management

Curious what poetry is and why we use it? 
Check out the respective section in the
[developers documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers/packaging/).

If you want to work on the code of DSP-TOOLS, you first have to do the following:

- install poetry with `curl -sSL https://install.python-poetry.org | python3 -` 
  (for Windows, see [https://python-poetry.org/docs/](https://python-poetry.org/docs/))
- install the exec plugin with `poetry self add poetry-exec-plugin`
- execute `poetry install`, which will: 
    - create a virtual environment (if there isn't already one) 
    - install all dependencies (dev and non-dev) from `poetry.lock`. 
      If `poetry.lock` doesn't exist, 
      it installs the dependencies from `pyproject.toml`, 
      and creates a new `poetry.lock`.
    - make an editable installation of DSP-TOOLS inside the virtual environment

There are two files defining the dependencies:

- `pyproject.toml` lists the direct dependencies, ordered in two sections:
    - `[tool.poetry.dependencies]` lists the dependencies used to run the software.
    - `[tool.poetry.group.dev.dependencies]` lists the dependencies used for developing and testing.
- `poetry.lock` enables deterministic installations, 
  by exactly pinning the versions of all (sub-)dependencies. 
  This is done automatically, you must not edit `poetry.lock`.

If you want to install a new package, 
install it with `poetry add package`. This 

- installs the package (incl. sub-dependencies) in your virtual environment
- adds the package to the section `[tool.poetry.dependencies]` of `pyproject.toml`
- adds the pinned versions of the package and all sub-dependencies to `poetry.lock`

If a package is only needed for development, 
please install it with `poetry add package --group dev`,
so it will be added to the `[tool.poetry.group.dev.dependencies]` section of `pyproject.toml`.

For security reasons, the dependencies should be kept up to date.
GitHub's dependabot is configured to automatically create a version bumping PR 
if there is an update for a dependency.
Version bumping PRs can also be created manually: 
Execute `poetry add dependency@latest` for every dependency,
and create a PR from the resulting changes.

All developers working with the DSP-TOOLS repository should regularly execute `poetry self update` to update poetry, 
and `poetry install` to update the dependencies from `poetry.lock`.



## Using the virtual environment

`poetry shell` spawns a shell within the virtual environment. 
Even more convenient is to choose `/bin/python` inside poetry's virtual environment as the interpreter in your IDE.
This way, every Terminal you open in your IDE will automatically be in the virtual environment.

The advantage of being in a poetry shell is that the command `dsp-tools` is available, 
because `poetry install` made an editable installation of DSP-TOOLS inside the virtual environment. 
This means that inside the `site-packages` folder of your poetry virtual environment, 
there is a folder called `dsp_tools-[version].dist-info` 
containing a link to your local clone of the DSP-TOOLS repository. 
When you call `dsp-tools` from within the virtual environment, 
the code of your local clone will be executed.



## Using the git submodule

This repository embeds a git submodule that needs to be initialised before you can start working with a fresh clone. 
Find more information in the 
[developers documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers/git-submodules/).



## Publishing/distribution

Publishing is automated with GitHub Actions and should _not_ be done manually. 
Please follow the 
[Pull Request Guidelines](https://docs.dasch.swiss/latest/developers/contribution/#pull-request-guidelines). 
If done correctly, when merging a pull request into `main`, 
the `release-please` action will create or update a release PR. 
This PR will follow semantic versioning and update the change log. 
Once all desired features are merged, 
the release can be executed by merging this release pull request into `main`. 
This will trigger actions that create a release on GitHub and on PyPI.

Please ensure you have only one pull request per feature.



## Testing

The tests of this repository 
are written in the [unittest](https://docs.python.org/3/library/unittest.html) framework 
and executed with the [pytest](https://docs.pytest.org) framework.
There are two groups of tests: 
The ones in `test/unittests` can be run directly, 
whereas the ones in `test/e2e` need a DSP stack running in the background.
A DSP stack can be started with the command 
[`dsp-tools start-stack`](https://docs.dasch.swiss/latest/DSP-TOOLS/cli-commands/#start-stack)

It is possible to run all tests in a given folder: `pytest test/unittests`  
Or only the tests inside a singe file: `pytest test/unittests/test_excel2xml.py`  
Or even a certain method: `pytest test/unittests/test_excel2xml.py::TestExcel2xml::test_make_boolean_prop`  

This is useful in combination with the debugging mode of your IDE, 
if you want to examine why a single line of code in a test method fails.

Some e2e tests require ImageMagick and ffmpeg to be installed: `brew install imagemagick ffmpeg`



## Code style

When contributing to the project, 
please make sure you use the same code style rules as we do. 
We use 

- [markdownlint](https://github.com/igorshubovych/markdownlint-cli) (configured in `.markdownlint.yml`)
- [black](https://pypi.org/project/black/) (configured in `pyproject.toml`)
- [mypy](https://pypi.org/project/mypy/) (configured in `pyproject.toml`)
- [pylint](https://pypi.org/project/pylint/) (configured in `pyproject.toml`)
- [darglint](https://pypi.org/project/darglint/) (configured in `.darglint`)

These linters are integrated in the GitHub CI pipeline, 
so that every pull request is checked for code style violations.

In addition, there are [pre-commit hooks](#pre-commit-hooks) 
that run black and markdownlint locally before every commit.
This prevents you from committing code style violations.

To locally check your code for style violations, follow the instructions depending on your IDE:


### VSCode

In VSCode, 

- markdownlint can be installed as extension (`davidanson.vscode-markdownlint`), 
  and be configured in the  VSCode settings.
- black can be set as formatter in the `ms-python.python` extension.
  To do so, set `"python.formatting.provider": "black"` in the VSCode `settings.json`.
  Alternatively, `ms-python.black-formatter` can be installed as extension.
- mypy can be installed as extension (`matangover.mypy`), 
  and be configured in the VSCode settings.
    - This extension is different from the mypy functionality 
      of Microsoft's Python extension `ms-python.python`,
      which only lints each file separately, 
      leading to incomplete type checking.
- pylint can be installed as extension (`ms-python.pylint`), 
  and be configured in the VSCode settings.

If configured correctly, you will see style violations in the "Problems" tab.

Make sure to set the docstring format to "google-notypes" in the VSCode settings:
VS Code > Settings > Auto Docstring: Docstring Format > google-notypes.


### PyCharm

In PyCharm, mypy is available as [plugin](https://plugins.jetbrains.com/plugin/11086-mypy), 
and many style checks can be enabled in Settings > Editor > Inspections > Python.

Make sure to set the docstring format to "Google notypes" in the PyCharm settings:
PyCharm > Settings > Tools > Python Integrated Tools > Docstring format: Google notypes



## Pre-commit hooks

We use [pre-commit hooks](https://pre-commit.com/).
They are configured in `.pre-commit-config.yaml`.

If you try to make a commit,
the pre-commit hooks will be executed before the commit is created.

If a hook fails, the commit will be aborted.
Check the Git output to see what needs to be fixed.

If a hook modifies a file, the commit will be aborted.
You can then stage the changes made by the hook,
and commit again. 



## Contributing to the documentation

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

Please note that this is not the final form how the documentation will be published.
Rather, they are published together with the docs of DSP-API and DSP-APP on <https://docs.dasch.swiss/>. 
This happens by embedding all three repositories as git submodules 
into the central [dsp-docs](https://github.com/dasch-swiss/dsp-docs) repository.
If conflicting, the configurations of dsp-docs will override the configurations of the dsp-tools repository.
In rare cases, a certain syntax is correctly rendered locally, 
but not on <https://docs.dasch.swiss/latest/DSP-TOOLS>. 
In order to keep this difference minimal, 
`mkdocs.yml` of dsp-tools should be as similar as possible as `mkdocs.yml` of dsp-docs.

During the centralized deployment process of all components of the DSP software stack,
the docs of DSP-TOOLS get built from the latest release tag to <https://docs.dasch.swiss/latest/DSP-TOOLS>.
This means that in order to modify the contents of <https://docs.dasch.swiss/latest/DSP-TOOLS>, 
it is necessary to 

- merge the modifications into the main branch of the DSP-TOOLS repository
- release DSP-TOOLS
