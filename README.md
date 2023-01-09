[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS - DaSCH Service Platform Tools

DSP-TOOLS is a command line tool that helps you to interact with the DaSCH Service Platform API. This document is 
intended for developers who want to work with the code of DSP-TOOLS. 

| Hint                                                                                                                                                         |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| If you aren't a developer, you might find the [end user documentation](https://docs.dasch.swiss/latest/DSP-TOOLS) more helpful than this technical document. |

This README contains basic information for getting started. More details can be found in the 
[developers documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers-index/).



## Using poetry for dependency management

Curious what poetry is and why we use it? Check out the 
[developers documentation](https://docs.dasch.swiss/latest/DSP-TOOLS/developers-packaging/).

If you want to work on the code of DSP-TOOLS, you first have to do a `make install`, which will

 - install poetry with `curl -sSL https://install.python-poetry.org | python3 -` (for Windows, see 
   [https://python-poetry.org/docs/](https://python-poetry.org/docs/))
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

Please note that testing requires launching the complete DSP API stack which is based on docker images. 
Therefore, we recommend installing the [docker desktop client](https://www.docker.com/products).  
To run the complete test suite:

```bash
make test
```



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

The documentation is a collection of [markdown](https://en.wikipedia.org/wiki/Markdown) files in the `docs` folder.  
After updates of the files, build and check the result with the following command:

```bash
make docs-serve 
```

The documentation is published on https://docs.dasch.swiss/latest/DSP-TOOLS. During the centralized release process of all
components of the DSP software stack, the docs of dsp-tools get built from the main branch to https://docs.dasch.swiss.
