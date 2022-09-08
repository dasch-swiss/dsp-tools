[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP XML file format for importing data

With dsp-tools, data can be imported into a DSP repository (on a DSP server) from an XML file. The import file is a
standard XML file as described on this page. After a successful upload of the data, an output file is written (called 
`id2iri_mapping_[timstamp].json`) with the mapping from the internal IDs used inside the XML to their corresponding IRIs which
uniquely identify them inside DSP. This file should be kept if data is later added with the `--incremental` [option](#incremental-xml-upload).

The command to import an XML file on a DSP server is described [here](./dsp-tools-usage.md#upload-data-to-a-dsp-server).

The import file must start with the standard XML header:

```xml
<?xml version='1.0' encoding='utf-8'?>
```


## The root element &lt;knora&gt;

The `<knora>` element describes all resources that should be imported. It has the following attributes:

- `xmlns`: `"https://dasch.swiss/schema"` (required)
- `xmlns:xsi`: `"http://www.w3.org/2001/XMLSchema-instance"` (required)
- `xsi:schemaLocation`: `"https://dasch.swiss/schema https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/data.xsd"` (
  required)
- `shortcode`: project shortcode, e.g. "0801" (required)
- `default-ontology`: name of the ontology (required)

The `<knora>` element may look as follows:

```xml
<knora
    xmlns="https://dasch.swiss/schema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="https://dasch.swiss/schema https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/data.xsd"
    shortcode="0806"
    default-ontology="webern">
 ...
</knora>
```

The `<knora>` element can only contain the following sub-elements:

- `<permissions>` (optional)
- `<resource>`


## Describing permissions with &lt;permissions&gt; elements

The DSP server provides access control for each resource and each field of a resource through permissions. For a
thorough explanation of the permission and access system of DSP, see
[DSP permissions](https://docs.dasch.swiss/latest/DSP-API/02-knora-ontologies/knora-base/#permissions).

It is optional to define permissions in the XML. If not defined, default permissions are applied, so that only project and 
system administrators can view and edit resources. All other users have no rights at all, not even view or restricted view permissions.

The following access rights are defined by DSP:

- (no right): If no permission is defined for a certain group of users, these users cannot view any resources/values.
- `RV` _restricted view permission_: Same as `V`, but if it is applied to an image, the image is shown with a reduced resolution or with a watermark overlay.
- `V` _view permission_: The user can view a resource or a value, but cannot modify it.
- `M` _modifiy permission_: The user can modify the element, but cannot mark it as deleted. The original resource or value will be preserved.
- `D` _delete permission_: The user is allowed to mark an element as deleted. The original resource or value will be preserved.
- `CR` _change right permission_: The user can change the permission of a resource or value. The user is also allowed to permanently delete (erase) a resource.

The user does not hold the permissions directly, but belongs to an arbitrary number of groups which hold the
permissions. By default, the following groups always exist, and each user belongs to at least one of them:

- `UnknownUser`: The user is not known to DSP (not logged in).
- `KnownUser`: The user is known (logged in), but is not a member of the project the data element belongs to.
- `ProjectMember`: The user belongs to the same project as the data element.
- `ProjectAdmin`: The user is project administrator in the project the data element belongs to.
- `Creator`: The user is the owner of the element (created the element).
- `SystemAdmin`: The user is a system administrator.

In addition, more groups with arbitrary names can be created by a project admin. See [here](dsp-tools-create.md#groups) 
how to create a group in an ontology JSON file. For referencing a group, the project name has to be prepended to the 
group name, separated by a colon, e.g. `dsp-test:MlsEditors`.

A `<permissions>` element contains the permissions given to the selected groups and is called a _permission set_. It has
a mandatory attribute `id` and must contain at least one `<allow>` element:

```xml
<permissions id="res-default">
  <allow group="UnknownUser">RV</allow>
  <allow group="KnownUser">V</allow>
  <allow group="ProjectAdmin">CR</allow>
  <allow group="Creator">CR</allow>
  <allow group="dsp-test:MlsEditors">D</allow>
</permissions>
```

If you don't want a group to have access at all, leave it out. In the following example, resources or properties with 
permission `special-permission` can only be viewed by `ProjectAdmin`s:

```xml
<permissions id="special-permission">
  <allow group="ProjectAdmin">CR</allow>
</permissions>
```

Note: The permissions defined in the XML are applied to resources that are created. But only project or system 
administrators have the permission to create resources via the XML upload.


### The &lt;allow&gt; sub-element

The `<allow>` element is used to define the permission for a specific group. It is of the following form:

```xml
<allow group="ProjectAdmin">CR</allow>
```

The values `CR` etc. are described above.

The `group` attribute is mandatory. It defines the group which the permission is applied to. In addition to the DSP 
system groups, project specific groups are supported as well. A project specific group name has the form 
`project-shortname:groupname`. The available system groups are described above. 

There are no sub-elements allowed for the `<allow>` element.


### Example of a permissions section

A complete `<permissions>` section may look as follows:

```xml
<knora
    xmlns="https://dasch.swiss/schema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="https://dasch.swiss/schema https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/data.xsd"
    shortcode="0806"
    default-ontology="webern">
  
  <permissions id="res-default">
    <allow group="UnknownUser">RV</allow>
    <allow group="KnownUser">V</allow>
    <allow group="Creator">CR</allow>
    <allow group="ProjectAdmin">CR</allow>
  </permissions>
  
  <permissions id="res-restricted">
    <allow group="KnownUser">V</allow>
    <allow group="Creator">CR</allow>
    <allow group="ProjectAdmin">CR</allow>
  </permissions>
  
  <permissions id="prop-default">
    <allow group="UnknownUser">V</allow>
    <allow group="KnownUser">V</allow>
    <allow group="Creator">CR</allow>
    <allow group="ProjectAdmin">CR</allow>
  </permissions>
  
  <permissions id="prop-restricted">
    <allow group="KnownUser">RV</allow>
    <allow group="Creator">CR</allow>
    <allow group="ProjectAdmin">CR</allow>
  </permissions>
  ...
</knora>
```


### How to use the `permissions` attribute in resources/properties

Based on the permissions section of the above example, there are different ways how to grant permissions to a resource
and its properties. It is important to note that a resource doesn't inherit its permissions to its properties. Each 
property must have its own permissions. So, in the following example, the bitstreams don't inherit the permissions from their 
resource:

```xml
<resource ...>
    <bitstream permissions="prop-default">
        postcards/images/EURUS015a.jpg
    </bitstream>
</resource>
<resource ...>
    <bitstream permissions="prop-restricted">
        postcards/images/EURUS015a.jpg
    </bitstream>
</resource>
<resource ...>
    <bitstream>
        postcards/images/EURUS015a.jpg
    </bitstream>
</resource>
```

To take `KnownUser` as example:
 - With `permissions="prop-default"`, a logged-in user who is not member of the project (`KnownUser`) has `V` rights 
   on the image: Normal view.
 - With `permissions="prop-restricted"`, a logged-in user who is not member of the project (`KnownUser`) has `RV` 
   rights on the image: Blurred image.
 - With a blank `<bitstream>` tag, a logged-in user who is not member of the project (`KnownUser`) has no rights on 
   the image: No view possible. Only users from `ProjectAdmin` upwards are able to look at the image.


## Describing resources with the &lt;resource&gt; element

A `<resource>` element contains all necessary information to create a resource. It has the following attributes:

- `label`: a human-readable, preferably meaningful short name of the resource (required)
- `restype`: the resource type as defined within the ontology (required)
- `id`: a unique, arbitrary string providing a unique ID to the resource in order to be referencable by other resources;
  the ID is only used during the import process and later replaced by the IRI used internally by DSP (required)
- `permissions`: a reference to a permission set; the permissions will be applied to the created resource (optional)
- `iri`: a custom IRI used when migrating existing resources (optional)
- `ark`: a version 0 ARK used when migrating existing resources from salsah.org to DSP (optional), it is not possible to
use `iri` and `ark` in the same resource. When `ark` is used, it overrides `iri`.

A complete `<resource>` element may look as follows:

```xml
<resource label="EURUS015a"
          restype=":Postcard"
          id="238807"
          permissions="res-def-perm">
   ...
</resource>
```

The `<resource>` element contains a property element (e.g. `<text-prop>`) for each property class (i.e. data field)
describing the resource. The property element itself contains one or several value elements (e.g. `<text>`) and must
have an attribute `name` with the name of the property as defined in the project specific ontology.

Example for a property element of type text (`<text-prop>`) with two value elements `<text>`:

```xml
<text-prop name=":hasTranslation">
   <text encoding="utf8">Dies ist eine Übersetzung.</text>
   <text encoding="utf8">Dies ist eine weitere Übersetzung.</text>
</text-prop>
```

The following property elements exist:

- `<bitstream>`: contains a path to a file (if the resource is a multimedia resource)
- `<boolean-prop>`: contains a boolean value
- `<color-prop>`: contains color values
- `<date-prop>`: contains date values
- `<decimal-prop>`: contains decimal values
- `<geometry-prop>`: contains JSON geometry definitions for a region
- `<geoname-prop>`: contains [geonames.org](https://www.geonames.org/) location codes
- `<list-prop>`: contains list element labels
- `<integer-prop>`: contains integer values
- `<interval-prop>`: contains interval values
- `<period-prop>`: contains time period values (not yet implemented)
- `<resptr-prop>`: contains links to other resources
- `<text-prop>`: contains text values
- `<time-prop>`: contains time values
- `<uri-prop>`: contains URI values


### &lt;bitstream&gt;

The `<bitstream>` element is used for bitstream data. It contains the path to a bitstream object like an image file, a
ZIP container, an audio file etc. It must only be used if the resource is a `StillImageRepresentation`, an
`AudioRepresentation`, a `DocumentRepresentation` etc.

Note:

- There is only _one_ `<bitstream>` element allowed per representation!
- The `<bitstream>` element must be the first element!

Supported file extensions:

| Representation              | Supported formats                      |
| --------------------------- |----------------------------------------| 
| `ArchiveRepresentation`     | ZIP, TAR, GZ, Z, TAR.GZ, TGZ, GZIP, 7Z | 
| `AudioRepresentation`       | MP3, MP4, WAV                          | 
| `DocumentRepresentation`    | PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX   | 
| `MovingImageRepresentation` | MP4                                    | 
| `StillImageRepresentation`  | JPG, JPEG, PNG, TIF, TIFF, JP2         | 
| `TextRepresentation`        | TXT, CSV, XML, XSL, XSD                | 

For more details, please consult the [API docs](https://docs.dasch.swiss/latest/DSP-API/01-introduction/file-formats/).

Attributes:

- `permissions` : Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)

Example:

```xml
<bitstream permissions="prop-restricted">postcards/images/EURUS015a.jpg</bitstream>
```


### &lt;boolean-prop&gt;

The `<boolean-prop>` element is used for boolean values. It must contain exactly one `<boolean>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;boolean&gt;

The `<boolean>` element must contain the string "true" or "false", or the numeral 1 (true) or 0 (false).

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<boolean-prop name=":hasBoolean">
  <boolean>true</boolean>
</boolean-prop>
```

```xml
<boolean-prop name=":hasBoolean">
  <boolean>0</boolean>
</boolean-prop>
```


### &lt;color-prop&gt;

The `<color-prop>` element is used for color values. It must contain at least one `<color>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;color&gt;

The `<color>` element is used to indicate a color value. The color has to be given in web-notation, that is a `#`
followed by 3 or 6 hex numerals.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

A property with two color values would be defined as follows:
```xml
<color-prop name=":hasColor">
    <color>#00ff66</color>
    <color>#ff00ff</color>
</color-prop>
```


### &lt;date-prop&gt;

The `<date-prop>` element is used for date values. It must contain at least one `<date>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;date&gt;

the `<date>` element contains a DSP-specific date value. It has the following format:

```
calendar:epoch:yyyy-mm-dd:epoch:yyyy-mm-dd
```

- `calendar`: either "JULIAN" or "GREGORIAN" (optional, default: GREGORIAN)
- `epoch`: either "BCE" or "CE" (optional, default CE)
- `yyyy`: year with four digits (required)
- `mm`: month with two digits (optional, e.g. 01, 02, ..., 12)
- `dd`: day with two digits (optional, e.g. 01, 02, ..., 31)

If two dates are provided, the date is defined as range between the two dates. If the day is omitted, then the precision
it _month_, if also the month is omitted, the precision is _year_.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<date-prop name=":hasDate">
  <date>GREGORIAN:CE:2014-01-31</date>
</date-prop>
```

```xml
<date-prop name=":hasDate">
  <date>GREGORIAN:CE:1930-09-02:CE:1930-09-03</date>
</date-prop>
```


### &lt;decimal-prop&gt;

The `<decimal-prop>` element is used for decimal values. It must contain at least one `<decimal>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;decimal&gt;

The `<decimal>` element contains a decimal number.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<decimal-prop name=":hasDecimal">
  <decimal>3.14159</decimal>
</decimal-prop>
```


### &lt;geometry-prop&gt;

The `<geometry-prop>` element is used for a geometric definition of a 2-D region (e.g. a region on an image). It must
contain at least one `<geometry>` element.

Note:

- Usually these are not created by an import and should be used with caution!

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;geometry&gt;

A geometry value is defined as a JSON object. It contains the following data:

- `status`: "active" or "deleted"
- `type`: "circle", "rectangle" or "polygon"
- `lineColor`: web-color
- `lineWidth`: integer number (in pixels)
- `points`: array of coordinate objects of the form `{"x": decimal, "y": decimal}`
- `radius`: coordinate object of the form `{"x": decimal, "y": decimal}`

Please note that all coordinates are normalized coordinates (relative to the image size) between 0.0 and 1.0!

The following example defines a polygon:

```json
{
   "status": "active",
   "type": "polygon",
   "lineColor": "#ff3333",
   "lineWidth": 2,
   "points": [{"x": 0.17252396166134185, "y": 0.1597222222222222},
             {"x": 0.8242811501597445,  "y": 0.14583333333333334},
             {"x": 0.8242811501597445,  "y": 0.8310185185185185},
             {"x": 0.1757188498402556,  "y": 0.8240740740740741},
             {"x": 0.1757188498402556,  "y": 0.1597222222222222},
             {"x": 0.16932907348242812, "y": 0.16435185185185186}],
   "original_index": 0
}
```

Example of a `<geometry>` element:

```xml
<geometry-prop name=":hasPolygon">
  <geometry>{"status":"active","type"="circle","lineColor"="#ff0000","lineWidth"=2,"points":[{"x":0.5,"y":0.5}],"radius":{"x":0.1,"y":0.0}}</geometry>
</geometry-prop>
```

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)


### &lt;geoname-prop&gt;

The `<geoname-prop>` element is used for values that contain a [geonames.org](http://geonames.org) ID. It must contain
at least one `<geoname>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;geoname&gt;

Contains a valid [geonames.org](http://geonames.org) ID.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example (city of Vienna):

```xml
<geoname-prop name=":hasLocation">
  <geoname>2761369</geoname>
</geoname-prop>
```


### &lt;integer-prop&gt;

The `<integer-prop>` element is used for integer values. It must contain at least one `<integer>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;integer&gt;

The `<integer>` element contains an integer value.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<integer-prop name=":hasInteger">
  <integer>4711</integer>
</integer-prop>
```


### &lt;interval-prop&gt;

The `<interval-prop>` element is used for intervals with a start and an end point on a timeline, e.g. relative to the beginning of an audio or video file. 
An `<interval-prop>`  must contain at least one `<interval>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;interval&gt;

A time interval is represented by plain decimal numbers (=seconds), without a special notation for minutes and hours. 
The `<interval>` element contains two decimals separated by a colon (`:`). The places before the decimal point are 
seconds, and the places after the decimal points are fractions of a second.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<interval-prop name=":hasInterval">
  <interval>60.5:120.5</interval>          <!-- 0:01:00.5 - 0:02:00.5 -->
  <interval>61:3600</interval>             <!-- 0:01:01 - 1:00:00 -->
</interval-prop>
```


### &lt;list-prop&gt;

The `<list-prop>` element is used as entry point into a list (list node). List nodes are identified by their `name`
attribute that was given when creating the list nodes (which must be unique within each list!). It must contain at least
one `<list>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)
- `list`: name of the list as defined in the ontology (required)


#### &lt;list&gt;

The `<list>` element references a node in a (pull-down or hierarchical) list.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<list-prop list="category" name=":hasCategory">
  <list>physics</list>
</list-prop>
```


### &lt;resptr-prop&gt;

The `<resptr-prop>` element is used to link other resources within DSP. It must contain at least one `<resptr>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;resptr&gt;

The `<resptr>` element contains either the internal ID of another resource inside the XML or the IRI of an already
existing resource on DSP. Inside the same XML file, a mixture of the two is not possible. If referencing existing
resources, `xmlupload --incremental` has to be used.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

If there is a resource defined as `<resource label="EURUS015a" restype=":Postcard" id="238807">...</resource>`, it can
be referenced as:

```xml
<resptr-prop name=":hasReferenceTo">
  <resptr>238807</resptr>
</resptr-prop>
```


### &lt;text-prop&gt;

The `<text-prop>` element is used for text values. It must contain at least one `<text>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;text&gt;

The `<text>` element has the following attributes:

- `encoding`: either "utf8" or "xml" (required)
    - `utf8`: The element describes a simple text without markup. The text is a simple UTF-8 string.
    - `xml`: The element describes a complex text containing markup. It must follow the XML format as defined by the
    [DSP standard mapping](https://docs.dasch.swiss/latest/DSP-API/03-apis/api-v2/xml-to-standoff-mapping/).
- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

There are two variants of text: Simple (UTF8) and complex (XML). Within a text property, multiple simple and 
complex text values may be mixed. Both simple and complex text values can be used inside all gui_elements 
that are defined in an ontology (SimpleText, Richtext, Textarea, see [here](dsp-tools-create-ontologies.md#textvalue)). 
But typically, you would use UTF8 in a SimpleText, and XML in Richtext or Textarea.


#### Simple text (UTF-8)

An example for simple text:

```xml
<text-prop name=":hasComment">
  <text encoding="utf8">Probe bei "Wimberger". Lokal in Wien?</text>
</text-prop>
```

If your text is very long, it is not advised to add XML-"pretty-print" whitespaces after line breaks. These 
whitespaces will be taken into the text field as they are.


#### Text with markup (XML)

dsp-tools assumes that for markup (standoff markup), the
[DSP standard mapping](https://docs.dasch.swiss/latest/DSP-API/03-apis/api-v2/xml-to-standoff-mapping/) is used (custom mapping is not yet
implemented).

Example of a text containing a link to another resource:

```xml
<text-prop name=":hasComment">
  <text encoding="xml" >The <strong>third</strong> object and a <a class="salsah-link" href="IRI:obj_0003:IRI">link</a>.</text>
</text-prop>
```

Please note that the `href` option within the anchor tag (`<a>`) points to an internal resource of the DSP and has to
conform to the special format `IRI:[res-id]:IRI` where [res-id] is the resource id defined within the XML import file.


### &lt;time-prop&gt;

The `<time-prop>` element is used for time values. It must contain at least one `<time>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;time&gt;

The `<time>` element represents an exact datetime value in the form of `yyyy-mm-ddThh:mm:ss.sssssssssssszzzzzz`. The
following abbreviations describe this form:

- `yyyy`: a four-digit numeral that represents the year. The value cannot start with a minus (-) or a plus (+) sign.
  0001 is the lexical representation of the year 1 of the Common Era (also known as 1 AD). The value cannot be 0000.
- `mm`: a two-digit numeral that represents the month
- `dd`: a two-digit numeral that represents the day
- `hh`: a two-digit numeral representing the hours. Must be between 0 and 23
- `mm`: a two-digit numeral that represents the minutes
- `ss`: a two-digit numeral that represents the seconds
- `ssssssssssss`: If present, a 1-to-12-digit numeral that represents the fractional seconds (optional)
- `zzzzzz`: represents the time zone (required).

Each part of the datetime value that is expressed as a numeric value is constrained to the maximum value within the 
interval that is determined by the next higher part of the datetime value.
For example, the day value can never be 32 and cannot be 29 for month 02 and year 2002 (February 2002).

The timezone is defined as follows:

- A plus (+) or minus (-) sign that is followed by hh:mm:
    - `+`: Indicates that the specified time instant is in a time zone that is ahead of the UTC time by hh hours and mm
      minutes.
    - `-`: Indicates that the specified time instant is in a time zone that is behind UTC time by hh hours and mm
      minutes.
    - `hh`: a two-digit numeral (with leading zeros as required) that represents the hours. The value must be between
      -14 and +14, inclusive.
    - `mm`: a two-digit numeral that represents the minutes. The value must be zero when hh is equal to 14.
- Z: The literal Z, which represents the time in UTC (Z represents Zulu time, which is equivalent to UTC). Specifying Z
  for the time zone is equivalent to specifying +00:00 or -00:00.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<time-prop name=":hasTime">
  <time>2019-10-23T13:45:12Z</time>
</time-prop>
```

The following value indicates noon on October 10, 2009, Eastern Standard Time in the United States:

```xml
<time-prop name=":hasTime">
  <time>2009-10-10T12:00:00-05:00</time>
</time-prop>
```


### &lt;uri-prop&gt;

The `<uri-prop>` element is used for referencing resources with a URI. It must contain at least one `<uri>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)


#### &lt;uri&gt;

The `<uri>` element contains a syntactically valid URI.

Attributes:

- `permissions`: Permission ID (optional, but if omitted, users who are lower than a `ProjectAdmin` have no permissions at all, not even view rights)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<uri-prop name=":hasURI">
   <uri>http://www.groove-t-gang.ch</uri>
</uri-prop>
```


## DSP base resources / base properties to be used directly in the XML file
There is a number of base resources and base properties that must not be subclassed in a project ontology. They are 
directly available in the XML data file. Please have in mind that built-in names of the knora-base ontology must be used 
without prepended colon.  
See also [the related part of the ontology documentation](dsp-tools-create-ontologies.md#dsp-base-resources-base-properties-to-be-used-directly-in-the-xml-file).

### `<annotation>`
`<annotation>` is an annotation to another resource of any class. It must have the following predefined properties:

- `hasComment` (1-n)
- `isAnnotationOf` (1)

Example:
```xml
<annotation label="Annotation to another resource" id="annotation_0" permissions="res-default">
    <text-prop name="hasComment">
        <text encoding="utf8" permissions="prop-default">This is an annotation to a resource.</text>
    </text-prop>
    <resptr-prop name="isAnnotationOf">
        <resptr permissions="prop-default">img_1</resptr>
    </resptr-prop>
</annotation>
```

Technical note: An `<annotation>` is in fact a `<resource restype="Annotation">`. But it is mandatory to use the 
shortcut, so that the XML file can be validated more precisely.

### `<region>`
A `<region>` resource defines a region of interest (ROI) in an image. It must have the following predefined properties:

- `hasColor` (1)
- `isRegionOf` (1)
- `hasGeometry` (1)
- `hasComment` (1-n)

There are three types of Geometry shapes (rectangle, circle, polygon), but only the rectangle is implemented.

Example:
```xml
<region label="Region in image" id="region_0" permissions="res-default">
    <color-prop name="hasColor">
        <color permissions="prop-default">#5d1f1e</color>
    </color-prop>
    <resptr-prop name="isRegionOf">
        <resptr permissions="prop-default">img_1</resptr>
    </resptr-prop>
    <geometry-prop name="hasGeometry">
        <geometry permissions="prop-default">
            {
                "status": "active",
                "type": "rectangle",
                "lineColor": "#ff3333",
                "lineWidth": 2,
                "points": [
                    {"x":0.08098591549295775,"y":0.16741071428571427},
                    {"x":0.739436619718309900,"y":0.72991071428571430}
                ],
                "original_index": 0
            }
        </geometry>
    </geometry-prop>
    <text-prop name="hasComment">
        <text encoding="utf8" permissions="prop-default">This is a rectangle-formed region of interest.</text>
    </text-prop>
</region>
```

Technical note: A `<region>` is in fact a `<resource restype="Region">`. But it is mandatory to use the 
shortcut, so that the XML file can be validated more precisely.

### `<link>`
`<link>` is a resource linking together several other resources of different classes. It must have the following 
predefined properties:

- `hasComment` (1-n)
- `hasLinkTo` (1-n)

Example:
```xml
<link label="Link between three resources" id="link_obj_0" permissions="res-default">
    <text-prop name="hasComment">
        <text permissions="prop-default" encoding="utf8">
            A link object can link together an arbitrary number of resources from any resource class.
        </text>
    </text-prop>
    <resptr-prop name="hasLinkTo">
        <resptr permissions="prop-default">doc_001</resptr>
        <resptr permissions="prop-default">img_obj_5</resptr>
        <resptr permissions="prop-default">audio_obj_0</resptr>
    </resptr-prop>
</link>
```

Technical note: A `<link>` is in fact a `<resource restype="LinkObj">`. But it is mandatory to use the 
shortcut, so that the XML file can be validated more precisely.


## Incremental XML Upload

After a successful upload of the data, an output file is written (called `id2iri_mapping_[timstamp].json`) with the 
mapping of internal IDs used inside the XML and their corresponding IRIs which uniquely identify them inside DSP. This 
file should be kept if data is later added with the `--incremental` option. 

To do an incremental XML upload, one of the following procedures is recommended.

- Incremental XML upload with use of internal IDs:

1. Initial XML upload with internal IDs.
2. The file `id2iri_mapping_[timestamp].json` is created.
3. Create new XML file(s) with resources referencing other resources by their internal IDs in `<resptr>` (using the same IDs as in the initial XML upload).
4. Run `dsp-tools id2iri new_data.xml id2iri_mapping_[timestamp].json` to replace the internal IDs in `new_data.xml` with IRIs. Only internal IDs inside the `<resptr>` tag are replaced.
5. Run `dsp-tools xmlupload --incremental new_data.xml` to upload the data to DSP.

- Incremental XML Upload with the use of IRIs: Use IRIs in the XML to reference existing data on the DSP server.


## Complete example

```xml
<?xml version='1.0' encoding='utf-8'?>
<knora 
    xmlns="https://dasch.swiss/schema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="https://dasch.swiss/schema https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/data.xsd"
    shortcode="0001"
    default-ontology="anything">

    <!-- permissions: see https://docs.dasch.swiss/latest/DSP-API/02-knora-ontologies/knora-base/#permissions -->
    <permissions id="res-default">
        <allow group="UnknownUser">V</allow>
        <allow group="KnownUser">V</allow>
        <allow group="Creator">CR</allow>
        <allow group="ProjectAdmin">CR</allow>
        <allow group="anything:Thing searcher">D</allow>
    </permissions>
    <permissions id="res-restricted">
        <allow group="UnknownUser">RV</allow>
        <allow group="KnownUser">V</allow>
        <allow group="Creator">CR</allow>
        <allow group="ProjectAdmin">CR</allow>
        <allow group="anything:Thing searcher">M</allow>
    </permissions>
    <permissions id="prop-default">
        <allow group="UnknownUser">V</allow>
        <allow group="KnownUser">V</allow>
        <allow group="Creator">CR</allow>
        <allow group="ProjectAdmin">CR</allow>
        <allow group="anything:Thing searcher">D</allow>
    </permissions>
    <permissions id="prop-restricted">
        <allow group="UnknownUser">RV</allow>
        <allow group="KnownUser">V</allow>
        <allow group="Creator">CR</allow>
        <allow group="ProjectAdmin">CR</allow>
        <allow group="anything:Thing searcher">M</allow>
    </permissions>
    <resource label="obj_inst1"
              restype=":BlueThing"
              id="obj_0001"
              permissions="res-default">
        <list-prop list="treelistroot" name=":hasListItem">
            <list permissions="prop-default">Tree list node 02</list>
        </list-prop>
        <list-prop list="treelistroot" name=":hasOtherListItem">
            <list permissions="prop-default">Tree list node 03</list>
        </list-prop>
        <text-prop name=":hasRichtext">
            <text permissions="prop-default" encoding="xml" >The <strong>third</strong> object and a <a class="salsah-link" href="IRI:obj_0003:IRI">link</a> to.</text>
        </text-prop>
        <text-prop name=":hasRichtext">
            <text permissions="prop-default" encoding="xml" >The <strong>third</strong> object and a <a class="salsah-link" href="IRI:obj_0003:IRI">link</a> to.</text>
        </text-prop>
        <text-prop name=":hasText">
            <text permissions="prop-default" encoding="utf8">Dies ist ein einfacher Text ohne Markup</text>
            <text permissions="prop-restricted" encoding="utf8">Nochmals ein einfacher Text</text>
        </text-prop>
        <date-prop name=":hasDate">
            <date permissions="prop-default">JULIAN:CE:1401-05-17:CE:1402-01</date>
        </date-prop>
        <integer-prop name=":hasInteger">
            <integer permissions="prop-default">4711</integer>
        </integer-prop>
        <decimal-prop name=":hasDecimal">
            <decimal permissions="prop-default" comment="Eulersche Zahl">2.718281828459</decimal>
        </decimal-prop>
        <boolean-prop name=":hasBoolean">
            <boolean permissions="prop-default">true</boolean>
        </boolean-prop>
        <uri-prop name=":hasUri">
            <uri permissions="prop-default">http://dasch.swiss/gaga</uri>
        </uri-prop>
        <interval-prop name=":hasInterval">
            <interval permissions="prop-default">12.5:14.2</interval>
        </interval-prop>
        <color-prop name=":hasColor">
            <color permissions="prop-default">#00ff00</color>
        </color-prop>
        <geometry-prop name=":hasGeometry">
            <geometry permissions="prop-default">
                {
                    "status":"active",
                    "lineColor":"#ff3333",
                    "lineWidth":2,
                    "points":[
                        {"x":0.08098591549295775,"y":0.16741071428571427},
                        {"x":0.7394366197183099,"y":0.7299107142857143}],
                    "type":"rectangle",
                    "original_index":0
                }
            </geometry>
        </geometry-prop>
        <geoname-prop name=":hasGeoname">
            <geoname permissions="prop-default" comment="A sacred place for railroad fans">5416656</geoname>
        </geoname-prop>
        <resptr-prop name=":hasBlueThing">
            <resptr permissions="prop-default">obj_0002</resptr>
        </resptr-prop>
    </resource>

    <resource label="obj_inst2"
              restype=":BlueThing"
              id="obj_0002"
              permissions="res-default">
        <list-prop list="treelistroot" name=":hasListItem">
            <list permissions="prop-default">Tree list node 10</list>
        </list-prop>
        <list-prop list="treelistroot" name=":hasOtherListItem">
            <list permissions="prop-default">Tree list node 11</list>
        </list-prop>
        <text-prop name=":hasRichtext">
            <text permissions="prop-default" encoding="xml">What is this <em>bold</em> thing?</text>
        </text-prop>
        <text-prop name=":hasText">
            <text permissions="prop-default" encoding="utf8">aa bbb cccc ddddd</text>
        </text-prop>
        <date-prop name=":hasDate">
            <date permissions="prop-default">1888</date>
        </date-prop>
        <integer-prop name=":hasInteger">
            <integer permissions="prop-default">42</integer>
        </integer-prop>
        <decimal-prop name=":hasDecimal">
            <decimal permissions="prop-default" comment="Die Zahl PI">3.14159</decimal>
        </decimal-prop>
        <boolean-prop name=":hasBoolean">
            <boolean permissions="prop-default">false</boolean>
        </boolean-prop>
        <uri-prop name=":hasUri">
            <uri permissions="prop-default">http://unibas.ch/gugus</uri>
        </uri-prop>
        <interval-prop name=":hasInterval">
            <interval permissions="prop-default">24:100.075</interval>
        </interval-prop>
        <color-prop name=":hasColor">
            <color permissions="prop-default">#33ff77</color>
        </color-prop>
        <geometry-prop name=":hasGeometry">
            <geometry permissions="prop-default">
                {
                    "status":"active",
                    "lineColor":"#ff3333",
                    "lineWidth":2,
                    "points":[
                        {"x":0.08098591549295775,"y":0.16741071428571427},
                        {"x":0.7394366197183099,"y":0.7299107142857143}],
                    "type":"rectangle",
                    "original_index":0
                }
            </geometry>
        </geometry-prop>
        <geoname-prop name=":hasGeoname">
            <geoname permissions="prop-default" comment="A sacred place for railroad fans">5416656</geoname>
        </geoname-prop>
        <resptr-prop name=":hasBlueThing">
            <resptr permissions="prop-default">obj_0003</resptr>
        </resptr-prop>
    </resource>

    <resource label="obj_inst3"
              restype=":BlueThing"
              id="obj_0003"
              permissions="res-default">
        <list-prop list="treelistroot" name=":hasListItem">
            <list permissions="prop-default">Tree list node 01</list>
        </list-prop>
        <list-prop list="treelistroot" name=":hasOtherListItem">
            <list permissions="prop-default">Tree list node 02</list>
        </list-prop>
        <text-prop name=":hasRichtext">
            <text permissions="prop-default" encoding="xml">This is <em>bold and <strong>strong</strong></em> text!</text>
        </text-prop>
        <text-prop name=":hasText">
            <text permissions="prop-default" encoding="utf8">aa bbb cccc ddddd</text>
        </text-prop>
        <date-prop name=":hasDate">
            <date permissions="prop-default">1888</date>
        </date-prop>
        <integer-prop name=":hasInteger">
            <integer permissions="prop-default">42</integer>
        </integer-prop>
        <decimal-prop name=":hasDecimal">
            <decimal permissions="prop-default" comment="Die Zahl PI">3.14159</decimal>
        </decimal-prop>
        <boolean-prop name=":hasBoolean">
            <boolean permissions="prop-default">false</boolean>
        </boolean-prop>
        <uri-prop name=":hasUri">
            <uri permissions="prop-default">http://unibas.ch/gugus</uri>
        </uri-prop>
        <interval-prop name=":hasInterval">
            <interval permissions="prop-default">24:100.075</interval>
        </interval-prop>
        <color-prop name=":hasColor">
            <color permissions="prop-default">#33ff77</color>
        </color-prop>
        <geometry-prop name=":hasGeometry">
            <geometry permissions="prop-default">
                {
                    "status":"active",
                    "lineColor":"#ff3333",
                    "lineWidth":2,
                    "points":[
                        {"x":0.08098591549295775,"y":0.16741071428571427},
                        {"x":0.7394366197183099,"y":0.7299107142857143}],
                    "type":"rectangle",
                    "original_index":0
                }
            </geometry>
        </geometry-prop>
        <geoname-prop name=":hasGeoname">
            <geoname permissions="prop-default" comment="A sacred place for railroad fans">5416656</geoname>
        </geoname-prop>
    </resource>

    <resource label="obj_inst4"
              restype=":ThingPicture"
              id="obj_0004"
              permissions="res-default">
        <bitstream>gaga.tif</bitstream>
        <text-prop name=":hasPictureTitle">
            <text permissions="prop-default" encoding="utf8">This is the famous Lena</text>
        </text-prop>
    </resource>

</knora>

```
