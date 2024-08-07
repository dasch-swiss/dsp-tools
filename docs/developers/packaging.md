[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Dependency Management, Packaging, and Distribution

## General Considerations

There are a number of tasks necessary to develop and distribute a Python package, and a number of tools to assist with 
these processes. The [Python Packaging User Guide](https://packaging.python.org) lists the following, among others:

| Task                   | poetry | Hatch | pipenv | venv | build | setuptools | flit | twine |
| ---------------------- | ------ | ----- | ------ | ---- | ----- | ---------- | ---- | ----- |
| Dependency management  | X      |       | X      |      |       |            |      |       |
| Virtual environment    | X      | X     | X      | X    |       |            |      |       |
| Build frontend         | X      | X     |        |      | X     |            |      |       |
| Build backend          | X      | X     |        |      |       | X          | X    |       |
| Publishing to pypi.org | X      | X     |        |      |       |            | X    | X     |

DSP-TOOLS uses [poetry](https://python-poetry.org) for all of these tasks. This allows us to use one single tool 
for all processes, and to keep the number of configuration files at a minimum. 

Poetry needs only 2 config files:

- `pyproject.toml`: Manifest file, a modern configuration/metadata file replacing the deprecated files listed below
- `poetry.lock`: Lock file, containing the pinned versions of all (sub-)dependencies, allowing a deterministic installation


## Dependency Management

The classic way to manage the dependencies was to write the required packages by hand into a `requirements.txt` and 
into a `setup.py` file. But this is cumbersome and error-prone.
Moreover, `setup.py` is problematic and not recommended anymore, especially 
[calling `setup.py sdist bdist_wheel`](https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html#summary). 
Python projects should define their dependencies and metadata in the modern `pyproject.toml` file. 

So it is necessary to dynamically manage the dependencies in `pyproject.toml`. 
And poetry seems to be the only tool capable of doing this.

Poetry is one of the few tools that cleanly distinguishes 

- dependencies necessary to run the application, 
- dependencies necessary for development, and 
- sub-dependencies, i.e. dependencies of your dependencies. 

It is also one of the few tools that makes the distinction between 

- the manifest file, i.e. a human-friendly list of (mostly unpinned) direct dependencies and 
- the lock file, i.e. a machine-friendly definition of exact (pinned) versions of all dependencies.  


## Packaging 

All project metadata, together with the dependencies and the configuration of the packaging tool poetry, is defined in 
`pyproject.toml`. The authoritative resource on how to create this file is 
[https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml](
  https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml).

The table `[build-system]` of `pyproject.toml` tells frontend build tools what backend build tool to use. The backend 
doesn't need to be installed. It will be installed by the frontend in a temporary, isolated environment for use during 
the build process. DSP-TOOLS uses poetry as both frontend and backend.

What happens when a distribution package of DSP-TOOLS is created? Poetry creates two files in the `dist` folder: a `.
tar.gz` compressed archive (the sdist or source distribution) and a `.whl` file (a wheel). Both contain the contents of 
the `src` folder plus some metadata - they are equivalent. They are then uploaded to the 
[Python Package Index (PyPI)](https://pypi.org/).  

When a user installs DSP-TOOLS with `pip install dsp-tools`, pip takes the sdist or the wheel, unpacks it, and copies 
it into the `site-packages` folder of the user's Python installation. As a result, the user has the same packages in 
his `site-packages` folder as the `src` folder of the dsp-tools repository. In our case, this is the `dsp_tools` 
package. Since `site-packages` is on `sys.path`, the user can then import the package `dsp_tools` in his script.


### Advantages of the src Layout

Putting all packages into a `src` folder has an important consequence: It forces the developer to work with an 
editable installation of his package. Why? Without an editable installation, it is impossible to write correct import 
statements. `from src.package import module` will not work, because the user has `package` installed, not `src`. And 
relative imports like `import module` will not work either, because when the test code (situated in a separate 
`test` folder) imports the actual code, the relative imports in the actual code fail. This is because relative imports 
depend on the location of the file that is run, not on the file that contains the import statement. 

The solution is to always have an editable installation of the package under development. Poetry does this 
automatically when you execute `poetry install`. This makes the package `dsp_tools` importable - just like on a 
user's machine. And exactly this is the big advantage: With the src layout and an editable installation, the setup on 
the developer's machine is more similar to the user's setup. 

The advantages of the src layout are:

- import parity
- The tests run against the package as it will be installed by the user - not against the situation in the 
  developer's repository.
- It is obvious to both humans and tools if a folder is a package to be distributed, or not.
- The editable installation is only able to import modules that will also be importable in a regular installation.
- For the developer, the working directory is the root of the repository, so the root will implicitly be included in 
  `sys.path`. Users will never have the same current working directory than the developer. So, removing the packages 
  from the root by putting them into `src` prevents some practices that will not work on the user's machine. 

For more in-depth explanations, please visit the following pages:

- [https://blog.ionelmc.ro/2014/05/25/python-packaging](https://blog.ionelmc.ro/2014/05/25/python-packaging)
- [https://hynek.me/articles/testing-packaging](https://hynek.me/articles/testing-packaging)
- [https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout)


## Publishing and Distribution

Publishing is automated with GitHub Actions and should _not_ be done manually. If you still need to do it, follow the
steps below.

Generate the distribution package:

```bash
poetry build
```

You can install the package locally from the dist:

```bash
pip install dist/some_name.whl
```

Upload package:

```bash
poetry publish
```
