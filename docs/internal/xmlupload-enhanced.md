[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Enhanced Mass-Upload

For projects with a big quantity of multimedia files, 
the `xmlupload` command is too slow.
That's why we developed, for internal usage, an enhanced workflow. 
It consists of the steps described in this document:

First, prepare your data as explained below.
Then, startup a local DSP stack.
Finally, use the `enhanced-xmlupload` command 
to preprocess the multimedia files locally, 
upload them to the server (local or remote),
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
- Every path referenced in a `<bitstream>` in the XML file must point to a file in `multimedia`.
- The paths in the `<bitstream>` are relative to the project root.
- Your project must not contain a folder named `ZIP` or `tmp` on the top level

A folder with the above structure can be created with

```bash
dsp-tools enhanced-xmlupload --generate-test-data --size=small/medium/big data.xml
```


## 2. Start DSP stack

- if not already available, make a clone of the [DSP-API repository](https://github.com/dasch-swiss/dsp-api)
- `make init-db-test`
- `make stack-up`

Method 2: Reuse an old clone:

- you have executed `make stack-up` before, so the `.env` file exists
- if you rename the repository, update `LOCAL_HOME` in the `.env` file
- continue with the common steps below

## 3. `enhanced-xmlupload`

The command `enhanced-xmlupload` must be called from the project root.

```bash
dsp-tools enhanced-xmlupload [options] xmlfile
```

Arguments and options:

- `--generate-test-data`: If set, only generate a test data folder in the current working directory (no upload).
  - `--size`: size of test data set: small/medium/big
- `--local-sipi-server` (optional, default: `http://0.0.0.0:1024`): URL of the local SIPI IIIF server
- `--sipi-processed-path`: Path to folder containing the processed multimedia files
- `-s` | `--remote-dsp-server` (optional, default: `http://0.0.0.0:3333`): URL of the DSP server
- `-S` | `--remote-sipi-server` (optional, default: `http://0.0.0.0:1024`): URL of the remote SIPI IIIF server (for testing purposes, can be the same as `--local-sipi-server`)
- `-t` | `--num-of-threads-for-preprocessing` (optional, default: 32): number of threads used for sending requests to the local SIPI
- `-T` | `--num-of-threads-for-uploading` (optional, default: 8): number of threads used for uploading the preprocessed files to the remote SIPI
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `-I` | `--incremental` (optional) : If set, IRIs instead of internal IDs are expected as reference to already existing resources on DSP
- `-v` | `--verbose` (optional): If set, more information about the process is printed to the console.
- `xmlfile` (required): path to XML file containing the data

This command makes the preprocessing, sends the preprocessed files to the server, and creates the resources of the XML file.
