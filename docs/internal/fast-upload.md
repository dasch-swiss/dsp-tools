[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Mass-Upload

For projects with a lot of files, 
the [`xmlupload`](../cli-commands.md#xmlupload) command is too slow.
That's why we developed, for internal usage, a specific workflow for mass uploads. 
It consists of the steps described in this document:

1. create the XLM file as usual
2. prepare one root directory with the files that are referenced in the XML file
3. get the latest Sipi image from [docker hub](https://hub.docker.com/r/daschswiss/sipi)
    - if you have run DSP-API recently, the Sipi image should be already on your machine. You can check it in Docker Desktop > Images
    - your machine must have the DSP software installed, as described in the (internal) document "Installation of your Mac"
4. make sure that you have ffmpeg installed (`brew install ffmpeg`)
5. make sure that you have ImageMagick installed (`brew install imagemagick`)
6. process the files locally with `dsp-tools process-files`
7. upload the files to DSP with `dsp-tools upload-files`
8. create the resources on DSP with `dsp-tools fast-xml-upload`

The mass upload workflow processes the files locally before uploading them to the DSP server.
Then, it creates the resources of the XML file on the DSP server.

## 1. dsp-tools process-files

```bash
dsp-tools process-files --input-dir=/path/to/root/directory/of/files --out-dir=/path/to/output/directory /path/to/xml/file/data.xml 
```

All files referenced in the <bitstream> tag of the XML are expected to be in the root directory which is provided with the --input-dir option.
The processed files (derivative, .orig file and sidecar file as well as the key frames for movies) will be stored in the
given --out-dir directory.
If the directory doesn't exist, it will be created automatically.

## 2. dsp-tools upload-files

```bash
dsp-tools upload-files --paths-file=file_processing_result_20230414_152810.pkl --processed-dir=/path/to/output/directory --sipi-url=http://localhost:1024 --dsp-url=http://0.0.0.0:3333 --user=root@example.com --password=test
```

After all files are processed,
the upload step can be started.
The processing step writes the result into a pickle file called `file_processing_result_[timestamp].pkl`.
The user has to provide the path to this file with the option `--paths-file`.
The `--processed-dir` option specifies the location of the files that should be uploaded.
It is most likely the same as the directory defined in the step before with `--out-dir`.
To upload the files, the user has to provide the URL to the Sipi server as well as the URL to DSP with the credentials
(e-mail and password).


## 3. dsp-tools fast-xml-upload

```bash
dsp-tools fast-xml-upload ...
```
