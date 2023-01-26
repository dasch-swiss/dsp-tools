[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Improved Mass-Upload

## Prepare your data

The following data structure is expected:

```
my_project
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

A folder with the above structure can be created with

```bash
dsp-tools enhanced-xmlupload --generate-test-data
```



## Start SIPI

First, you must start SIPI: 

- make a fresh clone of the [DSP-API repository](https://github.com/dasch-swiss/dsp-api)
- rename it to "dsp-api-sipi-only"
- execute `make env-file` inside it 
   - (This is only necessary if you have never started a stack from within that repo. It sets some environment variables.)
- in `docker-compose.yml`, comment out the following sections:
   - app
   - db
   - api
- in `docker-compose.yml`, change the `ports` of sipi from "1024:1024" to "1024"
- in `sipi/config/sipi.docker-config.lua`, change `nthreads` from 8 to 32
- in `sipi/scripts/upload.lua`, comment out the following section:
  ```lua
  -- Check for a valid JSON Web Token from Knora.
    local token = get_knora_token()
    if token == nil then
        return
    end
  ```
- finally, execute `docker compose up --scale sipi=1`
- find the 5-digit port number that SIPI uses, in the "Container" view of Docker Desktop



## Call to `enhanced-xmlupload`

The command `enhanced-xmlupload` must be called from the project root.

```bash
dsp-tools enhanced-xmlupload data.xml --multimedia_folder=multimedia --sipi_port=12345
```

Arguments and options:

 - data file (optional, default: `data.xml`): path to xml file containing the data
 - `--multimedia_folder` (optional, default: `multimedia`): name of the folder containing the multimedia files
 - `--sipi_port` (mandatory): 5-digit port number that SIPI uses, can be fouind in the "Container" view of Docker Desktop
