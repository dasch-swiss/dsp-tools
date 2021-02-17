[![PyPI version](https://badge.fury.io/py/knora.svg)](https://badge.fury.io/py/knora)

# DSP XML-file format for importing data
The import file is a standard XML file as decribed below.

## Preamble
The import file must start with the standard XML header:
```xml
<?xml version='1.0' encoding='utf-8'?>
```

## &lt;knora&gt;
The `<knora>`-element describes a set of resources that are to be imported. It is the
container for an arbitrary number of `resource` elements and may only
contain resource tags.
The `<knora>`-eelement defines has the following options:

- _xmlns:xsi_: `"http://www.w3.org/2001/XMLSchema-instance"` [required]
- _xsi:schemaLocation_: Path to knora XML schema file for validation [optional]
- _shortcode_: Knora project shortcode, e.g. "0801" [required]
- _ontology_: Name of the ontology [required]

Thus, the `<knora>`-eelment may b used as follows:
```xml
<knora
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="../knora-data-schema.xsd"
 shortcode="0806"
 ontology="webern">
 ...
</knora>
```
The `<knora>`-element can only contain
- `<permissions>`-elements
- `<resource>`-elements

The permissions are implemented for importing data using permission sets. A permission set is
a named element that contains the permissions for selected resources or values.
In order to give a resource a value the permission, the named permission set is referenced.

### &lt;permissions&gt;
The DSP-server provides for each resource and each field of a resource access control. For a more thorough discussion
of the permission and access system of the DSP platform, see
[DSP platform permissions](https://docs.knora.org/02-knora-ontologies/knora-base/#permissions)
The following access rights are defined by the DSP platform which apply to either the resource or field:

- `RV`: _Restricted View permission_: The user sees a somehow restricted view of the element. E.g. in case of a still image
  resource, the image is displeyed at reduced resolution or with a watermark overlay.
- `V`: _View permission_: The user has read access to the element
- `M`: _Modifiy permission_: The user may alter/modify the element, but may not delete it
- `D`: _Delete permission_: The user is allowed to delete the element
- `CR`: _Change Right permission_: The user may change the permission of the element

The user does not hold directly the permissions, but may belong to an arbitrary number of groups which hold the
permissions. By default, the following groups always exist, and each user belongs to at least one of them

- `UnkownUser`: The user is not known to the DSP platform (no login)
- `KnownUser`: The user is known (performed login), but is not member of the project the element belongs to
- `ProjectMember`: The user belongs to the same project as the data element retrieved
- `ProjectAdmin`: The user is project administrator in the project the data element belongs to
- `Creator`: The user is the "owner" of the element, that is the one that created the element
- `SystemAdmin`: System administrator

In addition, more groups with arbitrary names can be created by the project admins. For referencing such a group,
the projectname has to be prepended before the group name separated by a colon, e.g. `knora-py-test:MlsEditors`.

A `<permissions>`-element contains the permissions given to the selected groups and is called a _permission set_. It
contains a mandatory option `id` and must contain at least one `<allow>`-element per user group indicating the group's 
permission. It has the form:
```xml
     <permissions id="res-default">
        <allow group="UnknownUser">RV</allow>
        <allow group="KnownUser">V</allow>
        <allow group="Creator">CR</allow>
        <allow group="ProjectAdmin">CR</allow>
        <allow group="knora-py-test:MlsEditors">D</allow>
    </permissions>
```

_Options_:
- _id_: Unique id (an xs:ID) for the permission set. It is used to reference a permission set.

_Subelements allowed_:
- `<allow>`: defines the permission for one group

#### &lt;allow&gt;
The `<allow>`-element is used to defined the permission for one group. It has the form:
```xml
    <allow group="ProjectAdmin">CR</allow>>
```
The allowed values are
(see [Knora-documentation](https://docs.knora.org/paradox/02-knora-ontologies/knora-base.html#permissions)
for a more detailed description of the Knora permission system):

- _"RV"_: Restricted view: Th associated media is shown in reduced quality.
- _"V"_: View: The user is able to view the data readonly
- _"M"_: Modifiy: The user may modify of a value. The original value will be preserved using the history mchanism.
- _"D"_: Delete: The user is able to mark a resource of a value as deleted.
- _"CR"_: The user is able to change the right of a resource or value

The `group` option is mandatory.

_Options_:

- _group_: Defines the group for the permission. The knora systemgroups as well as project speccific groups are supported.
           A project specific group name has the form `project-shortname:groupnam`. The system groups are:
    - "UnknownUser"
    - "KnownUser"
    - "ProjectMember"
    - "Creator"
    - "ProjectAdmin"
    - "SystemAdmin"
    
_Subelements allowed_: None

Thus a complete _permission_ section may be as follows:
```xml
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
```

### `<resource>`
A `resource`-element contains all necessary information to create a resource. It
has the following options:

_Options_:

- _label_: The label, a human readable, semantical meaningfull short name of the resource [required]
- _restype_: The resource type as defined within the ontology [required]
- _id_: A unique, arbitrary string giving a unique ID to the resource. This ID is only used during the
  import process for referencing this resource from other resources. During the import process, it will be replaced by
  the IRI used internally by Knora. [required]
- _permissions_: a reference to a permission set. These permissions will be applied to the newly created resoource.
  [optional]

```xml
<resource label="EURUS015a"
          restype="Postcard"
          unique_id="238807"
          permissions="res-def-perm">
   ...
</resource>
```

The `<resource>`-element contains for each property class a `property`-element which itself
contains one or several `value`-elements. It _must_ also contain an `<image>`-element if the
resource is a StillImage. The `property`-element must have the option `name` present which
indicates the property class from the project specific ontology where the values belong to.

_name_-option:

- _"name"_: Name of the property as given in the ontology

Example:
```xml
<text-prop name="hasTranslation">
   <text encoding="utf8">Dies ist eine Übersetzung</text>
</text-prop>
```
 
The `<resource>`-element may contain the following tags describing properties (data fields):

- _`<bitstream>`_: In case of the StillImageResource contains the path to the image file.
- _`<text-prop>`_: Contains text values
- _`<color-prop>`_: Contains color values
- _`<date-prop>`_: Contains date values
- _`<decimal-prop>`_: Contains decimal values
- _`<geometry-prop>`_: Contains a JSON geometry definition for a region
- _`<geoname-prop>`_: Contains a geoname.org location code
- _`<list-prop>`_: Contains list elements labels
- _`<iconclass-prop>`_: Contains iconclass.org codes
- _`<integer-prop>`_: Contains integer values
- _`<interval-prop>`_: Contains interval values
- _`<period-prop>`_: Contains time period values
- _`<resptr-prop>`_: Contains links othr resources
- _`<time-prop>`_: Contains time values
- _`<uri-prop>`_: Contains URI values
- _`<boolean-prop>`_: Contains boolean values

#### `<bitstream>`-element
The `<bitstream>`-element contains the path to abitstream object like an image file, a ZIP-file, an audio-file etc.
It must only be used if the resource is a `StillImageRepresentation`, an `AudioRepresentation`, a `DocumentRepresentation` etc.
and must be the first element!

_Options_:
- none

_Note_: There is only _one_ `<bitstream>`-element allowed per Representation!

Example:
```xml
<bitstream>postcards.dir/images/EURUS015a.jpg</bitstream>
```



#### `<text-prop>`-element
The text property element is used to list text values.

The `<text-prop>`-element must contain at least one `<text>`-element. There are several variants of text tags:

_Options_:
- _"name"_: Name of the property as given in the ontology  (required)

##### `<text>`-element
The `<text>`-element has the following options:
- _encoding_: either "utf8" or "hex64" [required]
  - _utf8_: The element describes a simple text without markup. The text is a simple utf-8 string
  - _xml_: The element describes a complex text containing markup. It must be follow the XML-format as defined by the
  [DSP standard mapping](https://docs.knora.org/03-apis/api-v1/xml-to-standoff-mapping/) .
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

###### Simple Text
A complete example for a simple text:
```xml
<text-prop name="hasComment">
   <text encoding="utf8">Probe bei "Wimberger". Lokal in Wien?</text>
</text-prop>
```

###### Text with Markup
Knora-xml-import assumes that for markup-text (standoff-markup) standard mapping for Knora is being used (Custom mapping to
customized standoff tags is not yet implemented!)

E.g. a text containing a link to another resource must have the following form:
```xml
<text permissions="prop-default" encoding="xml" >The <strong>third</strong> object and a <a class="salsah-link" href="IRI:obj_0003:IRI">link</a> to.</text>
```
Please note that the href-option within the anchor tag points to an internal resource of knora
and this has to have the special format "`IRI:`res-id`:IRI`" where res-id is the resource
id defined within the XML import file. A resource already existing in knora can be referenced by
indicating its IRI directly has _href_-option.

Within one text property, multiple simple and complex text values may be mixed.

#### `<color-prop>`-element
The color-prop eelement is used to define a color property.

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<color>`-element
The color-element is used to indicate a color value. The color has to be giiven in
web-notation, that is a "#" followed by 3 or 6 hex numerals.

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

A propery with 2 color valus would be defined as follows:
```xml
<color-prop name="hasColor">
    <color>#00ff66</color>
    <color>#ff00ff</color>
</color-prop>
```

#### `<date-prop>`-eleement
Is used to define knora dates.

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<date>`-element
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
then the precision it _month_, if also the month is omited, the precision is _year_.

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Examples:
```
<date>GREGORIAN:CE:2014-01-31</date>
<date>GREGORIAN:CE:1930-09-02:CE:1930-09-03</date>
```

#### `<decimal-prop>`-element
Properties with decimal values. Contains one or more `<dcimal>`-tags.

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<decimal>`-element
The float element contains a decimal number.

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Example:
```
<float>3.14159</float>
```

#### `<geometry-prop>`-element
Properties which contain a geometric definition for a 2-D region (e.g. on an image). Usually thes
are not created by an import and should be used with caution!

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<geometry>`-element
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
Thus, a <geometry>-element may look like:
```
<geometry>{"status":"active","type"="circle","lineColor"="#ff0000","lineWidth"=2,"points":[{"x":0.5,"y":0.5}],"radius":{"x":0.1,"y":0.0}}</geometry>
```

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

#### `<geoname-prop>`-element
Used for values that contain a [geonames.org](http://geonames.org) location ID

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<geoname>`-element
Contains a valid geonames.org ID.

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Example (City of Wien):
```
<geoname>2761369</geoname>
```

#### `<list-prop>`-element
Entry into a list (list node). List nodes are identified by their `name`-property that was given when creating the list nodes (which must be unique within each list!).

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<list>`-element
References a node in a (pulldown- or hierarchical-) list

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Example:
```
<list>H_4128</list>
```

#### `<iconclass-prop>`-element (_NOT YET IMPLEMENTED_)
Contains the short code of an iconclass entry see [iconclass.org](http://iconclass.org).
For example the code
`92E112`stands for `(story of) Aurora (Eos); 'Aurora' (Ripa) - infancy, upbringing
Aurora · Ripa · air · ancient history · child · classical antiquity · goddess · gods · heaven · history · infancy · mythology · sky · upbringing · youth`

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<iconclass>`-element (_NOT YET IMPLEMENTED_)
References an [iconclass.org](https://iconclass.org) 

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Usage:
```
<iconclass>92E112</iconclass>
```

#### `<integer-prop>`-element
Contains integer values

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<integer>`-element

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Usage:
```
<integer>4711</integer>
```

#### `<interval-prop>`-element
An interval defined a time period with a start and an end

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<interval>`-element
The interval-tag value has the following form or two decimals separated by a ":".

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Example:
```
<interval>1.5:3.12</interval>
```

#### `<resptr-prop>`-element
A link to another resource within Knora

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<resptr>`-element
A value containing the XML-internal ID of the resource.

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Example:

If there is a resource deefined as
```
<resource label="EURUS015a" restype="Postcard" unique_id="238807">
…
</resource
```
it can be referenced as
```
<resptr>238807</resptr>
```

#### `<time-prop>`-element
A time property

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<time>`-element
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

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Example:

The following form indicates noon on 10 October 2009, Eastern Standard Time in the United States:
```
<time>2009-10-10T12:00:00-05:00</time>
<time>2019-10-23T13.45:12Z</time>
```

#### `<uri-prop>`-element
A property containing an valid URI

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<uri>`-element
Contains a syntactically valid URI.

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Example:
```
<uri>http://www.groove-t-gang.ch</ur>
```

#### `<boolean-prop`>-element
A property containing boolean values

_Options_:
- _"name"_: Name of the property as given in the ontology (required)

##### `<boolean>`-element
Must contain the string "true" or "false", or the numeral "1" or "0"

_Options_:
- _permissions_: ID or a permission set. Optional, but if omitted very restricted default permissions apply!
- _comment_: A comment to this specific value.

Example:

```
<boolean>true</boolean>
<boolean>0</boolean>
```

## Complete example

```xml
<?xml version='1.0' encoding='utf-8'?>
<knora xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       shortcode="0001" default-ontology="anything">
    <!-- permissions: see https://docs.knora.org/03-apis/api-v2/reading-user-permissions/ -->
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
        <!-- -->
        <list-prop list="treelistroot" name=":hasListItem">
            <list permissions="prop-default">Tree list node 02</list>
        </list-prop>
        <list-prop list="treelistroot" name=":hasOtherListItem">
            <list permissions="prop-default">Tree list node 03</list>
        </list-prop>
        <text-prop name=":hasRichtext">
            <text permissions="prop-default" encoding="xml" >The <strong>third</strong> object and a <a class="salsah-link" href="IRI:obj_0003:IRI">link</a> to.</text>
        </text-prop>
        <!-- -->
        <text-prop name=":hasRichtext">
            <text permissions="prop-default" encoding="xml" >The <strong>third</strong> object and a <a class="salsah-link" href="IRI:obj_0003:IRI">link</a> to.</text>
        </text-prop>
        <!-- -->
        <text-prop name=":hasText">
            <text permissions="prop-default" encoding="utf8">Dies ist ein einfacher Text ohne Markup</text>
            <text permissions="prop-restricted" encoding="utf8">Nochmals ein einfacher Text</text>
        </text-prop>
        <date-prop name=":hasDate">
            <date permissions="prop-default" >JULIAN:CE:1401-05-17:CE:1402-01</date>
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
         <!-- -->
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
            <date permissions="prop-default" >1888</date>
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
            <date permissions="prop-default" >1888</date>
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
