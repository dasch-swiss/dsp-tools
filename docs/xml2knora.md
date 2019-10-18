[![PyPI version](https://badge.fury.io/py/knora.svg)](https://badge.fury.io/py/knora)

# knora-xml-import

Use `knora-xml-import` for importing data from an XML-file into knora.

## Usage:

```bash
$ knora-xml-import project-show-name
```
It supports the following options:

- _"-s server" | "--server server"_: The URl of the Knora server [default: http://0.0.0.0:3333]
- _"-S sipi-server" | "--sipi sipi-server"_: The URL of the SIPI IIIF server [default: http://0.0.0.0:1024]
- _"-u username" | "--user username"_: Username to log into Knora [default: root@example.com]
- _"-p password" | "--password password"_: The password for login to the Knora server [default: test]
- _"-F folder" | "--folder folder"_: Folder containing the XML-file with the data and the images [default: `project-short-name`.dir]

## Data folder
The data folder contains the
- the XML file that has the same name as the project with the extension `.xml`
- an optional directory called `assets` that contains icons etc.
- a directory called `images` containing the images for StillImageResources
- may contain the project ontology definition as JSON file

## Knora import XML format

### Preample
The import file must start with the standard XML header:
```xml
<?xml version='1.0' encoding='utf-8'?>
```

### `knora`-tag
The `knora`-tag describes a set of resources that are to be imported. It is the
container for an arbitrary number of `resource` tags and may only
contain resource tags.
The `knora`-tag defines has the following options:
- _xmlns:xsi_: `"http://www.w3.org/2001/XMLSchema-instance"` [required]
- _xsi:schemaLocation_: Path to knora XML schema file for validation [optional]
- _shortcode_: Knora project shortcode, e.g. "0801" [required]
- _vocabulary_: Name of the ontology [required]
Thus, the knora-tag may b used as follows:
```xml
<knora
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="../knora-data-schema.xsd"
 shortcode="0806"
 vocabulary="webern">
…
</knora>

```

### `resource`-tag
A `resource`-tag contains all necessary information to create a resource. It
has th following options:
- _label_: The label, a human readable, semantical meaningfull short name of the resource [required]
- _restype_: The resource type as defined within the ontology [required]
- _unique_id_: A unique, arbitrary string giving a unique ID to the resource. This ID is only used during the
import process for referencing this resource from other resources. During the import process, it will be replaced by
the IRI used internally by Knora.

````
<resource label="EURUS015a" restype="Postcard" unique_id="238807">
…
</resource>
````

The resource-tag may contain the following tags describing properties (data fields):
- _\<image\>_: In case of the StillImageResource contains the path to the image file.
- _\<text-prop\>_: Contains text values
- _\<color-prop\>_: Contains color values
- _\<date-prop\>_: Contains date values
- _\<float-prop\>_: Contains decimal values
- _\<geometry-prop\>_: Contains a JSON geometry definition for a region
- _\<geoname-prop\>_: Contains a geoname.org location code
- _\<list-prop\>_: Contains list tag labels
- _\<iconclass-prop\>_: Contains iconclass.org codes
- _\<integer-prop\>_: Contains integer values
- _\<interval-prop\>_: Contains interval values
- _\<period-prop\>_: Contains time period values
- _\<resptr-prop\>_: Contains links othr resources
- _\<time-prop\>_: Contains time values
- _\<uri-prop\>_: Contains URI values
- _\<boolean-prop\>_: Contaibs boolean values

## Properties and values

### `\<image\>`-tag
The image property contains the path to an image file. It must only be used if the
resource is a `StillImageResource`!

_Note_: There is only _one_ \<image\> tag allowed per StillImageResource!

Example:
```xml
<image>postcards.dir/images/EURUS015a.jpg</image>
```

### `\<text-prop\>`-tag
The text property tag is used to list text values. It has one mandatory options:
- _name_: Name of the property as given in the ontology

Example:
```xml
<text-prop name="hasTranslation">
```
The `\<text-prop\>`-tag must contain at least one `\<text\>`-tag. There are several variants of text tags:

#### `\<text\>`-tag
The `\<text\>`-tag has the following options:
- _encoding_: either "utf8" or "hex64" [required]
  - _utf8_: The tag describes a simple text without markup. The text is a simple utf-8 string
  - _hex64_: The tag describes a complex text containing markup. It must be a hex64 encoded string in the
  XML-format as defined by Knora.
- _resrefs_: A list of resource ID's that are referenced in the markup, separated by the "|"-character such as `"2569981|6618"` [optional]

Knora-xml-import assumes that standard mapping for Knora is being used (Custom mapping to
customized standoff tags is not yet implemented!)

E.g. a text containing a link to another resource must be encoded like follows:
```xml
'Brief: <a class="salsah-link" href="IRI:6618:IRI"><p>Webern an Willheim, 10.10.1928</p></a>'
```
Please note that the href-option withiin the anchor tag points to an internal resource of knora
and this has to have the special format "`IRI:`res-id`:IRI`" where res-id is the resource
id defined within the XML import file. At the moment it is not yet possible to reference
already existing resources using the Knora-IRI (will b implemented soon).

In case the string references one or more internal resources, the option `rsrefs`_must_ be using to
indicate there ID's! The string must be encoded using standard hex64 encoding.

A complete example for a simple text:
```xml
<text-prop name="hasComment">
   <text encoding="utf8">Probe bei "Wimberger". Lokal in Wien?</text>
</text-prop>
```
A complete example of a complex text which encodes the text `<a class="salsah-link" href="IRI:6618:IRI"><p>Webern an Willheim, 10.10.1928</p></a><p></p>` containing
a link to the internal resource with the ID="6618":
```xml
<text-prop name="hasComment">
      <text resrefs="6618" encoding="hex64">PGEgY2xhc3M9InNhbHNhaC1saW5rIiBocmVmPSJJUkk6NjYxODpJUkkiPjxwPldlYmVybiBhbiBXaWxsaGVpbSwgMTAuMTAuMTkyODwvcD48L2E+PHA+PC9wPg==</text>
</text-prop>
```
Within one property, simple and complex text values may be mixed.

### `\<color-prop\>`-tag
The color-prop tag is used to define a color property. It has one mandatory options:
- _name_: Name of the property as given in the ontology

#### `\<color\>`-tag
The color-tag is used to indicate a color value. The color has to be giiven in
web-notation, that is a "#" followed by 3 or 6 hex numerals.

A propery with 2 color valus would be defined as follows:
```xml
<color-prop name="hasColor">
    <color>#00ff66</color>
    <color>#ff00ff</color>
</color-prop>
```

### `\<date-prop\>`-tag
Is used to define knora dates. Options:
- _name_: Name of the property as given in the ontology

#### `\<date\>`-tag
A Knora date value. It has the following format:
```
calendar:epoch:yyyy-mm-dd:epoch:yyyy-mm-dd
```
- _calendar_: either "JULIAN" or "GREGORIAN" [optional, default: GREGORIAN]
- _epoch_: either "BCE" or "CE" [optional, default CE]
- _yyyy_: year with four digits (at least one must be given)
- _mm_: month with two digits 01, 02, .., 12
- _dd_: day eith two digits

If two dates are given, the date is in between the two given borders.

