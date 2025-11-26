# Update Legal Info In XML

## Context

If an XML file contains multimedia files, they must be accompanied by legal metadata
in this format: 

```xml
<bitstream 
    license="http://rdfh.ch/licenses/cc-by-4.0" 
    copyright-holder="Louvre" 
    authorship-id="auth_0">
```

Older XML files may contain legal metadata as text properties. 
This document guides you through the process of updating them to the new format.


## Step 1: Find Out The Property Names And Run The Command

Every XML file uses different property names. 
Therefore, there cannot be an automatism in DSP-TOOLS to treat all XML files equally.
Rather, you have to call the command with the right flags.
Let's consider this example:

```xml
<knora>
    <resource label="lbl" restype=":type" id="res_1">
        <bitstream>testdata/bitstreams/test.jpg</bitstream>
        <text-prop name=":hasAuthor"><text encoding="utf8">M. Chuzeville</text></text-prop>
        <text-prop name=":hasCopyright"><text encoding="utf8">Louvre</text></text-prop>
        <text-prop name=":hasLicense"><text encoding="utf8">CC BY</text></text-prop>
    </resource>
</knora>
```

In this case, you need to run the command like this:

```bash
dsp-tools update-legal \
--authorship_prop=":hasAuthor" \
--copyright_prop=":hasCopyright" \
--license_prop=":hasLicense" \
data.xml
```

The output will be written to `data_updated.xml`:

```xml
<knora>
    <authorship id="authorship_0">
        <author>M. Chuzeville</author>
    </authorship>

    <resource label="lbl" restype=":type" id="res_1">
        <bitstream 
            license="http://rdfh.ch/licenses/cc-by-4.0" 
            copyright-holder="Louvre" 
            authorship-id="authorship_0"
        >
            testdata/bitstreams/test.jpg
        </bitstream>
    </resource>
</knora>
```

In case that the properties are present for some resources, but missing for others,
you would get a lot of repetitive errors.
To prevent this, you can provide default values that will be filled in if a property is missing.
Run the command with the following flags:

```bash
dsp-tools update-legal \
--authorship_prop=":hasAuthor" \
--authorship_default="Project Member" \
--copyright_prop=":hasCopyright" \
--copyright_default="University of Basel" \
--license_prop=":hasLicense" \
--license_default="CC BY SA" \
data.xml
```


### Automatically Treating Invalid Licenses as "Unknown"

If your XML file contains many resources with invalid licenses (licenses that cannot be parsed),
you can use the `--treat_invalid_license_as_unknown` flag to automatically convert them to `unknown`
instead of generating FIXME entries:

```bash
dsp-tools update-legal \
--authorship_prop=":hasAuthor" \
--copyright_prop=":hasCopyright" \
--license_prop=":hasLicense" \
--treat_invalid_license_as_unknown \
data.xml
```

When this flag is used:

- Invalid licenses are automatically replaced with `unknown`
- The final summary shows how many invalid licenses were replaced
- Resources with **multiple licenses** still generate FIXME entries (they require manual selection)
- CSV corrections (via `--fixed_errors`) always take priority over automatic conversion

This is useful when you have many resources with text like "Courtesy of Museum X" or
"Mit freundlicher Genehmigung" that should all be marked as `unknown`.


## Step 2: Fix The Update Errors in The CSV Error File

For each multimedia resource, one or more of these errors may occur:

1. copyright absent
2. authorship absent
3. license absent
4. license not parseable
    - If license information is present, 
      an attempt is made to parse it using [`xmllib.find_license_in_string()`](
      https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/general-functions/#xmllib.general_functions.find_license_in_string)

If there were errors, you will get 2 output files:

- `<input_file>_PARTIALLY_updated.xml`
- `<input_file>_legal_errors.csv`: lists the problematic resources

Please go through the CSV and fix the errors directly in the CSV.


### 1. Problem: Copyright Absent or Multiple Copyrights

CSV Output:

| file    | resource_id | license | copyright                                                 | authorship_1  | authorship_2    |
| ------- | ----------- | ------- | --------------------------------------------------------- | ------------- | --------------- |
| dog.jpg | res_1       | CC BY   | FIXME: Copyright missing                                  | Rita Gautschy | Daniela Subotic |
| cat.jpg | res_2       | CC BY   | FIXME: Multiple licenses found. Choose one: DaSCH, Louvre | Rita Gautschy | Daniela Subotic |

Please add a copyright holder to the CSV:

| file    | resource_id | license | copyright | authorship_1  | authorship_2    |
| ------- | ----------- | ------- | --------- | ------------- | --------------- |
| dog.jpg | res_1       | CC BY   | DaSCH     | Rita Gautschy | Daniela Subotic |
| cat.jpg | res_2       | CC BY   | Louvre    | Rita Gautschy | Daniela Subotic |


### 2. Problem: Authorship Absent

CSV Output:

| file    | resource_id | license | copyright | authorship_1              | authorship_2 |
| ------- | ----------- | ------- | --------- | ------------------------- | ------------ |
| dog.jpg | res_1       | CC BY   | DaSCH     | FIXME: Authorship missing |              |

Please add at least one authorship to the CSV:

| file    | resource_id | license | copyright | authorship_1  | authorship_2 |
| ------- | ----------- | ------- | --------- | ------------- | ------------ |
| dog.jpg | res_1       | CC BY   | DaSCH     | Rita Gautschy |              |


### 3. Problem: License Absent, Not Parseable, or Multiple Licenses Found

CSV Output:

| file     | resource_id | license                                                     | copyright | authorship_1  | authorship_2 |
| -------- | ----------- | ----------------------------------------------------------- | --------- | ------------- | ------------ |
| dog.jpg  | res_1       | FIXME: License missing                                      | DaSCH     | Rita Gautschy |              |
| cat.jpg  | res_2       | FIXME: Invalid license: Courtesy of DaSCH                   | DaSCH     | Rita Gautschy |              |
| bird.jpg | res_3       | FIXME: Multiple licenses found. Choose one: CC-BY, CC-BY-SA | DaSCH     | Rita Gautschy |              |

Please add a valid license to the CSV, either as IRI or in one of the formats understood by 
[`xmllib.find_license_in_string()`](
https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/helpers/#xmllib.helpers.find_license_in_string):

| file     | resource_id | license | copyright | authorship_1  | authorship_2 |
| -------- | ----------- | ------- | --------- | ------------- | ------------ |
| dog.jpg  | res_1       | CC BY   | DaSCH     | Rita Gautschy |              |
| cat.jpg  | res_2       | unknown | DaSCH     | Rita Gautschy |              |
| bird.jpg | res_3       | CC BY   | DaSCH     | Rita Gautschy |              |


#### "Courtesy" Is Not A License

It often happens that the provided license does not fulfill the requirements of a legally valid license.
Examples are "Courtesy of Louvre", or "Mit freundlicher Genehmigung des Louvre".
In this case, you don't really have a license, hence you have to set it to `unknown`.


## Step 3: Rerun The Command

Run the command again, this time with the partially updated XML file and a reference to the fixed errors file:

```bash
dsp-tools update-legal \
--authorship_prop=":hasAuthor" \
--copyright_prop=":hasCopyright" \
--license_prop=":hasLicense" \
--fixed_errors="data_legal_errors.csv" \      # <-- fixed errors file
data_PARTIALLY_updated.xml                    # <-- partially updated XML file
```

If everything is fine, `data_updated.xml` is created.
If some of your corrections in the CSV turn out to be problematic, the following happens:

- `data_PARTIALLY_updated.xml` is updated (overwritten) 
- `data_legal_errors_2.csv` is created

Repeat the steps 2 and 3 until everything is fine.

!!! warning "CSV Values Override Everything"

    When you rerun the command with `--fixed_errors`, the CSV becomes the **single source of truth** for the
    resources listed in it. This means:

    - Any value you change in the CSV (not just FIXME markers) will be used in the final XML
    - This allows you to correct extraction errors, but be careful not to accidentally modify correct values
    - Only resources with errors are included in the CSV; resources not in the CSV are processed normally
