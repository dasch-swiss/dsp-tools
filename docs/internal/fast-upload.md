[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Fast Mass-Upload

For projects with a lot of files, 
the [`xmlupload`](../cli-commands.md#xmlupload) command is too slow.
That's why we developed, for internal usage, a specific workflow for fast mass uploads.
The fast mass upload workflow processes the files locally before uploading them to the DSP server.
Then, it creates the resources of the XML file on the DSP server.

In order for the fast mass upload to work, you need the following dependencies:

- Your machine must be able to run the DSP software stack. 
  The (internal) document "Installation of your Mac" explains what software needs to be installed.
- Get the latest Sipi image from [docker hub](https://hub.docker.com/r/daschswiss/sipi). 
  If you have run DSP-API recently, the Sipi image should be already on your machine. 
  You can check it in Docker Desktop > Images.
- Install ffmpeg, e.g. with `brew install ffmpeg`
- Install ImageMagick, e.g. with `brew install imagemagick`

The fast mass upload consists of the following steps:

1. Prepare your data as explained below
2. Process the files locally with `dsp-tools process-files`
3. Upload the files to DSP with `dsp-tools upload-files`
4. Create the resources on DSP with `dsp-tools fast-xml-upload`


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


## 2. `dsp-tools process-files`

Process the files locally, using a SIPI container.

```bash
dsp-tools process-files --input-dir=multimedia --out-dir=tmp data.xml 
```

The following options are available:

- `--input-dir` (mandatory): path to the input directory where the files should be read from 
- `--out-dir` (mandatory): path to the output directory where the processed/transformed files should be written to
- `--sipi-image` (optional, default: `daschswiss/sipi:3.8.1`): the latest Sipi image from [docker hub](https://hub.docker.com/r/daschswiss/sipi)

All files referenced in the <bitstream> tags of the XML 
are expected to be in the input directory 
which is provided with the `--input-dir` option.
The processed files 
(derivative, .orig file, sidecar file, as well as the key frames for movies) 
will be stored in the given `--out-dir` directory.
If the output directory doesn't exist, it will be created automatically.
Additionally to the output directory,
a pickle file is written with the name `processing_result_[timestamp].pkl`.
It contains the mapping between the original file and the processed files,
e.g. "multimedia/dog.jpg" -> "tmp/0b22570d-515f-4c3d-a6af-e42b458e7b2b.jp2".


## 3. `dsp-tools upload-files`

After all files are processed, the upload step can be started.


```bash
dsp-tools upload-files --pkl-file=processing_result_20230414_152810.pkl --processed-dir=tmp
```

The following options are available:

- `-f` | `--pkl-file` (mandatory): path to the pickle file that was written by the processing step
- `-d` | `--processed-dir` (mandatory): path to the directory where the processed files are located (same as `--out-dir` in the processing step)
- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-S` | `--sipi-url` (optional, default: `0.0.0.0:1024`): URL of the SIPI server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 


## 4. `dsp-tools fast-xml-upload`

```bash
dsp-tools fast-xml-upload --pkl-file=processing_result_20230414_152810.pkl data.xml
```

The following options are available:

- `-f` | `--pkl-file` (mandatory): path to the pickle file that was written by the processing step
- `-s` | `--server` (optional, default: `0.0.0.0:3333`): URL of the DSP server 
- `-S` | `--sipi-url` (optional, default: `0.0.0.0:1024`): URL of the SIPI server 
- `-u` | `--user` (optional, default: `root@example.com`): username used for authentication with the DSP-API 
- `-p` | `--password` (optional, default: `test`): password used for authentication with the DSP-API 
