# Trace xmlupload

## Preparation

- update the dependencies in the virtual environment: `poetry install`
- activate the virtual environment: `poetry shell`
- create the data model: `dsp-tools create testdata/json-project/test-project-systematic.json`
- generate the XML files: `python src/dsp_tools/utils/generate-xmls-for-viztracer.py`
- you will get XML files with 10, 100, 1000, and 10'000 circles

## Run VizTracer

- for every XML file, run `dsp-tools xmlupload viztracer/circles-10.xml`
- for every XML file, run `vizviewer viztracer/viztracer_circles-10.json`

## Preliminary results on Johannes' machine

- When uploading the stashed resptr-props, 
  the performance of stays the same, regardless how many circles there are in the XML file: 
    - ca. 40 ms to get the resource, 
    - and ca. 130 ms to add the stashed link to it.
- But uploading the stashed XML-texts becomes very slow when the XML file has many circles:
  As can be seen in `2023-09-26_13.29.00_viztracer_circles-1000_johannes.json`
  on [Google Drive](https://drive.google.com/file/d/1q7ovGuz_bIWgbCvtIGhmcJ5TiIZYVIlX/view?usp=drive_link),
  for 1000 circles, there is 
    - consistently, ca. 500 ms inactivity between getting the resource and adding the stashed link
    - 1 time, ca. 5 min inactivity between adding one link until adding the next link
    - 1 time, the call to `Connection.put()` takes 10 minutes

Conclusion: The problem lies in the python code of DSP-TOOLS. 
It can be fixed by refactoring the function `_upload_stashed_xml_texts()`.
