[![DSP-TOOLS](https://img.shields.io/github/v/release/dasch-swiss/dsp-tools?include_prereleases&label=DSP-TOOLS)](https://github.com/dasch-swiss/dsp-tools)

# XML data from Excel files

The Excel file must be structured as in this image:  
![img-excel2xml.png](assets/images/img-excel2xml.png)

Some notes:

 - The special tags `<annotation>`, `<link>`, and `<region>` are represented as resources of restype `Annotation`, 
`LinkObj`, and `Region`. 
 - The columns "ark", "iri", and "creation_date" are only used for DaSCH-internal data migration.
 - If `file` is provided, but no `file permissions`, an attempt will be started to deduce them from the resource 
   permissions (`res-default` --> `prop-default` and `res-restricted` --> `prop-restricted`). If this attempt is not 
   successful, a `BaseError` will be raised.