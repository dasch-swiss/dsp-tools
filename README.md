[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS - DaSCH Service Platform Tools
dsp-tools is a command line tool that helps you interacting with the DaSCH Service Platform API.  
Go to [Full Documentation](https://dasch-swiss.github.io/dsp-tools/)

## Information for developers
There is a `Makefile` for all the following tasks (and more). Type `make` to print the available targets. 

For a quick start, use: 
```
pip install pipenv
pipenv install --dev
pipenv run make run
```

This creates a pipenv-environment, installs all dependencies, and installs `dsp-tools` from source.

If you prefer getting around pipenv, use instead:
```bash
make upgrade-dist-tools
make install-requirements
make run
```

## Pipenv
We use pipenv for our dependency management. There are two ways to get started:
 - `pipenv install --dev` installs all dependencies, while giving them the opportunity to update themselves
 - `pipenv install --ignore-pipfile` is used to get a deterministic build in production

This works because there are two files defining the dependencies:
 - `Pipfile` replaces `requirements.txt`, but lists only the core dependencies, ordered in two sections:
   - `[packages]` lists the dependencies used to run the software.
   - `[dev-packages]` lists additional dependencies used for tests and deployment.
 - `Pipfile.lock` enables deterministic builds, by exactly pinning the version of all (sub-) dependencies. 
   This is done automatically, you must not edit `Pipfile.lock`.

The diverse `requirements.txt` files in this repo are only present for backwards compatibility
and for GitHub CI.

If you want to install a new package, install it with `pipenv install package`. This 
 - installs the package (incl. sub-dependencies) in your virtual environment
 - adds the package to the section `[packages]` of `Pipfile`. By default, no versions are pinned
 - adds the pinned versions of package and all sub-dependencies to `Pipfile.lock`

If a package is only needed for development, please install it with `pipenv install package --dev`,
so it gets added to the `[dev-packages]` section of `Pipfile`.

For security reasons, the maintainer regularly executes
 - `pipenv check` to get informed about vulnerabilities
 - `pipenv update` to update `Pipfile.lock` with the latest version of every package
 - `make freeze-requirements` to update the requirement files and `setup.py`

`make freeze-requirements` must also be executed after adding a new dependency. If you prefer working 
without pipenv, you can freeze your requirements with `pip3 freeze > requirements.txt` and update `setup.py`
manually.

### Pipenv setup in PyCharm
 - Go to Add Interpreter > Pipenv Environment
 - Base Interpreter: PyCarm auto-detects one of your system-wide installed Pythons as base interpreter. 
 - Pipenv executable: auto-detected
 - After hitting OK, PyCharm creates a new pipenv environment and installs the dependencies from `Pipfile`

If you already initialized a pipenv-environment via command line, you can add its interpreter in PyCharm,
but this will create the pipenv-environment again.

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

## Publishing
Publishing is automated with GitHub Actions and should _not_ be done manually. Please follow the
[Pull Request Guidelines](https://docs.dasch.swiss/developers/dsp/contribution/#pull-request-guidelines). If done
correctly, when merging a pull request into `main`, the `release-please` action will create or update a pull request for
a release. This pull request will follow semantic versioning and update the change log. Once all desired features are
merged, the release can be executed by merging this release pull request into `main`. This will trigger actions that
create a release on GitHub, on PyPI and the docs.

Please ensure you have only one pull request per feature.

## Publishing manually
Publishing is automated with GitHub Actions and should _not_ be done manually. If you still need to do it, follow the
steps below.

Generate the distribution package. Make sure you have the latest versions of `setuptools` and `wheel` installed:

```bash
python3 -m pip install --upgrade pip setuptools wheel
python3 setup.py sdist bdist_wheel
```

You can install the package locally from the dist:

```bash
python3 -m pip ./dist/some_name.whl
```

Upload package works also with `make`:

```bash
make dist
make upload
```

For local development:

```bash
python3 setup.py develop
```

## Contributing to the documentation
The documentation is a collection of [markdown](https://en.wikipedia.org/wiki/Markdown) files in the `docs` folder.  
After updates of the files, build and check the result with the following commands:

```bash
make docs-build
make docs-serve 
```

To update the changes to the official documentation pages run:

```bash
make docs-publish
```
