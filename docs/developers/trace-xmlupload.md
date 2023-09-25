# Trace xmlupload

## Preparation

Update the dependencies in the virtual environment with `poetry install`.
Create the data model with `dsp-tools create testdata/json-project/test-project-systematic.json`.

```bash
viztracer src/dsp_tools/cli.py xmlupload testdata/xml-data/test-data-systematic.xml
```
