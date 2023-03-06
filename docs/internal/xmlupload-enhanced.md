[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Enhanced Mass-Upload

For projects with a big quantity of multimedia files, 
the `xmlupload` command is too slow.
That's why we developed, for internal usage, an enhanced workflow. 
It consists of the steps described in this document:

First, prepare your data as explained below.
Then, startup a local SIPI instance.
Finally, use the `enhanced-xmlupload` command 
to preprocess the multimedia files locally, 
upload them to the server,
and create the resources of the XML file on the DSP server.
This first step uses multithreading to speed up the process.



## 1. Prepare your data

The following data structure is expected:

```
my_project
├── data_model.json
├── data.xml   (<bitstream>multimedia/dog.jpg</bitstream>)
└── multimedia
    ├── dog.jpg
    ├── cat.mp3
    └── subfolder
        ├── snake.pdf
        └── bird.mp4
```

Note:

- Your project must contain one XML data file, anywhere.
- Your project must contain one sub-folder that contains all multimedia files (here: `multimedia`).
- The multimedia files in `multimedia` may be arbitrarily nested.
- Every multimedia file in `multimedia` must occur in the XML data file.
- Every path referenced in a `<bitstream>` in the XML file must point to a file in `multimedia`.
- The paths in the `<bitstream>` are relative to the project root.
- Your project must not contain a folder named `ZIP` or `tmp` on the top level

A folder with the above structure can be created with

```bash
dsp-tools enhanced-xmlupload --generate-test-data --size=small/medium/big data.xml
```


## 2. Start SIPI

Run a modified local instance of SIPI as follows: 

Method 1: Start with a fresh clone:

- make a fresh clone of the [DSP-API repository](https://github.com/dasch-swiss/dsp-api)
- optional: rename the repository
- execute `make env-file` inside it (this sets some environment variables)
   - after setting the environment variables, or after executing a `make stack-up` in the DSP-API repository, 
     every change of the repository's name must be updated in the `LOCAL_HOME` variable in the `.env` file
- continue with the common steps below

Method 2: Reuse an old clone:

- you have executed `make stack-up` before, so the `.env` file exists
- if you rename the repository, update `LOCAL_HOME` in the `.env` file
- continue with the common steps below

Common steps for methods 1 + 2:

- in `docker-compose.yml`, comment out the following sections:
  - app
  - db
  - api
- in `docker-compose.yml`, change `sipi/ports` from 1024:1024 to 1023
- in `docker-compose.yml`, change `sipi/environment/SIPI_EXTERNAL_PORT` from 1024 to 1023
- in `docker-compose.yml`, add the following line to the `sipi/volumes` list: `~/.dsp-tools:/dsp-tools-home-folder:delegated`
- in `docker-compose.yml`, change `sipi/networks` from `knora-net` to `knora-net-local`
- in `docker-compose.yml`, change `networks/knora-net/name: knora-net` to `networkds/knora-net-local/name: knora-net-local`
- in `sipi/config/sipi.docker-config.lua`, change `sipi/port` from 1024 to 1023
- in `sipi/config/sipi.docker-config.lua`, change `sipi/nthreads` from 8 to 32
- in `sipi/config/sipi.docker-config.lua`, change `sipi/imgroot` from `/sipi/images` to `/dsp-tools-home-folder`
- in `sipi/scripts/upload.lua`, comment out the following section:
  ```lua
  -- Check for a valid JSON Web Token from Knora.
    local token = get_knora_token()
    if token == nil then
        return
    end
  ```
- finally, execute `docker compose -p local-sipi up --scale sipi=1`
- find the 5-digit port number that SIPI uses, in the "Container" view of Docker Desktop



## 3. `enhanced-xmlupload`

The command `enhanced-xmlupload` must be called from the project root.

```bash
dsp-tools enhanced-xmlupload [options] xmlfile
```

Arguments and options:

- `--multimedia-folder` (optional, default: `multimedia`): name of the folder containing the multimedia files
- `--local-sipi-port` (required): 5-digit port number of the local SIPI instance, can be found in the "Container" view of Docker Desktop
- `--generate-test-data`: If set, only generate a test data folder in the current working directory (no upload).
  - `--size`: size of test data set: small/medium/big
- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `-S` | `--remote-sipi-server` (optional, default: `http://0.0.0.0:1024`): URL of the remote SIPI IIIF server
- `-I` | `--incremental` (optional) : If set, IRIs instead of internal IDs are expected as reference to already existing resources on DSP
- `-v` | `--verbose` (optional): If set, more information about the process is printed to the console.
- `xmlfile` (required): path to XML file containing the data

This command makes the preprocessing, sends the preprocessed files to the server, and creates the resources of the XML file.
