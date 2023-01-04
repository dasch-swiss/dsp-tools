[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP-TOOLS - DaSCH Service Platform Tools

dsp-tools is a command line tool that helps you to interact with the DaSCH Service Platform API. This document is 
intended for developers who want to work with the code of DSP-TOOLS. 

| Hint                                                                                                                                                       |
|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| If you are a normal user of DSP-TOOLS, consult the [end user documentation](https://docs.dasch.swiss/latest/DSP-TOOLS) instead of this technical document. |



## Toolbox for dependency management, packaging, and distribution

There are a number of tasks necessary to develop and distribute a Python package, and a number of tools to assist with 
these processes. The [Python Packaging User Guide](https://packaging.python.org) lists the following, among others:

| Task                   | poetry | Hatch | pipenv | venv | build | setuptools | flit | twine |
|------------------------|--------|-------|--------|------|-------|------------|------|-------|
| Dependency management  | X      |       | X      |      |       |            |      |       |
| Virtual environment    | X      | X     | X      | X    |       |            |      |       |
| Build frontend         | X      | X     |        |      | X     |            |      |       |
| Build backend          | X      | X     |        |      |       | X          | X    |       |
| Publishing to pypi.org | X      | X     |        |      |       |            | X    | X     |

DSP-TOOLS uses [poetry](https://python-poetry.org) for all of these tasks. This allows us to use one single tool 
for all processes, and to keep the number of configuration files at a minimum. 

There are many configuration and metadata files that can be found on the top level of a Python repository. The ones 
used in the DSP-TOOLS repository are:

| file           | purpose                                                                         |
|----------------|---------------------------------------------------------------------------------|
| README.md      | Markdown-formatted infos for developers                                         |
| pyproject.toml | Modern configuration/metadata file replacing the deprecated files listed below  |
| .gitignore     | List of files not under version control (won't be uploaded to GitHub)           |
| .gitmodules    | DSP-TOOLS contains a Git submodule (more infos below)                           |
| CHANGELOG.md   | Markdown-formatted release notes (must not be edited by hand)                   |
| LICENSE        | Text file with the license how to use the source code of DSP-TOOLS              |
| Makefile       | Definition of commands that can be executed with `make [command]`               |
| poetry.lock    | Pinned versions of all (sub-) dependencies, allows a deterministic installation |
| mkdocs.yml     | Configuration of `mkdocs`, used to build the documentation webpage              |

In earlier times, there were some more configuration files, but thanks to poetry, they are not necessary anymore:

| Deprecated file      | Replaced by                             | Replaced by                                          |
|----------------------|-----------------------------------------|------------------------------------------------------|
| MANIFEST.in          | files to include into distribution      | pyproject.toml: [tool.poetry.include]                |
| setup.py             | project metadata, dependencies          | pyproject.toml                                       |
| setup.cfg            | configuration for setuptools            | pyproject.toml                                       |
| requirements.txt     | all (sub-) dependencies                 | pyproject.toml: [tool.poetry.dependencies]           |
| dev-requirements.txt | additional dependencies for development | pyproject.toml: [tool.poetry.group.dev.dependencies] |
| Pipfile              | direct dependencies                     | pyproject.toml: [tool.poetry.dependencies]           |
| Pipfile.lock         | pinned dependencies                     | poetry.lock                                          |



### Dependency management

#### Historical considerations

The classic way to manage the dependencies was to write the required packages by hand into a `requirements.txt` and 
into a `setup.py` file. 

But this is cumbersome and error-prone, so there was a time when [pipenv](https://pipenv.pypa.io/en/latest/) was the 
way to go: Pipenv introduced the important distinction between (a) dependencies necessary to run the application, 
(b) dependencies necessary for development, and (c) sub-dependencies, i.e. dependencies of your dependencies. Another 
useful concept of pipenv is the distinction between a human-friendly list of (mostly unpinned) direct dependencies and 
a machine-friendly definition of exact (pinned) versions of all dependencies.  
But since pipenv has no packaging functionality, it was necessary to sync the dependency definitions from `Pipfile` to  
`requirements.txt` and `setup.py`.  

`setup.py`, too, is problematic, especially 
[calling `setup.py sdist bdist_wheel`](https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html#summary). 
Python projects should define their dependencies and metadata in the modern `pyproject.toml` file. So it is 
necessary to dynamically manage the dependencies in `pyproject.toml`. And poetry seems to be the only tool capable 
of doing this.


#### Using poetry for dependency management

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
 - `poetry.lock` enables deterministic installations, by exactly pinning the version of all (sub-) dependencies. 
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



### Using the virtual environment

`poetry shell` spawns a shell within the virtual environment. From there, the command `dsp-tools` is available, 
because `poetry install` made an editable installation of DSP-TOOLS inside the virtual environment. This means that 
inside the `site-packages` folder of your poetry virtual environment, there is a folder called `dsp_tools-[version].
dist-info` containing a link to your local clone of the DSP-TOOLS repository. When you call `dsp-tools` from within 
the virtual environment, the code of your local clone will be executed.


### Packaging 

All project metadata, together with the dependencies and the configuration of the packaging tool poetry, is defined in 
`pyproject.toml`. The authoritative resource on how to create this file is 
[https://packaging.python.org/en/latest/specifications/declaring-project-metadata](https://packaging.python.org/en/latest/specifications/declaring-project-metadata).

The table `[build-system]` of `pyproject.toml` tells frontend build tools what backend build tool to use. The backend 
doesn't need to be installed. It will be installed by the frontend in a temporary, isolated environment for use during 
the build process. DSP-TOOLS uses poetry as both frontend and backend.

What happens when a distribution package of DSP-TOOLS is created? Poetry creates two files in the `dist` folder: a `.
tar.gz` compressed archive (the sdist or source distribution) and a `.whl` file (a wheel). Both contain the contents of 
the `src` folder plus some metadata - they are equivalent. They are then uploaded to the 
[Python Package Index](https://pypi.org/).  

When a user installs DSP-TOOLS via `pip install dsp-tools`, pip takes the sdist or the wheel, unpacks it, and copies 
it into the `site-packages` folder of the user's Python installation. As a result, the user has the same packages in 
their `site-packages` folder as the `src` folder of the dsp-tools repository. In our case, this the `dsp_tools` package. 
Since `site-packages` is on `sys.path`, the user can then import the package `dsp_tools` in his script.

Putting all packages into a `src` folder has an important consequence: It forces the developer to work with an 
editable installation of his package. Why? Without editable installation, it is impossible to write correct import 
statements. `from src.package import module` will not work, because the user has `package` installed, not `src`. And 
relative imports like `import module` will not work either, because when the tests code (situated in a separate 
`test` folder) imports the actual code, the relative imports in the actual code fail. This is because relative imports 
depend on the location of the file that is run, not on the file that contains the import statement. 

The solution is to always have an editable installation of the package under development. Poetry does this 
automatically when you execute `poetry install`. This makes the package `dsp_tools` importable - just like on a 
user's machine. And exactly this is the big advantage: With the src layout + editable installation, the setup on the 
developer's machine is more similar to the user's setup than with any other project layout. 

The concrete advantages of the src layout are:

- import parity
- The tests run against the package as it will be installed by the user - not against the situation in the 
  developer's repository.
- It is obvious to both humans and tools if a folder is a package to be distributed, or not.
- The editable installation is only able to import files that will also be importable in a regular installation.
- For the developer, the working directory is the root of the repository, so the root will implicitly be included in 
  `sys.path`. Users will never have the same current working directory than the developer. So, removing the packages 
  from the root by putting them into `src` prevents some practices that will not work on the user's machine. 

These things are better explained by the following, often-cited readings:

- [https://blog.ionelmc.ro/2014/05/25/python-packaging](https://blog.ionelmc.ro/2014/05/25/python-packaging)
- [https://hynek.me/articles/testing-packaging](https://hynek.me/articles/testing-packaging)
- [https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout)



### Publishing/distribution

Publishing is automated with GitHub Actions and should _not_ be done manually. Please follow the
[Pull Request Guidelines](https://docs.dasch.swiss/latest/developers/dsp/contribution/#pull-request-guidelines). If done
correctly, when merging a pull request into `main`, the `release-please` action will create or update a release 
PR. This PR will follow semantic versioning and update the change log. Once all desired features are
merged, the release can be executed by merging this release pull request into `main`. This will trigger actions that
create a release on GitHub and on PyPI.

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




## User data in the folder `.dsp-tools`

DSP-TOOLS saves user data in the user's home directory, in the folder `.dsp-tools`. Here is an overview of its 
structure:

| folder     | command using it | description                                  |
|:-----------|:-----------------|:---------------------------------------------|
| xmluploads | `xmlupload`      | saves id2iri mappings and error reports      |
| docker     | `stack-up`       | files necessary to startup Docker containers |



## The `start-stack` command

This command starts Docker containers of DSP-API and DSP-APP, in the version that is running on [https://admin.dasch.
swiss](https://admin.dasch.swiss/help). In addition to the containers, a number of files from the DSP-API GitHub 
repository is necessary. The version of the docker images and these files must be the same. The version is hardcoded at the 
following places in the code:

- `knora/dsplib/docker/docker-compose.yml`: The 4 variables `services/{app,db,sipi,api}/image` must point to the 
  DockerHub image of the last deployed version
- `knora/dsplib/utils/stack_handling.py`: The variable `commit_of_used_api_version` must be the commit hash of DSP-API 
  of the version that is running on [https://admin.dasch.swiss](https://admin.dasch.swiss/help).



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
