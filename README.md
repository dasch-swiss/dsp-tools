[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS - DaSCH Service Platform Tools

dsp-tools is a command line tool that helps you to interact with the DaSCH Service Platform API. Consult the full 
documentation [here](https://docs.dasch.swiss/latest/DSP-TOOLS).


## Information for developers

There is a `Makefile` for all the following tasks (and more). Type `make` to print the available targets. 

For a quick start, use: 
```bash
pip install pipenv
pipenv install --dev
pipenv run make install
```

This creates a pipenv-environment, installs all dependencies, and installs `dsp-tools` from source.

If you prefer getting around pipenv, use instead:
```bash
make install-requirements
make install
```



## Packaging 

build frontend: build
build backend: setuptools (using setuptools as all-inclusive is deprecated: setup.py sdist bdist_wheel)
all infos in pyproject.toml, except some that don't work there are in manifest.in
src layout

instead of testing the local code, test the editable installation: https://stackoverflow.com/a/4780549/14414188. 
This is done in the GitHub actions when `make install` is called before the tests are executed. This makes 
the package `dsp_tools` directly accessible in the import statements, identically to copies installed on a 
customer's machine. Otherwise, it would be necessary to `from dsp_tools.models.x import Y` - 
but that would break on the customer's machine, because he doesn't have `src`.

This also solves another problem: 
Assume that inside a Python file from `src/dsp_tools/utils`, I would import a class from another Python file in 
`src/dsp_tools/models`: If I cannot access the other file via `from dsp_tools.models.x import Y`, and also not via 
`from dsp_tools.models.x import Y`, I would think to do it with a relative import: `from ..models.x import Y`. This 
would work in the IDE, but when executing test with pytest, it would not, because Relative imports depend on the 
location of the file that is run. https://stackoverflow.com/a/57292232/14414188

For this reason, you always have to make an editable install before working with the dsp-tools repository



## Git submodules

This repository embeds [https://github.com/dasch-swiss/0123-import-scripts](https://github.com/dasch-swiss/0123-import-scripts) 
as a Git submodule in `src/dsp_tools/import_scripts`. That means that `src/dsp_tools/import_scripts` has no contents, but
only a reference to a certain commit in the main branch of `0123-import-scripts`. When you clone `dsp-tools` from GitHub 
as usual, `src/dsp_tools/import_scripts` will be empty.


### Passively using the contents of the submodule

If you don't have a clone of dsp-tools yet, clone it with 

```bash
git clone --recurse-submodules https://github.com/dasch-swiss/dsp-tools.git
```

After cloning it that way, and after some time has passed, you might want to get the latest changes from GitHub:

```bash
cd dsp-tools
git pull --recurse-submodules
```

These two commands take care of the submodule, so that its contents are cloned/pulled as well. 

In case you have an old clone of dsp-tools, without the submodule, and you want to update it, you have to proceed 
differently: 

```bash
cd dsp-tools
git pull
git submodule update --init --recursive
```

Some notes:
 - `git clone --recurse-submodules <repo>` is shorthand for `git clone <repo>; cd <repo>; git submodule update --init --recursive`
 - `git pull --recurse-submodules` is shorthand for `git pull; git submodule update --init --recursive`
 - `--init` is necessary if you don't have the submodule `src/dsp_tools/import_scripts` yet. In all successive calls, 
   when the submodule is already on your machine, the flag `--init` can be omitted.
 - `--recursive` is optional, in case there would be more than one (nested) submodules inside dsp-tools. 
 - Since Git 2.15, you can tell Git to use `--recurse-submodules` for all commands that support it (except `clone`), 
   with `git config submodule.recurse true`.
 - These explanations rely on [the official Git Submodules documentation](https://git-scm.com/book/en/v2/Git-Tools-Submodules)


### Actively working with the contents of the submodule

After retrieving the contents of a submodule as described in the paragraph above, it is in "detached HEAD" state. Before 
committing to it, the `main` branch needs to be checked out. The order how to proceed is the following:

```bash
cd src/dsp_tools/import_scripts
git checkout main                     # check out main branch of 0123-import-scripts
# (modify contents of submodule)
git add .
git commit -m "modify submodule"
git push origin main                  # push to origin of 0123-import-scripts
cd ../../..
git add src/dsp_tools/import_scripts
git commit -m "modify submodule"
git push origin feature-branch        # push to origin of dsp-tools
```

When switching between branches, there are two options:

1. By default (`submodule.recurse` is false AND branches are switched with `git checkout <branch>`), the contents of 
  submodules will not be updated.
2. If `submodule.recurse` has been set to true, OR if branches are switched with `git checkout <branch> 
    --recurse-submodules`, the contents of submodules will be updated according to the commit recorded in the 
   superproject. If local modifications in a submodule would be overwritten, the checkout will fail.

To quickly switch between branches when you have uncommitted work in the submodule, the first option might be 
preferable. After merging a Pull Request and switching back to the main branch, the second option might be more 
suitable. Read more about the checkout options in 
[the official documentation](https://git-scm.com/docs/git-checkout#Documentation/git-checkout.txt---recurse-submodules)



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
 - `make freeze-requirements` to update the requirement files

`make freeze-requirements` must also be executed after adding a new dependency. If you prefer working 
without pipenv, you can freeze your requirements with `pip3 freeze > requirements.txt`.


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
[Pull Request Guidelines](https://docs.dasch.swiss/latest/developers/dsp/contribution/#pull-request-guidelines). If done
correctly, when merging a pull request into `main`, the `release-please` action will create or update a release 
PR. This PR will follow semantic versioning and update the change log. Once all desired features are
merged, the release can be executed by merging this release pull request into `main`. This will trigger actions that
create a release on GitHu and on PyPI.

Please ensure you have only one pull request per feature.


### Publishing manually

Publishing is automated with GitHub Actions and should _not_ be done manually. If you still need to do it, follow the
steps below.

Generate the distribution package:

```bash
make dist
```

You can install the package locally from the dist:

```bash
python3 -m pip ./dist/some_name.whl
```

Upload package works also with `make`:

```bash
make upload
```



## Contributing to the documentation

The documentation is a collection of [markdown](https://en.wikipedia.org/wiki/Markdown) files in the `docs` folder.  
After updates of the files, build and check the result with the following command:

```bash
make docs-serve 
```

The documentation is published on https://docs.dasch.swiss/latest/DSP-TOOLS. During the centralized release process of all
components of the DSP software stack, the docs of dsp-tools get built from the main branch to https://docs.dasch.swiss.
