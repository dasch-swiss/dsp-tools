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

### `<knora>`-tag
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

### `<resource>`-tag
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
- _<image>_: In case of the StillImageResource contains the path to the image file.
- _<text-prop>_: Contains text values
- _<color-prop>_: Contains color values
- _<date-prop>_: Contains date values
- _<float-prop>_: Contains decimal values
- _<geometry-prop>_: Contains a JSON geometry definition for a region
- _<geoname-prop>_: Contains a geoname.org location code
- _<list-prop>_: Contains list tag labels
- _<iconclass-prop>_: Contains iconclass.org codes
- _<integer-prop>_: Contains integer values
- _<interval-prop>_: Contains interval values
- _<period-prop>_: Contains time period values
- _<resptr-prop>_: Contains links othr resources
- _<time-prop>_: Contains time values
- _<uri-prop>_: Contains URI values
- _<boolean-prop>_: Contains boolean values

## `<image>`-tag
The image property contains the path to an image file. It must only be used if the
resource is a `StillImageResource`!

_Note_: There is only _one_ <image> tag allowed per StillImageResource!

Example:
```xml
<image>postcards.dir/images/EURUS015a.jpg</image>
```

## Properties and values
All proporty tags must have a _name_-option:
- _name_: Name of the property as given in the ontology

Example:
```xml
<text-prop name="hasTranslation">
```

### `<text-prop>`-tag
The text property tag is used to list text values.

The `<text-prop>`-tag must contain at least one `<text>`-tag. There are several variants of text tags:

#### `<text>`-tag
The `<text>`-tag has the following options:
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

### `<color-prop>`-tag
The color-prop tag is used to define a color property.

#### `<color>`-tag
The color-tag is used to indicate a color value. The color has to be giiven in
web-notation, that is a "#" followed by 3 or 6 hex numerals.

A propery with 2 color valus would be defined as follows:
```xml
<color-prop name="hasColor">
    <color>#00ff66</color>
    <color>#ff00ff</color>
</color-prop>
```

### `<date-prop>`-tag
Is used to define knora dates.

#### `<date>`-tag
A Knora date value. It has the following format:
```
calendar:epoch:yyyy-mm-dd:epoch:yyyy-mm-dd
```
- _calendar_: either "JULIAN" or "GREGORIAN" [optional, default: GREGORIAN]
- _epoch_: either "BCE" or "CE" [optional, default CE]
- _yyyy_: year with four digits (at least one must be given)
- _mm_: month with two digits 01, 02, .., 12
- _dd_: day eith two digits

If two dates are given, the date is in between the two given limits. If the day is omitted,
then the precision it _month_, if also the month is omited, the procision is _year_.

Examples:
```
<date>GREGORIAN:CE:2014-01-31</date>
<date>GREGORIAN:CE:1930-09-02:CE:1930-09-03</date>
```
## `<float-prop>`-tag
Properties with decimal values. Contains one or more `<float>`-tags.

### `<float>`-tag
The float tag contains a decimal number. Example:
```
<float>3.14159</float>
```

## `<geometry-prop>`-tag
Properties which contain a geometric definition for a 2-D region (e.g. on an image)

### `<geometry>`-tag
A geometry is defined as a JSON object. It  contains the following data:
- _status_: "active" or "deleted"
- _type_: "circle", "rectangle" or "polygon"
- _lineColor_: WEB-Color
- _lineWidth_: integer number (in pixels)
- _points_: Array of coordinate objects of the form `{"x": decimal, "y": decimal}`
- _radius_: Coordinate object in the form `{"x": decimal, "y": decimal}`
Please note that all coordinates are normalized coordinates (relative to the image size)  between 0.0 and 1.0 !
The following example defines a poylgon:
```
{
   "status": "active",
   "type": "polygon",
   "lineColor": "#ff3333",
   "lineWidth": 2,
   "points: [{"x": 0.17252396166134185, "y": 0.1597222222222222},
             {"x": 0.8242811501597445,  "y": 0.14583333333333334},
             {"x": 0.8242811501597445,  "y": 0.8310185185185185},
             {"x": 0.1757188498402556,  "y": 0.8240740740740741},
             {"x": 0.1757188498402556,  "y": 0.1597222222222222},
             {"x": 0.16932907348242812, "y": 0.16435185185185186}],
   "original_index": 0
}
```
Thus, a <geometry>-tag may look like:
```
<geometry>{"status":"active","type"="circle","lineColor"="#ff0000","lineWidth"=2,"points":[{"x":0.5,"y":0.5}],"radius":{"x":0.1,"y":0.0}}</geometry>
```

## `<geoname-prop>`-tag
Used for values that contain a [geonames.org](http://geonames.org) location ID

### `<geoname>`-tag
Contains a valid geonames.org ID. Example (City of Wien):
```
<geoname>2761369</geoname>
```

## `<list-prop>`-tag
Entry into a list (list node). List nodes are identified by their `name`-property that was given when creating the list nodes (which must be unique within each list!).

### `<list>`-tag
Example:
```
<list>H_4128</list>
```

## `<iconclass-prop>`-tag
Contains the short code of an iconclass entry see [iconclass.org](http://iconclass.org).
For example the code
`92E112`stands for `(story of) Aurora (Eos); 'Aurora' (Ripa) - infancy, upbringing
Aurora · Ripa · air · ancient history · child · classical antiquity · goddess · gods · heaven · history · infancy · mythology · sky · upbringing · youth`

### `<iconclass>`-tag
Usage:
```
<iconclass>92E112</iconclass>
```

## `<integer-prop>`-tag
Contains integer values

### `<integer>`-tag
Usage:
```
<integer>4711</integer>
```

## `<interval-prop>`-tag
An interval defined a time period with a start and an end

### `<interval>`-tag
The interval-tag value has the following form or two decimals separated by a ":":
```
<interval>1.5:3.12</interval>
```

## `<resptr-prop>`-tag
A link to another resource within Knora

### `<resptr>`-tag
A value containing the XML-internal ID of the resource. If there is a resource deefined as
```
<resource label="EURUS015a" restype="Postcard" unique_id="238807">
…
</resource
```
it can be referenced as

```
<resptr>238807</resptr>
```

## `<time-prop>`-tag
A time property

### `<time>`-tag
This represents an exact date/time value in the form of `yyyy-mm-ddThh:mm:ss.sssssssssssszzzzzz`
The following abbreviations describe this form:

- _yyyy_ A four-digit numeral that represents the year. The value cannot begin with a negative (-) sign or a plus (+) sign. 0001 is the lexical representation of the year 1 of the Common Era (also known as 1 AD).
The value cannot be 0000.
- _mm_ A two-digit numeral that represents the month.
- _dd_ A two-digit numeral that represents the day.
- _hh_A two-digit numeral (with leading zeros as required) that represents the hours. The value must be between -14 and +14, inclusive.
- _mm_ A two-digit numeral that represents the minute.
- _ss_ A two-digit numeral that represents the whole seconds.
- _ssssssssssss_ Optional. If present, a 1-to-12 digit numeral that represents the fractional seconds.
- _zzzzzz_ Is required and represents the time zone. Each part of the datetime value that is expressed as a numeric value is constrained to the maximum value within the interval that is determined by the next-higher part of the datetime value. For example, the day value can never be 32 and cannot be 29 for month 02 and year 2002 (February 2002). 

The timezone is defined as follows:

- A positive (+) or negative (-) sign that is followed by hh:mm, where the following abbreviations are used:
- _hh_ A two-digit numeral (with leading zeros as required) that represents the hours. The value must be between -14 and +14, inclusive.
- _mm_  two-digit numeral that represents the minutes. The value of the minutes property must be zero when the hours property is equal to 14.
- _+_ Indicates that the specified time instant is in a time zone that is ahead of the UTC time by hh hours and mm minutes.
- _-_ Indicates that the specified time instant is in a time zone that is behind UTC time by hh hours and mm minutes.

or

- _Z_ The literal Z, which represents the time in UTC (Z represents Zulu time, which is equivalent to UTC). Specifying Z for the time zone is equivalent to specifying +00:00 or -00:00.

The following form indicates noon on 10 October 2009, Eastern Standard Time in the United States:
```
<time>2009-10-10T12:00:00-05:00</time>
<time>2019-10-23T13.45:12Z</time>
```

## `<uri-prop>`-tag
A property containing an valid URI

### `<uri>`-tag
Contains a syntactically valid URI

```
<uri>http://www.groove-t-gang.ch</ur>
```

## `<boolean-prop`>-tag
A property containing boolean values

### `<boolean>`-tag
Must contain the string "true" or "false", or the numeral "1" or "0"

```
<boolean>true</boolean>
<boolean>0</boolean>
```


