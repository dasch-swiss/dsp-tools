# Update legal info in XML

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

## Step 1: Find out the flags to run `update-legal`

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

In this case, you need to call the command like this:

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
            copyright-holder="© Louvre" 
            authorship-id="authorship_0"
        >
            testdata/bitstreams/test.jpg
        </bitstream>
    </resource>
</knora>
```

## Step 2: Fix the update errors in the CSV error file

For each multimedia resource, one or more of these errors may occur:

1. copyright absent
2. authorship absent
3. license absent
4. license not parseable
    - If license information is present, 
      an attempt is made to parse it using [`xmllib.find_license_in_string()`](
      https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/helpers/#xmllib.helpers.find_license_in_string).

If there were errors, no output XML is written.
Instead, you get the file `legal_errors.csv` that lists all problematic resources.
Please go through the CSV and fix the errors directly in the CSV.

### 1. Copyright absent

CSV Output:

| file    | resource_id | license                           | copyright | authorship_1  | authorship_2    |
| ------- | ----------- | --------------------------------- | --------- | ------------- | --------------- |
| dog.jpg | res_1       | http://rdfh.ch/licenses/cc-by-4.0 |           | Rita Gautschy | Daniela Subotic |

Please add a copyright holder to the CSV:

| file    | resource_id | license                           | copyright | authorship_1  | authorship_2    |
| ------- | ----------- | --------------------------------- | --------- | ------------- | --------------- |
| dog.jpg | res_1       | http://rdfh.ch/licenses/cc-by-4.0 | DaSCH     | Rita Gautschy | Daniela Subotic |

### 2. Authorship absent

CSV Output:

| file    | resource_id | license                           | copyright | authorship_1 | authorship_2 |
| ------- | ----------- | --------------------------------- | --------- | ------------ | ------------ |
| dog.jpg | res_1       | http://rdfh.ch/licenses/cc-by-4.0 | DaSCH     |              |              |

Please add at least one authorship to the CSV:

| file    | resource_id | license                           | copyright | authorship_1  | authorship_2 |
| ------- | ----------- | --------------------------------- | --------- | ------------- | ------------ |
| dog.jpg | res_1       | http://rdfh.ch/licenses/cc-by-4.0 | DaSCH     | Rita Gautschy |              |

### 3. License absent

CSV Output:

| file    | resource_id | license | copyright | authorship_1  | authorship_2 |
| ------- | ----------- | ------- | --------- | ------------- | ------------ |
| dog.jpg | res_1       |         | DaSCH     | Rita Gautschy |              |

Please add a valid license to the CSV, either as IRI or in one of the formats understood by 
[`xmllib.find_license_in_string()`](
https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/helpers/#xmllib.helpers.find_license_in_string):

| file    | resource_id | license | copyright | authorship_1  | authorship_2 |
| ------- | ----------- | ------- | --------- | ------------- | ------------ |
| dog.jpg | res_1       | CC BY   | DaSCH     | Rita Gautschy |              |

### 4. License not parseable

CSV Output:

| file    | resource_id | license           | copyright | authorship_1  | authorship_2 |
| ------- | ----------- | ----------------- | --------- | ------------- | ------------ |
| dog.jpg | res_1       | Courtesy of DaSCH | DaSCH     | Rita Gautschy |              |

Please add a valid license to the CSV, either as IRI or in one of the formats understood by 
[`xmllib.find_license_in_string()`](
https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/helpers/#xmllib.helpers.find_license_in_string):

| file    | resource_id | license | copyright | authorship_1  | authorship_2 |
| ------- | ----------- | ------- | --------- | ------------- | ------------ |
| dog.jpg | res_1       | unknown | DaSCH     | Rita Gautschy |              |


#### "Courtesy" is not a license

It often happens that the provided license does not fulfill the requirements of a legally valid license.
Examples are "Courtesy of Louvre", or "Mit freundlicher Genehmigung des Louvre".
In this case, you don't really have a license, hence you have to set it to `unknown`.

## Step 3: Rerun the command

Run the command again, this time with a reference to the fixed errors file:

```bash
dsp-tools update-legal \
--authorship_prop=":hasAuthor" \
--copyright_prop=":hasCopyright" \
--license_prop=":hasLicense" \
--fixed_errors="legal_errors.csv" \
data.xml
```

If everything is fine, `data_updated.xml` is created.
If not, a new version of `legal_errors.csv` is created.
Repeat the steps 2 and 3 until everything is fine.
