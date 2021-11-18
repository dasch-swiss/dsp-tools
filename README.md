[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS - DaSCH Service Platform Tools

dsp-tools is a command line tool that helps you interact with the DaSCH Service Platform API.

Go to [Full Documentation](https://dasch-swiss.github.io/dsp-tools/)

## Information for developers

There is a `Makefile` for all the following tasks (and more). Type `make` to print the available targets.

## Install from source

To install from source run:

```bash
python3 setup.py install
```

## Install the requirements

To install the requirements run:

```bash
pip3 install -r requirements.txt
```

To generate a requirements file (usually requirements.txt), that you commit with your project, run:

```bash
pip3 freeze > requirements.txt
```

## Testing

Please note that testing requires launching the complete DSP API stack which is based on docker images. Therefore, we
recommend installing the [docker desktop client](https://www.docker.com/products).

To run the complete test suite:

```bash
make test
```

## Code style

When contributing to the project please make sure you use the same code style rules as we do. We use
[autopep8](https://pypi.org/project/autopep8/) and [mypy](https://pypi.org/project/mypy/). The configuration is defined
in `pyproject.toml` in the root directory of the project.

```toml
[tool.autopep8]
max_line_length = 180
in-place = true
experimental = true

[tool.mypy]
ignore_missing_imports = true
follow_imports = "silent"
show_column_numbers = true
strict = true
```

You can use the configuration with `autopep8 --global-config pyproject.toml [file path]`
and `mypy --config-file pyproject.toml
[file path]`.

If you are using PyCharm we recommend installing autopep8 as external tool. You can then use it with right-click on the
file > `External Tools` > `autopep8` to reformat files in-place. mypy is available as
[plugin](https://plugins.jetbrains.com/plugin/11086-mypy).

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
