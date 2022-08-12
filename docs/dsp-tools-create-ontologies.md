# Ontologies

An ontology is a formal representation of a set of terminologies which finally represent real world objects.
Dependencies, attributes and relations of and between the individual components of the set are recorded in a logical,
formal language. In contrast to a taxonomy, which defines a mere hierarchical structure within a range of terms, an
ontology is much more a network of information of logical dependencies of term elements. Or, in other words, an ontology
defines a strict, formal "data model" for real world _concepts_ such as "Person", "Work", "Artist" etc.

A full-fledged ontology thus has to offer at least *two* things: a set of _concepts_ or terms (called _resources_,
actually "resource classes") that represent _concepts_ of real world objects, as well as attributes or _properties_
describing these resources. These properties are linked either to a final value or may define a relationship to another
resource. Let's assume that we define a resource called "Person" and two properties called "hasBirthday" and "hasParent"
. For a specific incarnation of a
"Person" (we call this an _instance_), "hasBirthday" will have a final value such as "1960-05-21", whereas
"hasParent" will link to another instance of a "Person".

Within DSP, properties may be re-used for different resources. E.g. a property "description" may be used for a resource
called "image" as well as "movie". Therefore, the list of properties is separated from the list of resources. The
properties are assigned to the resources by defining "_cardinalities_". A cardinality indicates if a property is
mandatory or can be omitted (e.g. if unknown), and if a property may be used several times on the same instance of a
resource or not. The cardinality definitions are explained [further below](#cardinalities).

Example of an `ontologies` object:

```json
{
  "ontologies": [
    {
      "name": "seworon",
      "label": "Secrets of the World Ontology",
      "properties": [
        ...
      ],
      "resources": [
        ...
      ]
    },
    {
      ...
    },
    {
      ...
    }
  ]
}
```




## Ontologies Object in Detail

The following properties can occur within each object in `ontologies`.



### Name

(required)

`"name": "<string>"`

The ontology's (short) name should be in the form of a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This
means a string without blanks or special characters but `-` and `_` are allowed (although not as first character).



### Label

(required)

`"label": "<string>"`

A string that provides the full name of the ontology.



### Properties

(required)

`"properties": [<property-definition>, <property-definition>, ...]`

A `properties` array contains all properties used to describe resources in the ontology. A property has to be of a
certain data type. It is not possible to create a custom data type.

The following fields are mandatory:

- `name`
- `labels`
- `super`
- `object`
- `gui_element`

The following fields are optional:

- `comments` 
- `subject`
- `gui_attributes`

A detailed description of `properties` can be found [below](#properties-object-in-detail).



### Resources

(required)

The resource classes are the primary entities of the data model. They are the actual objects inside a terminology space.
A resource class can be seen as a template for the representation of a real object that is represented in the DSP. A
resource class defines properties (_data fields_). For each of these properties a data type as well as the cardinality
has to be provided.

`"resources": [<resource-definition>, <resource-definition>, ...]`

A resource object needs to have the following fields:

- `name`
- `labels`
- `super`
- `cardinalities`

The following field is optional:

- `comments` 

A detailed description of `resources` can be found [below](#properties-object-in-detail).




## Properties Object in Detail



### Name

(required)

`"name": "<string>"`

A name for the property, e.g. "pageOf", "hasBirthdate", "createdBy". It should be in the form of
a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This means a string without blanks or special characters
but `-` and `_` are allowed (although not as first character).

By convention, property names start with a lower case letter.



### Labels

(required)

`"labels": {"<language>": "<string>", ...}`

Collection of `labels` for the property as strings with language tag (currently "en", "de", "fr", "it",
and "rm" are supported).



### Comments

(optional)

`"comments": { "<lang>": "<comment>", "<lang>": "<comment>", ... }`

Comments with language tags. Currently, "de", "en", "fr", "it", and "rm" are supported. The `comments` element is optional.



### Super

(required)

`"super": ["<super-property>", "<super-property>, ...]`

A property is always derived from at least one other property. There are three groups of properties that can serve as 
super-property:

 - DSP base properties
 - properties defined in external ontologies
 - properties defined in the project ontology itself

The syntax how to refer to these different groups of properties is described [here](#referencing-ontologies).

The following DSP base properties are available:

- `hasValue`: This is the most general case, to be used in all cases when your property is none of the special cases below.
- `hasLinkTo`: a link to another resource
- `isPartOf`: A special variant of `hasLinkTo`. It says that an instance of the given resource class is an integral part
  of another resource class. E.g. a "page" is part of a "book".
- `seqnum`: An integer that is used to define a sequence number in an ordered set of instances, e.g. the ordering of the
  pages in a book. A resource that has a property derived from `seqnum` must also have a property derived from `isPartOf`.
- `hasColor`: Defines a color value.  
- `hasComment`: Defines a standard comment.
- `isSequenceOf`: A special variant of `hasLinkTo`. It says that an instance of the given resource class is a section 
  of an audio/video resource.
- `hasSequenceBounds`: This base property is used together with `isSequenceOf`. It denotes a time interval of an audio/
  video resource.

Example of a `properties` object:

```json
{
  "properties": [
    {
      "name": "id",
      "subject": ":School",
      "object": "TextValue",
      "super": [
          "hasValue"
      ],
      "labels": {
        "en": "School ID",
        "de": "ID der Schule",
        "fr": "ID de l'école"
      },
      "gui_element": "SimpleText",
      "gui_attributes": {
        "size": 32,
        "maxlength": 128
      }
    },
    {
      "name": "name",
      "subject": ":School",
      "object": "TextValue",
      "super": [
          "hasValue"
      ],
      "labels": {
        "en": "Name of the school",
        "de": "Name der Schule",
        "fr": "Nom de l'école"
      },
      "gui_element": "SimpleText",
      "gui_attributes": {
        "size": 32,
        "maxlength": 128
      }
    }
  ]
}
```



### Subject

(optional)

`"subject": "<resource-class>"`

The `subject` defines the resource class the property can be used on. It has to be provided as prefixed name of the 
resource class (see [below](#referencing-ontologies) on how prefixed names are used).



### Object / gui_element / gui_attributes

These three are related as follows:

 - `object` (required) is used to define the data type of the value that the property will store. 
 - `gui_element` (required) depends on the value of `object`.
 - `gui_attributes` (optional) depends on the value of `gui_element`.

The following `object`s are available, and will be discussed below, in this order:

- `BooleanValue`
- `ColorValue`
- `DateValue`
- `DecimalValue`
- `GeonameValue`
- `IntervalValue`
- `IntValue`
- `ListValue`
- `TextValue`
- `TimeValue`
- `UriValue`
- `Representation`
- in case of the supers `hasLinkTo` or `isPartOf`: any resource class


#### BooleanValue

`"object": "BooleanValue"`

Represents a Boolean ("true" or "false).

*gui-elements / gui_attributes*:

- `Checkbox`: A GUI element for _BooleanValue_.
    - _gui_attributes_: No attributes

*Example:*

```json
{
  "name": "hasBoolean",
  "super": [
    "hasValue"
  ],
  "object": "BooleanValue",
  "labels": {
    "en": "Boolean value"
  },
  "gui_element": "Checkbox"
}
```


#### ColorValue

`"object": "ColorValue"`

A string representation of the color in the hexadecimal form e.g. "#ff8000".

*gui-elements / gui_attributes*:

- `Colorpicker`: The only GUI element for _ColorValue_. It's used to choose a color.
    - _gui_attributes_:
        - `ncolors=integer` (optional): Number of colors the color picker should present.

*Example:*

```json
{
  "name": "hasColor",
  "super": [
    "hasColor"
  ],
  "object": "ColorValue",
  "labels": {
    "en": "Color"
  },
  "gui_element": "Colorpicker"
}
```


#### DateValue

`object": "DateValue"`  
Represents a date. It's a string with the format `calendar:start:end`

Please note that the DateValue is an extremely flexible data type. It can represent an exact date or a date with a given
uncertainty, and the date can be given in several calendars (currently the Gregorian and the Julian calendars are
supported, with the Jewish and Islamic coming soon). Internally, a date is always represented as a start and end date.
If start and end date match, it's an exact date. A value like "1893" will automatically be expanded to a range from
January 1st 1893 to December 31st 1893.

- _calendar_ is either _GREGORIAN_ or _JULIAN_
- _start_ has the form _yyyy_-_mm_-_dd_. If only the year is given, the precision is to the year. If only the year and
  month is given, the precision is to the month.
- _end_ is optional if the date represents a clearly defined period or uncertainty.

In total, a DateValue has the following form: "GREGORIAN:1925:1927-03-22"
which means anytime in between 1925 and the 22nd March 1927.

*gui_elements / gui_attributes*:

- `Date`: The only GUI element for _DateValue_. A date picker gui.
   - _gui_attributes_: No attributes

*Example:*

```json
{
  "name": "hasDate",
  "super": [
    "hasValue"
  ],
  "object": "DateValue",
  "labels": {
    "en": "Date"
  },
  "gui_element": "Date"
}
```


#### DecimalValue

`"object": "DecimalValue"`

A number with decimal point.

*gui-elements / gui_attributes*:

- `Slider`: A GUI element for _DecimalValue_. Provides a slider to select a decimal value.
    - _gui_attributes_:
        - `max=decimal` (mandatory): maximal value
        - `min=decimal` (mandatory): minimal value
- `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
  "maxlength=integer" and "size=integer" are optional.
    - _gui_attributes_:
        - `maxlength=integer` (optional): maximum number of characters accepted
        - `size=integer` (optional): size of the input field

*Example:*

```json
{
  "name": "hasDecimal",
  "super": [
    "hasValue"
  ],
  "object": "DecimalValue",
  "labels": {
    "en": "Decimal number"
  },
  "gui_element": "SimpleText",
  "gui_attributes": {
    "maxlength": 255,
    "size": 80
  }
}
```


#### GeonameValue

Represents a location ID in geonames.org. DSP uses identifiers provided by
[geonames.org](https://geonames.orgs) to identify geographical locations.

*gui-elements / gui_attributes*:

- `Geonames`: The only valid GUI element for _GeonameValue_. It interfaces are with geonames.org and it allows to select
  a location.
    - _gui_attributes_: No attributes

*Example:*

```json
{
  "name": "hasGeoname",
  "super": [
    "hasValue"
  ],
  "object": "GeonameValue",
  "labels": {
    "en": "Geoname"
  },
  "gui_element": "Geonames"
}
```


#### IntervalValue

`"object": "IntervalValue"`

This `object` belongs to the DSP base property ("`super`") `hasSequenceBounds`. It represents a time interval of an 
audio or video. It can be used together with an `isSequenceOf` property on a resource that represents the sequence. The 
`isSequenceOf` would then point to the audio/video resource, and the `hasSequenceBounds` would be the time interval of 
the sequence.

See the [`isSequenceOf` property](#issequenceof-property) for more detailed explanations.

*gui-elements / gui_attributes*:

- `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
  "maxlength=integer" and "size=integer" are optional.
    - _gui_attributes_:
        - `maxlength=integer` (optional): The maximum number of characters accepted
        - `size=integer` (optional): The size of the input field
- `Interval`: Two spin boxes, one for each decimal
    - _gui_attributes_: No attributes

*Example:*

```json
{
  "name": "hasBounds",
  "super": [
    "hasSequenceBounds"
  ],
  "subject": ":AudioSequence",
  "object": "IntervalValue",
  "labels": {
    "en": "Interval defining the start and end point of a sequence of an audio or video file"
  },
  "gui_element": "Interval"
}
```


#### IntValue

`"object": "IntValue"`

Represents an integer value.

*gui-elements / gui_attributes*:

- `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
  "maxlength=integer" and "size=integer" are optional.
    - _gui_attributes_:
        - `maxlength=integer` (optional): The maximum number of characters accepted
        - `size=integer` (optional): The size of the input field
- `Spinbox`: A GUI element for _IntegerValue_. A text field with and "up"- and "down"-button for increment/decrement.
  The attributes "max=decimal" and "min=decimal" are optional.
    - _gui_attributes_:
        - `max=decimal` (optional): Maximal value
        - `min=decimal` (optional): Minimal value

*Example:*

```json
{
  "name": "hasInteger",
  "super": [
    "hasValue"
  ],
  "object": "IntValue",
  "labels": {
    "en": "Integer"
  },
  "gui_element": "Spinbox",
  "gui_attributes": {
    "max": 10.0,
    "min": 0.0
  }
}
```


#### ListValue

`"object": "ListValue"`

Represents a node of a (possibly hierarchical) list

*gui-elements / gui_attributes*:

- `Radio`: A GUI element for _ListValue_. A set of radio buttons. This works only with flat lists.
    - _gui_attributes_:
        - `hlist=<list-name>` (required): The reference of a [list](./dsp-tools-create.md#lists) root node
- `List`: A GUI element for _ListValue_. A list of values to select one from. This GUI element should be chosen for
  hierarchical lists or flat lists that could be expanded to hierarchical lists in the future.
    - _gui_attributes_:
        - `hlist=<list-name>` (required): The reference of a [list](./dsp-tools-create.md#lists) root node

*Example:*

```json
{
  "name": "hasListItem",
  "super": [
    "hasValue"
  ],
  "object": "ListValue",
  "labels": {
    "en": "List element"
  },
  "gui_element": "List",
  "gui_attributes": {
    "hlist": "treelistroot"
  }
}
```


#### TextValue

`"object": "TextValue"`

Represents a text that may contain standoff markup.

*gui_elements / gui_attributes*:

- `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes are:
    - _gui_attributes_:
        - `maxlength=integer` (optional): maximal length (number of characters accepted)
        - `size=integer` (optional): size (width) of widget
- `Textarea`: A GUI element for _TextValue_. Presents a multiline text entry box. The optional attributes are:
    - _gui_attributes_:
        - `cols=integer` (optional): number of columns of the textarea
        - `rows=integer` (optional): number of rows of the textarea
        - `width=percent` (optional): width of the textarea on screen
        - `wrap=soft|hard` (optional): wrapping of text
- `Richtext`: A GUI element for _TextValue_. Provides a richtext editor.
    - _gui_attributes_: No attributes

*Example:*

```json
{
  "name": "hasPictureTitle",
  "super": [
    "hasValue"
  ],
  "object": "TextValue",
  "labels": {
    "en": "Title"
  },
  "gui_element": "SimpleText",
  "gui_attributes": {
    "maxlength": 255,
    "size": 80
  }
}
```


#### TimeValue

`"object": "TimeValue"`

A time value represents a precise moment in time in the Gregorian calendar. Since nanosecond precision can be included, it is suitable for use as a timestamp.

*gui-elements / gui_attributes*:

- `TimeStamp`: A GUI element for _TimeValue_ which contains a date picker and a time picker.
  - _gui_attributes_: No attributes

*Example:*

```json
{
  "name": "hasTime",
  "super": [
    "hasValue"
  ],
  "object": "TimeValue",
  "labels": {
    "en": "Time"
  },
  "gui_element": "TimeStamp"
}
```


#### UriValue

`"object": "UriValue"`

Represents an URI

*gui-elements / gui_attributes*:

- `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
  "maxlength=integer" and "size=integer" are optional.
    - _gui_attributes_:
        - `maxlength=integer` (optional): The maximum number of characters accepted
        - `size=integer` (optional): The size of the input field

*Example:*

```json
{
  "name": "hasUri",
  "super": [
    "hasValue"
  ],
  "object": "UriValue",
  "labels": {
    "en": "URI"
  },
  "gui_element": "SimpleText",
  "gui_attributes": {
    "maxlength": 255,
    "size": 80
  }
}
```


#### Representation

`"object": "Representation"`

A property pointing to a `knora-base:Representation`. Has to be used in combination with `"super": ["hasRepresentation"]`. A resource having this generic property `hasRepresentation` can point to any type of Representation, be it a `StillImageRepresentation`, an `AudioRepresentation`, etc.

*gui-elements / gui_attributes*:

- `Searchbox`: Allows searching resources that have super class `Representation` by entering at least 3 characters into
  a searchbox.
    - _gui_attributes_:
        - `numprops=integer` (optional): While dynamically displaying the search result, the number of properties that
          should be displayed.

*Example:*

```json
{
    "name": "hasRep",
    "super": [
        "hasRepresentation"
    ],
    "object": "Representation",
    "labels": {
        "en": "Represented by"
    },
        "gui_element": "Searchbox"
    }
```


#### hasLinkTo Property

`"object": "<resource-name>"`

Link properties do not follow the pattern of the previous data types, because they do not connect to a final value but 
to an existing resource. Thus, the `object` denominates the resource class the link will point to. There are different 
groups of resource classes that can be the object:

 - project resources: a resource class defined in the present ontology itself
 - external resources: a resource class defined in another ontology
 - DSP base resources:
     - `Resource`: the most generic one, can point to any resource class, be it a DSP base resource, a project resource, 
     or an external resource. `Resource` is at the very top of the inheritance hierarchy.
     - `Region`: a region in an image
     - `StillImageRepresentation`, `MovingImageRepresentation`, `TextRepresentation`, `AudioRepresentation`, 
       `DDDRepresentation`, `DocumentRepresentation`, or `ArchiveRepresentation`
     - `Representation`: any type of the just mentioned representations. `Representation` is the parent class of them.

The syntax how to refer to these different groups of resources is described [here](#referencing-ontologies).

When defining a link property, its "super" element has to be `hasLinkTo` or derived from `hasLinkTo`.

*gui-elements/gui_attributes*:

- `Searchbox`: The only GUI element for _hasLinkTo_. Allows searching resources by entering the target resource name.
    - _gui_attributes_:
        - `numprops=integer` (optional): Number of search results to be displayed

*Example:*

```json
{
  "name": "hasOtherThing",
  "super": [
    "hasLinkTo"
  ],
  "object": ":Thing",
  "labels": "Another thing",
  "gui_element": "Searchbox"
}
```


#### isPartOf Property
A special case of linked resources are resources in a part-whole relation, i.e. resources that are composed of 
other resources. A `isPartOf` property has to be added to the resource that is part of another resource. In case of 
resources that are of type `StillImageRepresentation`, an additional property derived from `seqnum` with object `IntValue` 
is required. When defined, a client is able to leaf through the parts of a compound object, p.ex. to leaf through pages of a book.

*gui-elements/gui_attributes*:

- `Searchbox`: The only GUI element for _isPartOf_. Allows searching resources by entering the target resource name.
    - _gui_attributes_:
        - `numprops=integer` (optional): Number of search results to be displayed

*Example:*

```json
{
  "name": "partOfBook",
  "super": [
    "isPartOf"
  ],
  "object": ":Book",
  "labels": {
      "en": "is part of"
  },
  "gui_element": "Searchbox"
},
{
  "name": "hasPageNumber",
  "super": [
    "seqnum"
  ],
  "object": "IntValue",
  "labels": {
      "en": "has page number"
  },
  "gui_element": "Spinbox"
}
```


#### hasComment property

`"object": "TextValue"`

This property is actually very similar to a simple text field. 

*Example:*

```json
{
    "name": "hasComment",
    "super": [
      "hasComment"
    ],
    "object": "TextValue",
    "labels": {
      "de": "Kommentar",
      "en": "Comment",
      "fr": "Commentaire"
    },
    "gui_element": "SimpleText"
}
```


#### isSequenceOf property

`"object": (AudioRepresentation/MovingImageRepresentation or a subclass of one of them)`

This property can be used, together with a `hasSequenceBounds` property, on a resource representing a sequence of an
audio/video resource. The `isSequenceOf` would then point to the audio/video resource, and the `hasSequenceBounds` 
would be the time interval of the sequence.

The DSP base properties `isSequenceOf` and `hasSequenceBounds` can be used to derive a custom property from them, or 
they can be userd directly as cardinalities in a resource. The example belows shows both possibilities.

*gui-elements/gui_attributes*:

- `Searchbox`: The only GUI element for _isSequenceOf_. Allows searching resources by entering the target resource name.
    - _gui_attributes_:
        - `numprops=integer` (optional): Number of search results to be displayed

*Example:*

```json
"properties": [
    {
        "name": "sequenceOfAudio",
        "super": [
            "isSequenceOf"
        ],
        "subject": ":AudioSequence",
        "object": ":Audio",
        "labels": {
            "en": "is sequence of"
        },
        "gui_element": "Searchbox"
    },
    {
        "name": "hasBounds",
        "super": [
            "hasSequenceBounds"
        ],
        "subject": ":AudioSequence",
        "object": "IntervalValue",
        "labels": {
            "en": "Interval defining the start and end point of a sequence of an audio or video file"
        },
        "gui_element": "Interval"
    }
],
"resources": [
    {
        "name": "AudioSequence",
        "labels": {
            "en": "Sequence of an audio resource that uses properties derived from 'isSequenceOf' and 'hasSequenceBounds'"
        },
        "super": "Resource",
        "cardinalities": [
            {
                "propname": ":sequenceOfAudio",
                "cardinality": "1"
            },
            {
                "propname": ":hasBounds",
                "cardinality": "1"
            }
        ]
    },
    {
        "name": "MinimalisticAudioSequence",
        "labels": {
            "en": "Sequence of an audio resource that uses 'isSequenceOf' and 'hasSequenceBounds' directly"
        },
        "super": "Resource",
        "cardinalities": [
            {
                "propname": "isSequenceOf",
                "cardinality": "1"
            },
            {
                "propname": "hasSequenceBounds",
                "cardinality": "1"
            }
        ]
    }
```




## Resources Object in Detail

### Name

(required)

`"name": "<string>"`

A name for the resource, e.g. "Book", "Manuscript", "Person". It should be in the form of
a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This means a string without blanks or special characters
but `-` and `_` are allowed (although not as first character).

By convention, resource names start with a upper case letter.



### Labels

(required)

`"labels": {"<language>": "<string>", ...}`

Collection of `labels` for the resource as strings with language tag (currently "en", "de", "fr", "it", 
and "rm" are supported).



### Super

(required)

`"super": ["<super-resource>", "<super-resource>", ...]`

A resource is always derived from at least one other resource. There are three groups of resources that can serve 
as super-resource:

 - DSP base resources
 - resources defined in external ontologies
 - resources defined in the project ontology itself

The syntax how to refer to these different groups of resources is described [here](#referencing-ontologies).

The following base resources can be used as super-resource:

- `Resource`: A generic resource representing an item from the real world. This is the most general case, to be 
used in all cases when your resource is none of the special cases below.
- `StillImageRepresentation`: A resource representing an image
- `TextRepresentation`: A resource representing a text
- `AudioRepresentation`: A resource representing an audio file
- `DDDRepresentation`: A resource representing a 3-D representation (not yet implemented)
- `DocumentRepresentation`: A resource representing an opaque document (e.g. a PDF)
- `MovingImageRepresentation`: A resource representing a video
- `ArchiveRepresentation`: A resource representing an archive file (e.g. ZIP)



### Cardinalities

(required)

`"cardinalities": [...]`

An array that contains information about the relation between resources and properties. It tells what properties a
resource can have as well as how many times the relation is established.

- `cardinalities`: Array of references to the properties that the resource may hold including the cardinality. A
  cardinality has the following properties:
    - `propname` (1): The name of the property. If it's used in the form `:my_propname`, the current ontology is referenced.
      Otherwise, the prefix of the ontology the property is part of has to be used.
    - `gui_order` (0-1): An integer number which will help the GUI to display the properties in the desired order (optional)
    - `cardinality` (1): Indicates how often a given property may occur. The possible values are:
        - `"1"`: exactly once (mandatory one value and only one)
        - `"0-1"`: The value may be omitted, but can occur only once.
        - `"1-n"`: At least one value must be present, but multiple values may be present.
        - `"0-n"`: The value may be omitted, but may also occur multiple times.



### Comments

(optional)

`"comments": { "<lang>": "<comment>", "<lang>": "<comment>", ... }`

Comments with language tags. Currently, "de", "en", "fr", "it", and "rm" are supported. The `comments` element is optional.

Example for a resource definition:

```json
{
  "resources": [
    {
      "name": "Schule",
      "labels": {
        "de": "Schule",
        "en": "School",
        "fr": "Ecole",
        "it": "Scuola"
      },
      "super": "Resource",
      "comments": {
        "de": "Ein Kommentar",
        "en": "A comment",
        "fr": "Une commentaire",
        "it": "Un commento"
      },
      "cardinalities": [
        {
          "propname": ":schulcode",
          "gui_order": 1,
          "cardinality": "1"
        },
        {
          "propname": ":schulname",
          "gui_order": 2,
          "cardinality": "1"
        },
        {
          "propname": ":bildungsgang",
          "gui_order": 3,
          "cardinality": "1"
        }
      ]
    }
  ]
}
```




## Referencing Ontologies

For several fields, such as `super` in both `resources` and `properties` or `propname` in `cardinalities`
it is necessary to reference entities that are defined elsewhere. The following cases are possible:

- DSP API internals: They are referenced as such and do not have a leading colon.  
  E.g. `Resource`, `DocumentRepresentation` or `hasValue`
- An external ontology: The ontology must be defined in the [prefixes](dsp-tools-create.md#prefixes-object) section.
  The prefix can then be used for referencing the ontology.  
  E.g. `foaf:familyName` or `sdo:Organization`
- The current ontology: Within an ontology definition, references can be made by prepending a colon without a prefix.  
  E.g. `:hasName`
  Optionally, an explicit prefix can be used. In this case the ontology must be added to the
  [prefixes](dsp-tools-create.md#prefixes-object) section and the prefix must be identical to the ontology's `name`.  
- A different ontology defined in the same file: Within one data model file, multiple ontologies can be defined.
  These will be created in the exact order they appear in the `ontologies` array. Once an ontology has been created,
  it can be referenced by the following ontologies by its name, e.g. `first-onto:hasName`. It is not necessary to add 
  `first-onto` to the prefixes.




## DSP base resources / base properties to be used directly in the XML file
There is a number of DSP base resources that must not be subclassed in a project ontology. They are directly available 
in the XML data file:

- `Annotation` is an annotation to another resource of any class. It can be used in the XML file with the 
  [&lt;annotation&gt; tag](dsp-tools-xmlupload.md#annotation). It automatically has the following predefined properties:
    - `hasComment` (1-n)
    - `isAnnotationOf` (1)
- `LinkObj` is a resource linking together several other resources of different classes. It can be used in the XML file 
  with the [&lt;link&gt; tag](dsp-tools-xmlupload.md#link). It automatically has the following predefined properties:
    - `hasComment` (1-n)
    - `hasLinkTo` (1-n)
- A `Region` resource defines a region of interest (ROI) in an image. It can be used in the XML file with the 
  [&lt;region&gt; tag](dsp-tools-xmlupload.md#region). It automatically has the following predefined properties:
    - `hasColor` (1)
    - `isRegionOf` (1)
    - `hasGeometry` (1)
    - `hasComment` (1-n)

There are some DSP base properties that are used directly in the above resource classes. Some of them can also be 
subclassed and used in a resource class.

- `hasLinkTo`: a link to another resource
    - can be subclassed ([hasLinkTo Property](#haslinkto-property))
    - can be used directly in the XML data file in the [&lt;link&gt; tag](dsp-tools-xmlupload.md#link)
- `hasColor`: Defines a color value. 
    - can be subclassed ([ColorValue](#colorvalue))
    - can be used directly in the XML data file in the [&lt;region&gt; tag](dsp-tools-xmlupload.md#region)
- `hasComment`: Defines a standard comment. 
    - can be subclassed ([hasComment Property](#hascomment-property))
    - can be used directly in the XML data file in the [&lt;region&gt; tag](dsp-tools-xmlupload.md#region) or 
      [&lt;link&gt; tag](dsp-tools-xmlupload.md#link)
- `hasGeometry`: Defines a geometry value (a JSON describing a polygon, circle or rectangle). 
    - must be used directly in the XML data file in the [&lt;region&gt; tag](dsp-tools-xmlupload.md#region)
- `isRegionOf`: A special variant of `hasLinkTo`. It means that the given resource class is a region of interest in an image. 
    - must be used directly in the XML data file in the [&lt;region&gt; tag](dsp-tools-xmlupload.md#region)
- `isAnnotationOf`: A special variant of `hasLinkTo`. It means that the given resource class is an annotation to another
  resource class. 
    - must be used directly in the XML data file in the [&lt;annotation&gt; tag](dsp-tools-xmlupload.md#annotation)
