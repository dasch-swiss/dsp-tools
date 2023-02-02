[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Enhanced Mass-Upload

For projects with a big quantity of multimedia files, 
the `xmlupload` command is too slow.
That's why we developed, for internal usage, an enhanced workflow. 
It consists of two steps:

First, the `preprocess-xmlupload` command 
preprocesses the multimedia files locally (using a local SIPI instance), 
uploads them to the server,
and creates a copy of the XML file in which the `<bitstream>` tags don't contain file paths anymore, 
but a reference to the internal filename on the server.
This first step uses multithreading to speed up the process.

The second step is done with the `xmlupload` command,
using the `--preprocessing-done` flag.
This second step takes much less time than a normal `xmlupload`,
because it only creates the resources, 
and doesn't have to deal with the multimedia files. 

In order to use this enhanced workflow, 
follow the steps described in this document.


## 1. Prepare your data

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
- Your project must not contain a folder named `ZIP` or `tmp` on the top level

A folder with the above structure can be created with

```bash
dsp-tools preprocess-xmlupload --generate-test-data
```



## 2. Start SIPI

Run a modified local instance of SIPI as follows: 

- make a fresh clone of the [DSP-API repository](https://github.com/dasch-swiss/dsp-api)
- do NOT rename it, its name must be "dsp-api"
- execute `make env-file` inside it 
   - (This is only necessary if you have never started a stack from within that repo. It sets some environment variables.)
- in `docker-compose.yml`, comment out the following sections:
   - app
   - db
   - api
- in `docker-compose.yml`, change the `ports` of sipi from "1024:1024" to "1024"
- in `docker-compose.yml`, add your project folder to the `sipi/volumes` list, in the form: `full/path:abbreviation:delegated`
- in `sipi/config/sipi.docker-config.lua`, change `imgroot` from '/sipi/images' to the abbreviation of your project folder 
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



## 3. Preprocess and upload the multimedia files with `preprocess-xmlupload`

The command `preprocess-xmlupload` must be called from the project root.

```bash
dsp-tools preprocess-xmlupload --xmlfile=data.xml --multimedia_folder=multimedia --sipi_port=12345
```

Arguments and options:

 - `--xmlfile` (optional, default: `data.xml`): path to xml file containing the data
 - `--multimedia_folder` (optional, default: `multimedia`): name of the folder containing the multimedia files
 - `--sipi_port` (mandatory): 5-digit port number that SIPI uses, can be found in the "Container" view of Docker Desktop

This command makes the preprocessing and sends the preprocessed files to the server.
The output is an XML file 
where all file paths inside the `<bitstream>` tags are replaced by the internal filename used on the server.



## 4. Create the resources with `xmlupload --preprocessing-done`

As last step, do

```bash
dsp-tools xmlupload data-preprocessed.xml --preprocessing-done
```

You can use the [usual flags](../cli-commands.md#xmlupload) that are available for this command, 
except `--sipi`, which is not necessary.
