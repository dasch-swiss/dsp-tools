[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Enhanced Mass-Upload

For projects with a big number of multimedia files, 
the [`xmlupload`](../cli-commands.md#xmlupload) command is too slow.
That's why we developed, for internal usage, an enhanced workflow. 
It consists of the steps described in this document:

1. prepare your data as explained below
2. start a local DSP stack
3. use the `enhanced-xmlupload` command 

The enhanced xmlupload uses multithreading 
to preprocess the multimedia files with the local DSP stack 
and to upload the preprocessed files to the server (local or remote).
Then, it creates the resources of the XML file on the DSP server.



## 1. Prepare your data

The following data structure is expected:

```text
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

A folder with the above structure can be created with

```bash
dsp-tools enhanced-xmlupload --generate-test-data --size=small/medium/big data.xml
```


## 2. Assign CPUs to Docker and start DSP stack

- If not already available, make a clone of the [DSP-API repository](https://github.com/dasch-swiss/dsp-api).
- In Docker > Settings > Resources, assign as many CPUs as you afford to Docker. Not all, because some CPUs should remain for the OS.
- In `dsp-api/sipi/config/sipi.docker-config.lua`, set nthreads to a number slightly lesser than the number of CPUs assigned to Docker.
  - `--num-of-threads-for-preprocessing` (see below) will be dependent on the number of CPUs assigned to Docker and the number of threads of SIPI (???)
- On the main branch, execute `make init-db-test-minimal` and then `make stack-up`.


## 3. `enhanced-xmlupload`

The command `enhanced-xmlupload` must be called from the project root.

```bash
dsp-tools enhanced-xmlupload [options] xmlfile
```

### Arguments and options

To generate test data:

- `--generate-test-data`: If set, only generate a test data folder in the current working directory (no upload).
  - `--size`: size of test data set: small/medium/big

For the actual command:

- `--local-sipi-server` (optional, default: `http://0.0.0.0:1024`): URL of the local SIPI IIIF server
- `--sipi-processed-path`: Path to folder containing the processed multimedia files. This must be the `sipi/images/processed` folder of your local clone of DSP-API
- `-s` | `--remote-dsp-server` (optional, default: `http://0.0.0.0:3333`): URL of the DSP server where your data should be uploaded to, e.g. `https://api.dasch.swiss`
- `-S` | `--remote-sipi-server` (optional, default: `http://0.0.0.0:1024`): URL of the remote SIPI IIIF server, e.g. `https://iiif.dasch.swiss`
- `-t` | `--num-of-threads-for-preprocessing` (optional, default: 32): number of threads used for sending requests to the local SIPI 
  - depends on the number of CPUs assigned to Docker and the number of threads of SIPI (see above)
  - must be fine-tuned and optimized on every individual machine
- `-T` | `--num-of-threads-for-uploading` (optional, default: 8): number of threads used for uploading the preprocessed files to the remote SIPI
  - depends on the number of cores available on the remote server
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API
- `-I` | `--incremental` (optional) : If set, IRIs instead of internal IDs are expected as reference to already existing resources on DSP
- `-v` | `--verbose` (optional): If set, more information about the process is printed to the console.
- `xmlfile` (required): path to XML file containing the data

This command makes the preprocessing, sends the preprocessed files to the server, and creates the resources of the XML file.
