
If license information is present, an attempt is made to parse it using [`xmllib.find_license_in_string()`](
https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/helpers/#xmllib.helpers.find_license_in_string). 
If none is recognized, [`LicenseRecommended.DSP.UNKNOWN`](
https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/licenses/recommended/#xmllib.models.licenses.recommended.DSP)
is used.

**Example:**

```bash
dsp-tools update-legal \
--authorship_prop=":hasAuthorship" \
--copyright_prop=":hasCopyright" \
--license_prop=":hasLicense" \
input.xml
```

Input:

```xml
<knora>
    <resource label="lbl" restype=":type" id="res_1">
        <bitstream>testdata/bitstreams/test.jpg</bitstream>
        <text-prop name=":hasAuthorship"><text encoding="utf8">Maurice Chuzeville</text></text-prop>
        <text-prop name=":hasCopyright"><text encoding="utf8">© Louvre</text></text-prop>
        <text-prop name=":hasLicense"><text encoding="utf8">CC BY</text></text-prop>
    </resource>
</knora>
```

Output:

```xml
<knora>
    <authorship id="authorship_0">
        <author>Maurice Chuzeville</author>
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
