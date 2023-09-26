# Trace xmlupload

## Preparation

- update the dependencies in the virtual environment: `poetry install`
- activate the virtual environment: `poetry shell`
- create the data model: `dsp-tools create testdata/json-project/test-project-systematic.json`
- generate the XML files: `python src/dsp_tools/utils/generate-xmls-for-viztracer.py`

## Run VizTracer

- run `dsp-tools xmlupload viztracer/circles-10.xml`
- run `vizviewer viztracer/viztracer_circles-10.json`
