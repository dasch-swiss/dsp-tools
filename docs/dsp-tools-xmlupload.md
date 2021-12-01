[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# DSP XML file format for importing data

With dsp-tools data can be imported into a DSP repository (on a DSP server) from an XML file. The import file is a
standard XML file as described on this page. After a successful upload of the data, an output file is written (called 
`id2iri_mapping_[timstamp].json`) with the mapping of internal IDs used inside the XML and their corresponding IRIs which
uniquely identify them inside DSP. This file should be kept if data is later added with the `--incremental` [option](#incremental-xml-upload).

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
thorough explanation of the permission and access system of the DSP platform, see
[DSP platform permissions](https://docs.knora.org/02-knora-ontologies/knora-base/#permissions).

It is optional to define permissions in the XML. If not defined, default permissions are applied (only project and 
system administrators can view and edit resources).

The following access rights are defined by the DSP platform which apply to either a resource or a field:

- `RV` _restricted view permission_: The user gets only a restricted view of the element. E.g. in case of a still image
  resource, the image is displayed at reduced resolution or with a watermark overlay.
- `V` _view permission_: The user has read access to the element.
- `M` _modifiy permission_: The user may modify the element, but may not delete it.
- `D` _delete permission_: The user is allowed to delete the element.
- `CR` _change right permission_: The user may change the permission of the element.

The user does not hold the permissions directly, but may belong to an arbitrary number of groups which hold the
permissions. By default, the following groups always exist, and each user belongs to at least one of them:

- `UnknownUser`: The user is not known to the DSP platform (not logged in).
- `KnownUser`: The user is known (performed login), but is not a member of the project the data element belongs to.
- `ProjectMember`: The user belongs to the same project as the data element.
- `ProjectAdmin`: The user is project administrator in the project the data element belongs to.
- `Creator`: The user is the owner of the element (created the element).
- `SystemAdmin`: The user is a system administrator.

In addition, more groups with arbitrary names can be created by a project admin. For referencing a group, the project
name has to be prepended before the group name, separated by a colon, e.g. `dsp-test:MlsEditors`.

A `<permissions>` element contains the permissions given to the selected groups and is called a _permission set_. It has
a mandatory attribute `id` and must contain at least one `<allow>` element per group indicating the group's permission.
The permission is referenced inside the resource or property tag by its `id`. It is of the following form:

```xml
<permissions id="res-default">
  <allow group="UnknownUser">RV</allow>
  <allow group="KnownUser">V</allow>
  <allow group="ProjectAdmin">CR</allow>
  <allow group="Creator">CR</allow>
  <allow group="dsp-test:MlsEditors">D</allow>
</permissions>
```

If you don't want a group to have access at all, leave it out. In the following example, only `ProjectAdmin`s will see
the resource or property with permission `special-permission`:

```xml
<permissions id="special-permission">
  <allow group="ProjectAdmin">CR</allow>
</permissions>
```


### The &lt;allow&gt; sub-element

The `<allow>` element is used to define the permission for a specific group. It is of the following form:

```xml
<allow group="ProjectAdmin">CR</allow>
```

The allowed values are:

- `RV` _restricted view_: Same as `V` but if it is applied to an image, the image is shown blurred.
- `V` _view_: The user can view a resource or a value, but can not modify it.
- `M` _modify_: The user can modify a resource or value, but can not delete it. The original resource or value will be preserved.
- `D` _delete_: The user can mark a resource or value as deleted. The original resource or value will be preserved.
- `CR` _change right_: The user can change the permission of a resource or value. The user is also allowed to 
  permanently delete (erase) a resource.

The `group` attribute is mandatory. It defines the group which the permission is applied to. DSP system groups as
well as project specific groups are supported. A project specific group name has the form `project-shortname:groupname`.
The available system groups are:

- UnknownUser (not logged in user)
- KnownUser (logged in user)
- ProjectMember (user with project membership)
- Creator (creator of the resource or value)
- ProjectAdmin (user with project admin membership)
- SystemAdmin (system administrator)

There are no sub-elements allowed for the `<allow>` element.

### Example for a permissions section

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
    <allow group="KnownUser">V</allow>
    <allow group="Creator">CR</allow>
    <allow group="ProjectAdmin">CR</allow>
  </permissions>
  ...
</knora>
```

## Describing resources with the &lt;resource&gt; element

A `<resource>` element contains all necessary information to create a resource. It has the following attributes:

- `label`: a human-readable, preferably meaningful short name of the resource (required)
- `restype`: the resource type as defined within the ontology (required)
- `id`: a unique, arbitrary string providing a unique ID to the resource in order to be referencable by other resources;
  the ID is only used during the import process and later replaced by the IRI used internally by DSP (required)
- `permissions`: a reference to a permission set; the permissions will be applied to the created resource (optional)

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

| ⚠ Look out  |
|:----------|
| In case of a cardinality 1-n, multiple `<text>` tags have to be created inside the `<text-prop>` tag (do not use multiple `<text-prop>` tags). |

The following property elements exist:

- `<bitstream>`: contains the path to the file
- `<text-prop>`: contains text values
- `<color-prop>`: contains color values
- `<date-prop>`: contains date values
- `<decimal-prop>`: contains decimal values
- `<geometry-prop>`: contains a JSON geometry definition for a region
- `<geoname-prop>`: contains a [geonames.org](https://www.geonames.org/) location code
- `<list-prop>`: contains list element labels
- `<iconclass-prop>`: contains [iconclass.org](http://iconclass.org/) codes
- `<integer-prop>`: contains integer values
- `<interval-prop>`: contains interval values
- `<period-prop>`: contains time period values
- `<resptr-prop>`: contains links to other resources
- `<time-prop>`: contains time values
- `<uri-prop>`: contains URI values
- `<boolean-prop>`: contains boolean values

### `<bitstream>`

The `<bitstream>` element is used for bitstream data. It contains the path to a bitstream object like an image file, a
ZIP container, an audio file etc. It must only be used if the resource is a `StillImageRepresentation`, an
`AudioRepresentation`, a `DocumentRepresentation` etc.

Note:

- There is only _one_ `<bitstream>` element allowed per representation!
- The `<bitstream>` element must be the first element!

Attributes:

- `permissions` : ID or a permission set (optional, but if omitted very restricted default permissions apply)

Example:

```xml
<bitstream permissions="prop-restricted">postcards/images/EURUS015a.jpg</bitstream>
```

### `<text-prop>`

The `<text-prop>` element is used for text values. It must contain at least one `<text>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<text>`

The `<text>` element has the following attributes:

- `encoding`: either "utf8" or "xml" (required)
    - `utf8`: The element describes a simple text without markup. The text is a simple UTF-8 string.
    - `xml`: The element describes a complex text containing markup. It must follow the XML format as defined by the
      [DSP standard mapping](https://docs.knora.org/03-apis/api-v1/xml-to-standoff-mapping/).
- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

There are two variants of text:

#### Simple text (UTF-8)

An example for simple text:

```xml
<text-prop name=":hasComment">
  <text encoding="utf8">Probe bei "Wimberger". Lokal in Wien?</text>
</text-prop>
```

#### Text with markup (XML)

dsp-tools assumes that for markup (standoff markup) the
[DSP standard mapping](https://docs.knora.org/03-apis/api-v1/xml-to-standoff-mapping/) used (custom mapping is not yet
implemented).

Example of a text containing a link to another resource:

```xml
<text-prop name=":hasComment">
  <text encoding="xml" >The <strong>third</strong> object and a <a class="salsah-link" href="IRI:obj_0003:IRI">link</a>.</text>
</text-prop>
```

Please note that the `href` option within the anchor tag (`<a>`) points to an internal resource of the DSP and has to
conform to the special format `IRI:[res-id]:IRI` where [res-id] is the resource id defined within the XML import file.

Within a text property, multiple simple and complex text values may be mixed.

### `<color-prop>`

The `<color-prop>` element is used for color values. It must contain at least one `<color>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<color>`

The `<color>` element is used to indicate a color value. The color has to be given in web-notation, that is a `#`
followed by 3 or 6 hex numerals.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

A property with two color values would be defined as follows:

```xml
<color-prop name=":hasColor">
    <color>#00ff66</color>
    <color>#ff00ff</color>
</color-prop>
```

### `<date-prop>`

The `<date-prop>` element is used for date values. It must contain a `<date>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<date>`

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

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
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

### `<decimal-prop>`

The `<decimal-prop>` element is used for decimal values. It must contain at least one `<decimal>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<decimal>`

The `<decimal>` element contains a decimal number.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<decimal-prop name=":hasDecimal">
  <decimal>3.14159</decimal>
</decimal-prop>
```

### `<geometry-prop>`

The `<geometry-prop>` element is used for a geometric definition of a 2-D region (e.g. a region on an image). It must
contain at least one `<geometry>` element.

Note:

- Usually these are not created by an import and should be used with caution!

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<geometry>`

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

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

### `<geoname-prop>`

The `<geoname-prop>` element is used for values that contain a [geonames.org](http://geonames.org) ID. It must contain
at least one `<geoname>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<geoname>`

Contains a valid [geonames.org](http://geonames.org) ID.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

Example (city of Vienna):

```xml
<geoname-prop name=":hasLocation">
  <geoname>2761369</geoname>
</geoname-prop>
```

### `<list-prop>`

The `<list-prop>` element is used as entry point into a list (list node). List nodes are identified by their `name`
attribute that was given when creating the list nodes (which must be unique within each list!). It must contain at least
one `<list>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)
- `list`: name of the list as defined in the ontology (required)

#### `<list>`

The `<list>` element references a node in a (pull-down or hierarchical) list.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<list-prop list="category" name=":hasCategory">
  <list>physics</list>
</list-prop>
```

### `<iconclass-prop>` (_not yet implemented_)

The `<iconclass-prop>` element is used for [iconclass.org](http://iconclass.org) ID. It must contain at least one
`<iconclass>` element.

For example: `92E112` stands
for `(story of) Aurora (Eos); 'Aurora' (Ripa) - infancy, upbringing Aurora · Ripa · air · ancient history · child · classical antiquity · goddess · gods · heaven · history · infancy · mythology · sky · upbringing · youth`

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<iconclass>` (_not yet implemented_)

References an [iconclass.org](https://iconclass.org) ID.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

Usage:

```xml
<iconclass-prop name=":hasIcon">
  <iconclass>92E112</iconclass>
</iconclass-prop>
```

### `<integer-prop>`

The `<integer-prop>` element is used for integer values. It must contain at least one `<integer>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<integer>`

The `<integer>` element contains an integer value.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<integer-prop name=":hasInteger">
  <integer>4711</integer>
</integer-prop>
```

### `<interval-prop>`

The `<interval-prop>` element is used for time periods with start and end dates. It must contain at least one
`<interval>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<interval>`

The `<interval>` element contains two decimals separated by a colon (`:`).

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<interval-prop name=":hasInterval">
  <interval>1.5:3.12</interval>
</interval-prop>
```

### `<resptr-prop>`

The `<resptr-prop>` element is used to link other resources within DSP. It must contain a `<resptr>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<resptr>`

The `<resptr>` element contains either the internal ID of another resource inside the XML or the IRI of an already
existing resource on DSP. Inside the same XML file a mixture of the two is not possible. If referencing existing
resources, `xmlupload --incremental` has to be used.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

Example:

If there is a resource defined as `<resource label="EURUS015a" restype=":Postcard" id="238807">...</resource>`, it can
be referenced as:

```xml
<resptr-prop name=":hasReferenceTo">
  <resptr>238807</resptr>
</resptr-prop>
```

### `<time-prop>`

The `<time-prop>` element is used for time values. It must contain at least one `<time>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<time>`

The `<time>` element represents an exact datetime value in the form of `yyyy-mm-ddThh:mm:ss.sssssssssssszzzzzz`. The
following abbreviations describe this form:

- `yyyy`: a four-digit numeral that represents the year. The value cannot start with a minus (-) or a plus (+) sign.
  0001 is the lexical representation of the year 1 of the Common Era (also known as 1 AD). The value cannot be 0000.
- `mm`: a two-digit numeral that represents the month
- `dd`: a two-digit numeral that represents the day
- `hh`: a two-digit numeral (with leading zeros as required) that represents the hours. The value must be between -14
  and +14, inclusive.
- `mm`: a two-digit numeral that represents the minutes
- `ss`: a two-digit numeral that represents the seconds
- `ssssssssssss`: If present, a 1-to-12-digit numeral that represents the fractional seconds (optional)
- `zzzzzz`: represents the time zone (required). Each part of the datetime value that is expressed as a numeric value is
  constrained to the maximum value within the interval that is determined by the next higher part of the datetime value.
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

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
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

### `<uri-prop>`

The `<uri-prop>` element is used for referencing resources with a URI. It must contain at least one `<uri>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<uri>`

The `<uri>` element contains a syntactically valid URI.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
- `comment`: a comment for this specific value (optional)

Example:

```xml
<uri-prop name=":hasURI">
   <uri>http://www.groove-t-gang.ch</uri>
</uri-prop>
```

### `<boolean-prop>`

The `<boolean-prop>` element is used for boolean values. It must contain a `<boolean>` element.

Attributes:

- `name`: name of the property as defined in the ontology (required)

#### `<boolean>`

The `<boolean>` element must contain the string "true" or "false", or the numeral 1 or 0.

Attributes:

- `permissions`: ID or a permission set (optional, but if omitted very restricted default permissions apply)
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
<knora xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       shortcode="0001" default-ontology="anything">
    <permissions id="res-default">
        <allow group="UnknownUser">RV</allow>
        <allow group="KnownUser">V</allow>
        <allow group="Creator">CR</allow>
        <allow group="ProjectAdmin">CR</allow>
        <allow group="anything:Thing searcher">D</allow>
    </permissions>
    <permissions id="res-restricted">
        <allow group="KnownUser">V</allow>
        <allow group="Creator">CR</allow>>
        <allow group="ProjectAdmin">CR</allow>>
        <allow group="anything:Thing searcher">M</allow>>
    </permissions>
    <permissions id="prop-default">
        <allow group="UnknownUser">V</allow>
        <allow group="KnownUser">V</allow>
        <allow group="Creator">CR</allow>
        <allow group="ProjectAdmin">CR</allow>>
        <allow group="anything:Thing searcher">D</allow>>
    </permissions>
    <permissions id="prop-restricted">
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
            <text permissions="prop-default" encoding="xml">This is <em>bold and <strong>string</strong></em> text!</text>
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
        <image>gaga.tif</image>
        <text-prop name=":hasPictureTitle">
            <text permissions="prop-default" encoding="utf8">This is the famous Lena</text>
        </text-prop>
    </resource>

</knora>

```
