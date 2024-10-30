[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Dependency Management, Packaging, and Distribution

## General Considerations

There are a number of tasks necessary to develop and distribute a Python package, 
and a number of tools to assist with these processes. 
The [Python Packaging User Guide](https://packaging.python.org/en/latest/key_projects/) lists the following, among others:

| Requirement            | uv  | poetry | Hatch | pdm | pipenv | venv | build | setuptools | flit | twine |
| ---------------------- | --- | ------ | ----- | --- | ------ | ---- | ----- | ---------- | ---- | ----- |
| Installable w/o Python | X   |        | X     |     |        |      |       |            |      |       |
| Install Python         | X   |        | X     | X   |        |      |       |            |      |       |
| Dependency management  | X   | X      |       | X   | X      |      |       |            |      |       |
| Virtual environment    | X   | X      | X     | X   | X      | X    |       |            |      |       |
| Build frontend         | X   | X      | X     | X   |        |      | X     |            |      |       |
| Build backend          |     | X      | X     | X   |        |      |       | X          | X    |       |
| Publishing to pypi.org |     | X      | X     | X   |        |      |       |            | X    | X     |

DSP-TOOLS uses [uv](https://docs.astral.sh/uv/) for most of these tasks. 

uv needs 3 config files:

- `pyproject.toml`: Manifest file, a modern configuration/metadata file replacing the deprecated files listed below
- `uv.lock`: Lock file, containing the pinned versions of all (sub-)dependencies, allowing a deterministic installation
- `.python-version`: tells uv which Python version to use when creating the project's virtual environment


## Is the tool dependent on a certain Python interpreter?

Many tools are written in Python and can only be installed by a Python interpreter. 
But unfortunately, Python can be installed in various ways, 
so that Python installations can live in many different places. 
And these locations are sometimes unstable. 

A concrete problem that often arises: 
When a Homebrew-installed Python is used to install the tool, 
a `brew upgrade` might break the tool.

Additionally, problems might arise if the tool is used to create a venv 
with a Python version higher than the Python that was used to install the tool. 

UV avoids all these problems: it is a static binary that doesn't depend on a Python installation.


## Dependency Management

The classic way to manage the dependencies was to write the required packages by hand into a `requirements.txt` and 
into a `setup.py` file. But this is cumbersome and error-prone.
Moreover, `setup.py` is problematic and not recommended anymore, especially calling
[`python setup.py`](https://packaging.python.org/en/latest/discussions/setup-py-deprecated/#setup-py-deprecated). 
Python projects should define their dependencies and metadata in the modern `pyproject.toml` file. 

So it is necessary to dynamically manage the dependencies in `pyproject.toml`. 
And [uv](https://docs.astral.sh/uv/) is one of the few tools capable of doing this.

uv is one of the few tools that cleanly distinguishes 

- dependencies necessary to run the application, 
- dependencies necessary for development, and 
- transitive dependencies, i.e. dependencies of your dependencies. 

It is also one of the few tools that makes the distinction between 

- the manifest file, i.e. a human-friendly list of (mostly unpinned) direct dependencies and 
- the lock file, i.e. a machine-friendly definition of exact (pinned) versions of all dependencies.


## Packaging 

All project metadata, together with the dependencies and the configuration of the packaging tool hatchling,
is defined in `pyproject.toml`. 
The authoritative resource on how to create this file is 
[https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml](
  https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#writing-pyproject-toml).

The table `[build-system]` of `pyproject.toml` tells frontend build tools what backend build tool to use. The backend 
doesn't need to be installed. It will be installed by the frontend in a temporary, isolated environment for use during 
the build process. DSP-TOOLS uses uv as frontend and hatchling as backend.

What happens when a distribution package of DSP-TOOLS is created? 
uv creates two files in the `dist` folder: 
a `.tar.gz` compressed archive (the sdist or source distribution) and a `.whl` file (a wheel). 
Both contain the contents of the `src` folder plus some metadata - they are equivalent. 
They are then uploaded to the [Python Package Index (PyPI)](https://pypi.org/).  

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

The solution is to always have an editable installation of the package under development. uv does this 
automatically. This makes the package `dsp_tools` importable - just like on a 
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
