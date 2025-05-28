[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# The `ontologies` Array of a JSON Project

An ontology is a formal representation of a set of terms which represent real world objects.
Dependencies, attributes and relations of and between the individual components of the set are recorded in a logical,
formal language. In contrast to a taxonomy, which defines a mere hierarchical structure within a range of terms, an
ontology is much more a network of information of logical dependencies of term elements. Or, in other words, an ontology
defines a strict, formal "data model" for real world concepts such as "Person", "Work", "Artist" etc.

An ontology thus has to offer at least two things: 

- a set of concepts or terms (called **resource classes**) that represent concepts of real world objects
- **properties** describing these resources. These properties are linked either to a final value or may define a 
  relationship to another resource. 

Let's assume that we define a resource class called `Person` and two properties called `hasBirthday` and `hasParent`. 
For a specific **instance** of a `Person`, `hasBirthday` will have a final value such as "1960-05-21", whereas
`hasParent` will link to another instance of a `Person`.

Within DSP, properties may be re-used for different resources. E.g. a property "description" may be used for a resource
called "image" as well as "movie". Therefore, the list of properties is separated from the list of resources. The
properties are assigned to the resources by defining "**cardinalities**". A cardinality indicates if a property is
mandatory or can be omitted (e.g. if unknown), and if a property may be used several times on the same instance of a
resource or not. The cardinality definitions are explained [further below](#resource-cardinalities).



## The `ontology` Object

Example of an ontology object:

```json
{
  "name": "seworon",
  "label": "Secrets of the World Ontology",
  "comment": "This is an example ontology",
  "properties": [
    ...
  ],
  "resources": [
    ...
  ]
}
```



### Ontology: `name`

(required)

`"name": "<string>"`

The ontology's (short) name should be in the form of a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This
means a string without blanks or special characters but `-` and `_` are allowed (although not as first character).



### Ontology: `label`

(required)

`"label": "<string>"`

A string that provides the full name of the ontology.



### Ontology: `comment`

(optional)

`"comment": "<string>"`

A string that provides a comment to the ontology.



### Ontology: `properties`

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

A detailed description of `properties` can be found [below](#the-property-object).



### Ontology: `resources`

(required)

The resource classes are the primary entities of the data model. They are the actual objects inside a terminology space.
A resource class can be seen as a template for the representation of a real object that is represented in the DSP. A
resource class defines properties (*data fields*). For each of these properties a data type as well as the cardinality
has to be provided.

`"resources": [<resource-definition>, <resource-definition>, ...]`

A resource object needs to have the following fields:

- `name`
- `labels`
- `super`
- `cardinalities`*

The following field is optional:

- `comments` 

A detailed description of `resources` can be found [below](#the-resource-object).

(*It is technically possible to have a resource without cardinalities,
but in most cases it doesn't make sense to omit them.)



## The `property` Object

```json
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
}
```



### Property: `name`

(required)

`"name": "<string>"`

A name for the property, e.g. `pageOf`, `hasBirthdate`, `createdBy`. It should be in the form of
a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This means a string without blanks or special characters
but `-` and `_` are allowed (although not as first character).

By convention, property names start with a lower case letter.



### Property: `label`

(required)

`"labels": {"<language>": "<string>", ...}`

Collection of `labels` for the property as strings with language tag 
(currently, `en`, `de`, `fr`, `it`, and `rm` are supported).



### Property: `comments`

(optional)

`"comments": { "<lang>": "<comment>", "<lang>": "<comment>", ... }`

Comments with language tags. Currently, `de`, `en`, `fr`, `it`, and `rm` are supported. 
The `comments` element is optional.



### Property: `super`

(required)

`"super": ["<super-property>", "<super-property>, ...]`

A property is always derived from at least one other property. There are three groups of properties that can serve as 
super-property:

- DSP base properties
- properties defined in external ontologies
- properties defined in the project ontology itself

The syntax how to refer to these different groups of properties is described 
[here](./caveats.md#referencing-ontologies).

The following DSP base properties are available:

- `hasValue`: This is the most general case, 
  to be used in all cases when your property is none of the special cases below.
- `hasLinkTo`: a link to another resource
- `isPartOf`: A special variant of `hasLinkTo`. It says that an instance of the given resource class is an integral part
  of another resource class. E.g. a "page" is part of a "book".
- `seqnum`: An integer that is used to define a sequence number in an ordered set of instances, 
  e.g. the ordering of the pages in a book. 
  A resource that has a property derived from `seqnum` must also have a property derived from `isPartOf`.
- `hasColor`: Defines a color value.  
- `hasComment`: Defines a standard comment.



### Property: `subject`

(optional)

`"subject": "<resource-class>"`

The `subject` defines the resource class the property can be used on. It has to be provided as prefixed name of the 
resource class (see [here](./caveats.md#referencing-ontologies) on how prefixed names are used).



### Property: `object`, `gui_element`, `gui_attributes`

These three are related as follows:

- `object` (required) is used to define the data type of the value that the property will store. 
- `gui_element` (required) depends on the value of `object`.
- `gui_attributes` (optional) depends on the value of `gui_element`.

#### Overview

| DSP base property (`super`)           | `object`                                                           | `gui_element`                          |
| ------------------------------------- | ------------------------------------------------------------------ | -------------------------------------- |
| hasValue                              | BooleanValue                                                       | Checkbox                               |
| hasColor                              | ColorValue                                                         | Colorpicker                            |
| hasValue                              | DateValue                                                          | Date                                   |
| hasValue                              | DecimalValue                                                       | Spinbox, <br>SimpleText                |
| hasValue                              | GeonameValue                                                       | Geonames                               |
| hasValue                              | IntValue                                                           | Spinbox, <br>SimpleText                |
| hasValue                              | ListValue                                                          | List                                   |
| hasValue                              | TextValue                                                          | SimpleText, <br>Textarea, <br>Richtext |
| hasComment                            | TextValue                                                          | Richtext                               |
| hasValue                              | TimeValue                                                          | TimeStamp                              |
| hasValue                              | UriValue                                                           | SimpleText                             |
| hasLinkTo                             | (resourceclass)                                                    | Searchbox                              |
| hasRepresentation                     | Representation                                                     | Searchbox                              |
| isPartOf                              | (resourceclass)                                                    | Searchbox                              |
| seqnum                                | IntValue                                                           | Spinbox, <br>SimpleText                |


#### `BooleanValue`

`"object": "BooleanValue"`

Represents a Boolean ("true" or "false"). 
See the [xmlupload documentation](../xml-data-file.md#boolean-prop) for more information.

*gui_elements / gui_attributes*:

- `Checkbox`: The only GUI element for boolean values: a box to check or uncheck
    - *gui_attributes*: No attributes

Example:

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


#### `ColorValue`

`"object": "ColorValue"`

A string representation of a color in the hexadecimal form. 
See the [xmlupload documentation](../xml-data-file.md#color-prop) for more information.

*gui_elements / gui_attributes*:

- `Colorpicker`: The only GUI element for colors. It's used to choose a color.
    - *gui_attributes*:
        - `ncolors: integer` (optional): Number of colors the color picker should present.

Example:

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


#### `DateValue`

`object": "DateValue"`  

Represents a date. It's a string with the format `calendar:start:end`. 
See the [xmlupload documentation](../xml-data-file.md#date-prop) for more information.

*gui_elements / gui_attributes*:

- `Date`: The only GUI element for *DateValue*. A date picker GUI.
    - *gui_attributes*: No attributes

Example:

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


#### `DecimalValue`

`"object": "DecimalValue"`

A number with decimal point. 
See the [xmlupload documentation](../xml-data-file.md#decimal-prop) for more information.

*gui_elements / gui_attributes*:

- `Spinbox`: Provides a Spinbox to select a decimal value.
    - *gui_attributes*:
        - `max: decimal` (optional): maximal value
        - `min: decimal` (optional): minimal value
- `SimpleText`: A simple text entry box (one line only).
    - *gui_attributes*:
        - `maxlength: integer` (optional): maximum number of characters accepted
        - `size: integer` (optional): size of the input field

Example:

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


#### `GeonameValue`

`"object": "GeonameValue"`

Represents a location ID of [geonames.org](https://www.geonames.org). 
See the [xmlupload documentation](../xml-data-file.md#geoname-prop) for more information.

*gui_elements / gui_attributes*:

- `Geonames`: The only GUI element for *GeonameValue*. A dropdown to select a geonames.org location, either by ID if 
  digits are typed in, or by name if letters are typed in.
    - *gui_attributes*: No attributes

Example:

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


#### `IntValue`

`"object": "IntValue"`

Represents an integer value. 
See the [xmlupload documentation](../xml-data-file.md#integer-prop) for more information.

*gui_elements / gui_attributes*:

- `Spinbox`: A GUI element for *IntValue*. 
  A text field with and an "up" and a "down" button for increment/decrement.
    - *gui_attributes*:
        - `max: decimal` (optional): Maximal value
        - `min: decimal` (optional): Minimal value
- `SimpleText`: A simple text entry box (one line only). 
    - *gui_attributes*:
        - `maxlength: integer` (optional): The maximum number of characters accepted
        - `size: integer` (optional): The size of the input field

Example:

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


#### `ListValue`

`"object": "ListValue"`

Represents a node of a (possibly hierarchical) list. 
See the [xmlupload documentation](../xml-data-file.md#list-prop) for more information.

*gui_elements / gui_attributes*:

- `List`: A GUI element for *ListValue*. A dropdown to select a list node.
    - *gui_attributes*:
        - `hlist: list-name` (required): 
          The name of a list defined in the [`lists` section](./overview.md#lists).
- `Radio` and `Pulldown` are allowed, too, 
  but they don't have a different behavior than `List`. 
  It is recommended to use `List`.


Example:

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


#### `TextValue`

`"object": "TextValue"`

Represents a text that may contain standoff markup. 
See the [xmlupload documentation](../xml-data-file.md#text-prop) for more information.

*gui_elements / gui_attributes*:

- `SimpleText`: one-line text entry box (for text **without** markup)
    - *gui_attributes*:
        - `maxlength: integer` (optional): maximal length (number of characters accepted)
        - `size: integer` (optional): size (width) of widget
- `Textarea`: multiline text entry box (for text **without** markup)
    - *gui_attributes*:
        - `cols: integer` (optional): number of columns of the textarea
        - `rows: integer` (optional): number of rows of the textarea
        - `width: percent` (optional): width of the textarea on the screen
        - `wrap: soft|hard` (optional): wrapping of text
- `Richtext`: multiline rich-text editor (for text **with** markup)
    - *gui_attributes*: No attributes

Example:

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


#### `hasComment` Property

`"object": "TextValue"`

This property is a text field with formatted text. 

Example:

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
    "gui_element": "Richtext"
}
```


#### `TimeValue`

`"object": "TimeValue"`

A time value represents a precise moment in time in the Gregorian calendar. See the 
[xmlupload documentation](../xml-data-file.md#time-prop) for more information.

*gui_elements / gui_attributes*:

- `TimeStamp`: A GUI element for *TimeValue* which contains a date picker and a time picker.
    - *gui_attributes*: No attributes

Example:

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


#### `UriValue`

`"object": "UriValue"`

Represents an URI. See the [xmlupload documentation](../xml-data-file.md#uri-prop) for more information.

*gui_elements / gui_attributes*:

- `SimpleText`: A simple text entry box (one line only).
    - *gui_attributes*:
        - `maxlength: integer` (optional): The maximum number of characters accepted
        - `size: integer` (optional): The size of the input field

Example:

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


### Link-Properties

Link-properties do not follow the pattern of the previous data types, because they do not connect to a final value but 
to an existing resource. Thus, the `object` denominates the resource class the link will point to.


#### `hasLinkTo` Property

`"object": "<resourceclass>"`

The most basic kind of link-property is the `hasLinkTo` property. Its "super" element has to be `hasLinkTo` or derived 
from `hasLinkTo`. There are different groups of resource classes that can be the object:

- project resources: a resource class defined in the present ontology itself
- external resources: a resource class defined in another ontology
- DSP base resources:
    - `Resource`: the most generic one, can point to any resource class, be it a DSP base resource, a project resource, 
      or an external resource. `Resource` is at the very top of the inheritance hierarchy.
    - `Region`: a region in an image
    - `StillImageRepresentation`, `MovingImageRepresentation`, `TextRepresentation`, `AudioRepresentation`, 
      `DDDRepresentation`, `DocumentRepresentation`, or `ArchiveRepresentation`

The syntax how to refer to these different groups of resources is described [here](./caveats.md#referencing-ontologies).

*gui_elements / gui_attributes*:

- `Searchbox`: The only GUI element for *hasLinkTo*. Allows searching resources by entering the target resource name.
    - *gui_attributes*:
        - `numprops: integer` (optional): Number of search results to be displayed

Example:

```json
{
  "name": "hasOtherThing",
  "super": [
    "hasLinkTo"
  ],
  "object": ":Thing",
  "labels": {
    "en": "Another thing"
  },
  "gui_element": "Searchbox"
}
```


#### `hasRepresentation` Property

`"object": "Representation"`

A property pointing to the DSP base resource class `Representation`, which is the parent class of the DSP base resource 
classes `StillImageRepresentation`, `AudioRepresentation`, `MovingImageRepresentation`, ... Has to be used in 
combination with `"super": ["hasRepresentation"]`. 
This generic property can point to any type of the aforementioned representations, or to a subclass of them. See the 
[xmlupload documentation](../xml-data-file.md#resptr-prop) for more information.

*gui_elements / gui_attributes*:

- `Searchbox`: Allows searching resources that have super class `Representation` 
  by entering at least 3 characters into a searchbox.
    - *gui_attributes*:
        - `numprops: integer` (optional): While dynamically displaying the search result,
          the number of properties that should be displayed.

Example:

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


#### `isPartOf` Property

`"object": "<resourceclass>"`

A special case of linked resources are resources in a part-whole relation, 
i.e. resources that are composed of other resources. 
A `isPartOf` property has to be added to the resource that is part of another resource. 
In case of resources that are of type `StillImageRepresentation`, 
an additional property derived from `seqnum` with object `IntValue` is required. 
When defined, the user is able to leaf through the parts of a compound object, 
e.g. to leaf through pages of a book.

The DSP base properties `isPartOf` and `seqnum` 
can be used to derive a custom property from them, 
or they can be used directly as cardinalities in a resource. 
The example below shows both possibilities.

*gui_elements / gui_attributes*:

- `Searchbox`: The only GUI element for *isPartOf*. Allows searching resources by entering the target resource name.
    - *gui_attributes*:
        - `numprops: integer` (optional): Number of search results to be displayed

Example:

```json
"properties": [
    {
        "name": "partOfBook",
        "super": ["isPartOf"],
        "object": ":Book",
        "labels": {"en": "is part of"},
        "gui_element": "Searchbox"
    },
    {
        "name": "hasPageNumber",
        "super": ["seqnum"],
        "object": "IntValue",
        "labels": {"en": "has page number"},
        "gui_element": "SimpleText"
    }
],
"resources": [
    {
        "name": "Page",
        "labels": {"en": "Page using properties derived from 'isPartOf' and 'seqnum'"},
        "super": "StillImageRepresentation",
        "cardinalities": [
            {
                "propname": ":partOfBook",
                "cardinality": "1"
            },
            {
                "propname": ":hasPageNumber",
                "cardinality": "1"
            }
        ]
    },
    {
        "name": "MinimalisticPage",
        "labels": {"en": "Page using 'isPartOf' and 'seqnum' directly"},
        "super": "StillImageRepresentation",
        "cardinalities": [
            {
                "propname": "isPartOf",
                "cardinality": "1"
            },
            {
                "propname": "seqnum",
                "cardinality": "1"
            }
        ]
    }
]
```


#### `seqnum` Property

`"object": "IntValue"`

This property can be attached to a `StillImageRepresentation`, together with `isPartOf`. The `seqnum` is then the page
number of the image inside the compound object. Apart from this, `seqnum` is like an integer property. See the 
[xmlupload documentation](../xml-data-file.md#integer-prop) for more information.

*gui_elements / gui_attributes*:

- `Spinbox`: A GUI element for *IntValue*. 
  A text field with and an "up" and a "down" button for increment/decrement.
    - *gui_attributes*:
        - `max: decimal` (optional): Maximal value
        - `min: decimal` (optional): Minimal value
- `SimpleText`: A simple text entry box (one line only). 
    - *gui_attributes*:
        - `maxlength: integer` (optional): The maximum number of characters accepted
        - `size: integer` (optional): The size of the input field

Example: See the [`isPartOf` Property](#ispartof-property) above.




## The `resource` Object

```json
{
  "name": "school",
  "labels": {
    "de": "Schule",
    "en": "School",
    "fr": "Ecole",
    "it": "Scuola"
  },
  "super": "Resource",
  "comments": {
    "de": "Eine Bildungsinstitution für Grundbildung",
    "en": "An education institution for basic education",
    "fr": "Une institution de formation de base",
    "it": "Un'istituzione educativa per l'istruzione di base"
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
      "cardinality": "0-n"
    }
  ]
}
```



### Resource: `name`

(required)

`"name": "<string>"`

A name for the resource, e.g. "Book", "Manuscript", "Person". It should be in the form of
a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This means a string without blanks or special characters
but `-` and `_` are allowed (although not as first character).

By convention, resource names start with an upper case letter.



### Resource: `labels`

(required)

`"labels": {"<language>": "<string>", ...}`

Collection of `labels` for the resource as strings with language tag 
(currently, `en`, `de`, `fr`, `it`, and `rm` are supported).


### Resource: `super`

(required)

`"super": ["<super-resource>", "<super-resource>", ...]`

A resource is always derived from at least one other resource. There are three groups of resources that can serve 
as super-resource:

- DSP base resources
- resources defined in external ontologies
- resources defined in the project ontology itself

The syntax how to refer to these different groups of resources is described [here](caveats.md#referencing-ontologies).

The following base resources can be used as super-resource:

- `Resource`: A generic resource representing an item from the real world. 
  This is the most general case, 
  to be used in all cases when your resource is none of the special cases below.
- `ArchiveRepresentation`: A resource representing an archive file (e.g. ZIP)
- `AudioRepresentation`: A resource representing an audio file
- `DDDRepresentation`: A resource representing a 3-D representation (not yet implemented)
- `DocumentRepresentation`: A resource representing an opaque document (e.g. a PDF)
- `MovingImageRepresentation`: A resource representing a video
- `StillImageRepresentation`: A resource representing an image
- `TextRepresentation`: A resource representing a text

**File Extensions**: An overview of the supported file types per representation can be found in the 
[xmlupload documentation](../xml-data-file.md#bitstream).



### Resource: `cardinalities`

(required*)

```json
"cardinalities": [
  {
    "propname": ":hasText",
    "gui_order": 1,
    "cardinality": "1-n"
  },
  {
    ...
  }
]
```

An array that contains information about the relation between resources and properties. 
It tells what properties a resource can have 
as well as how many values a property can have.
A cardinality is defined as follows:

- `propname` (mandatory): The name of the property. 
  If it's used in the form `:my_property`, the current ontology is referenced.
  If the property was defined in another ontology, the prefix of that ontology must be provided.
- `gui_order` (optional): By default, DSP-APP displays the properties in the order 
  how they are defined in the `cardinalities` array.
  If you prefer another order, you can provide a positive integer here.
  Example: You order the propnames alphabetically in the JSON file, 
  but they should be displayed in another order in DSP-APP.
- `cardinality` (mandatory): Indicates how often a given property may occur. The possible values are:
    - `"1"`: exactly once (mandatory one value and only one)
    - `"0-1"`: The value may be omitted, but can occur only once.
    - `"1-n"`: At least one value must be present, but multiple values may be present.
    - `"0-n"`: The value may be omitted, but may also occur multiple times.

(*A resource can have no cardinalities.
If the `super` is a class of the own ontology, the child class will inherit the cardinalities. 
If this is not the case then no properties can be used with this class.)



### Resource: `comments`

(optional)

`"comments": { "<lang>": "<comment>", "<lang>": "<comment>", ... }`

Comments with language tags
(currently, `en`, `de`, `fr`, `it`, and `rm` are supported).
The `comments` element is optional.
