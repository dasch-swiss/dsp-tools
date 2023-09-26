# Trace xmlupload

## Preparation

Update the dependencies in the virtual environment with `poetry install`.
Create the data model with `dsp-tools create testdata/json-project/test-project-systematic.json`.

```bash
for number in 10 100 1000 10000:
    viztracer --output_file=viztracer_$number.json -- src/dsp_tools/cli.py xmlupload circles-$number.xml
```
