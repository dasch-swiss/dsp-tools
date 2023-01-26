[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS - DaSCH Service Platform Tools

DSP-TOOLS is a command line tool that helps you to interact with the DaSCH Service Platform API. This document is 
intended for developers who want to work with the code of DSP-TOOLS. 

| <center>Hint</center>                                                                                                                                                                |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| This technical document was written as a guide for developers. For the end user documentation, please consult [https://docs.dasch.swiss](https://docs.dasch.swiss/latest/DSP-TOOLS). |

This README contains basic information for getting started. More details can be found in the 
[developers documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers-index/).



## Using poetry for dependency management

Curious what poetry is and why we use it? Check out the respective section in the 
[developers documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers-packaging/).

If you want to work on the code of DSP-TOOLS, you first have to do the following:

 - install poetry with `curl -sSL https://install.python-poetry.org | python3 -` (for Windows, see 
   [https://python-poetry.org/docs/](https://python-poetry.org/docs/))
 - install the exec plugin with `poetry self add poetry-exec-plugin`
 - execute `poetry install`, which will: 
     - create a virtual environment (if there isn't already one) 
     - install all dependencies (dev and non-dev) from `poetry.lock`. If `poetry.lock` doesn't exist, it installs 
       the dependencies from `pyproject.toml`, and creates a new `poetry.lock`.
     - make an editable installation of DSP-TOOLS inside the virtual environment

There are two files defining the dependencies:

 - `pyproject.toml` lists the direct dependencies, ordered in two sections:
   - `[tool.poetry.dependencies]` lists the dependencies used to run the software.
   - `[tool.poetry.group.dev.dependencies]` lists the dependencies used for developing and testing.
 - `poetry.lock` enables deterministic installations, by exactly pinning the versions of all (sub-)dependencies. 
   This is done automatically, you must not edit `poetry.lock`.

If you want to install a new package, install it with `poetry add package`. This 

 - installs the package (incl. sub-dependencies) in your virtual environment
 - adds the package to the section `[tool.poetry.dependencies]` of `pyproject.toml`
 - adds the pinned versions of the package and all sub-dependencies to `poetry.lock`

If a package is only needed for development, please install it with `poetry add package --group dev`,
so it will be added to the `[tool.poetry.group.dev.dependencies]` section of `pyproject.toml`.

For security reasons, the maintainer regularly executes `poetry update` to update `poetry.lock` with the latest 
version of every package. The resulting changes are then committed in a version bumping PR.

All developers working with the DSP-TOOLS repository should regularly execute `poetry self update` to update poetry, 
and `poetry install` to update the dependencies from `poetry.lock`.



## Using the virtual environment

`poetry shell` spawns a shell within the virtual environment. From there, the command `dsp-tools` is available, 
because `poetry install` made an editable installation of DSP-TOOLS inside the virtual environment. This means that 
inside the `site-packages` folder of your poetry virtual environment, there is a folder called `dsp_tools-[version].
dist-info` containing a link to your local clone of the DSP-TOOLS repository. When you call `dsp-tools` from within 
the virtual environment, the code of your local clone will be executed.



## Using the git submodule

This repository embeds a git submodule that needs to be initialised before you can start working with a fresh clone. 
Find more information in the 
[developers documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers-git-submodules/).



## Publishing/distribution

Publishing is automated with GitHub Actions and should _not_ be done manually. Please follow the
[Pull Request Guidelines](https://docs.dasch.swiss/latest/developers/dsp/contribution/#pull-request-guidelines). If done
correctly, when merging a pull request into `main`, the `release-please` action will create or update a release 
PR. This PR will follow semantic versioning and update the change log. Once all desired features are
merged, the release can be executed by merging this release pull request into `main`. This will trigger actions that
create a release on GitHub and on PyPI.

Please ensure you have only one pull request per feature.



## Testing

The tests of this repository 
are written in the [unittest](https://docs.python.org/3/library/unittest.html) framework 
and executed with the [pytest](https://docs.pytest.org) framework.
There are two groups of tests: 
The ones in `test/unittests` can be run directly, 
whereas the ones in `test/e2e` need a DSP stack running in the background.
A DSP stack can be started with the command 
[`dsp-tools start-stack`](https://docs.dasch.swiss/latest/DSP-TOOLS/dsp-tools-usage/#simple-way-dsp-tools-start-stack)

It is possible to run all tests in a given folder: `pytest test/unittests`  
Or only the tests inside a singe file: `pytest test/unittests/test_excel2xml.py`  
Or even a certain method: `pytest test/unittests/test_excel2xml.py::TestExcel2xml::test_make_boolean_prop`  

This is useful in combination with the debugging mode of your IDE, 
if you want to examine why 
a single line of code in a test method fails.


## Code style

When contributing to the project please make sure you use the same code style rules as we do. We use
[autopep8](https://pypi.org/project/autopep8/) and [mypy](https://pypi.org/project/mypy/). The 
configuration is defined in `pyproject.toml` in the root directory of the project.

You can use the configuration with `autopep8 --global-config pyproject.toml [file path]` and 
`mypy --config-file pyproject.toml [file path]`.

If you are using PyCharm we recommend installing autopep8 as external tool. You can then use it with 
right-click on the file > `External Tools` > `autopep8` to reformat files in-place. Due to compatibility 
issues with VSCode, the argument  `--in-place=true` can not be declared in the `pyproject.toml` and 
needs to be passed to the external tool in the PyCharm settings.  
mypy is available as [plugin](https://plugins.jetbrains.com/plugin/11086-mypy).

In VSCode, both mypy and autopep8 can be set up as default linter and formatter through the python extension.

For formatting Markdown files (*.md) we use the default styling configuration provided by PyCharm.



## Contributing to the documentation

The documentation is a collection of [Markdown](https://en.wikipedia.org/wiki/Markdown) files in the `docs` folder.
They are converted to HTML with [MkDocs](https://pypi.org/project/mkdocs/).
We are gradually switching to [Semantic Line Breaks](https://sembr.org/),
so don't be confused to see unexpected line breaks.

The style can be adapted in the CSS file `docs/assets/style/theme.css`. 
The navigation bar and other configurations can be configured in the `mkdocs.yml` file.

After modifying the documentation, build and check the result with the following command:

```bash
mkdocs serve
```

This allows you to look at a preview of the documentation in a browser. 

Please note that this is not the final form how the documentation will be published.
Rather, they are published together with the docs of DSP-API and DSP-APP on https://docs.dasch.swiss/. 
This happens by embedding all three repositories as git submodules 
into the central [DSP-DOCS](https://github.com/dasch-swiss/dsp-docs) repository.
If conflicting, the CSS and other configurations there will override the configurations of the DSP-TOOLS repository.
In rare cases, a certain syntax is correctly rendered locally, 
but not on https://docs.dasch.swiss/latest/DSP-TOOLS. 

During the centralized release process of all components of the DSP software stack, 
the docs of DSP-TOOLS get built from the main branch to https://docs.dasch.swiss/latest/DSP-TOOLS.



### Styling constraints in the documentation

In our GitHub actions, we check PRs for dead links in the documentation. 
Our tool markdown-link-validator is only able to check internal links
if they start with `./`. For example:

- `[prefixes](./dsp-tools-create.md#prefixes-object)` instead of `[prefixes](dsp-tools-create.md#prefixes-object)`
- `![Colors_en](./assets/images/img-list-english-colors.png)` instead of `![Colors_en](assets/images/img-list-english-colors.png)`

It is okay, however, to make an internal link to a title of the current document: `[prefixes](#prefixes-object)`

Please follow this constraint, so that markdown-link-validator can check the internal links.

| <center>Hint</center>                                                                                                                                                                      |
|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| If your links are correct, but markdown-link-validator doesn't recognize them, it might be necessary to adapt the call to markdown-link-validator in `.github/workflows/tests-on-push.yml` |
