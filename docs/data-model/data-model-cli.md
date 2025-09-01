[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# CLI-Commands

## `create` - Create a Project on a Server

This command reads a JSON project definition (containing one or more data models)
and creates it on a DSP server.

```bash
dsp-tools create [options] project_definition.json
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
- `-V` | `--validate-only` (optional): validate the JSON file without creating it on the DSP server
- `-l` | `--lists-only` (optional): create only the lists (prerequisite: the project exists on the server)
- `-v` | `--verbose` (optional): print more information about the progress to the console
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The defaults are intended for local testing: 

```bash
dsp-tools create project_definition.json
```

This will create the project defined in `project_definition.json` on `localhost` for local viewing.

In order to create the same project
on the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools create -s https://api.dasch.swiss -u 'your@email.com' -p 'password' project_definition.json
```

The expected JSON format is [documented here](./json-project/overview.md).



## `get` - Download a Project from a Server

This command retrieves a project with its data model(s) from a DSP server 
and writes it into a JSON file. 
This JSON file can then be used 
to create the same project on another DSP server. 

```bash
dsp-tools get [options] project_definition.json
```

The following options are available:

- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-u` | `--user` (optional, default: `root@example.com`): username (e-mail) used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
- `-P` | `--project` (mandatory): shortcode, shortname or IRI of the project 
- `-v` | `--verbose` (optional): print more information about the progress to the console
- `--suppress-update-prompt` (optional): don't prompt when using an outdated version of DSP-TOOLS 
  (useful for contexts without interactive shell, e.g. when the Terminal output is piped into a file)

The defaults are intended for local testing: 

```bash
dsp-tools get -P my_project project_definition.json
```

will get `my_project` from `localhost`.

In order to get a project from the DSP server `https://app.dasch.swiss`,
it is necessary to specify the following options:

```bash
dsp-tools get -s https://api.dasch.swiss -u 'your@email.com' -p 'password' -P my_project project_definition.json
```

It is possible to get a project from a DSP server without giving credentials.
But in this case, the resulting JSON file won't have a "users" section.

The expected JSON format is [documented here](./json-project/overview.md).
