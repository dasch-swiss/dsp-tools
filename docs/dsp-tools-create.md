[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# JSON data model definition format

This document describes the structure of a data model (ontology) used by DSP. According to Wikipedia,
the [data model](https://en.wikipedia.org/wiki/Data_model) is "an abstract model that organizes elements of data and
standardizes how they relate to one another and to the properties of real-world entities. [...] A data model explicitly
determines the structure of data. Data models are typically specified by a data specialist, data librarian, or a digital
humanities scholar in a data modeling notation". The following sections describe the notation for ontologies in the
context of DSP.

## A short overview

A complete data model definition for DSP looks like this:

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json",
  "project": {
    "shortcode": "0123",
    "shortname": "BiZ",
    "longname": "Bildung in Zahlen",
    "descriptions": {
      ...
    },
    "keywords": [
      ...
    ],
    "lists": [
      ...
    ],
    "groups": [
      ...
    ],
    "users": [
      ...
    ],
    "ontologies": [
      ...
    ]
  }
}
```

### "prefixes" object

`"prefixes": { "prefix": "<iri>", ...}`

The `prefixes` object contains the prefixes of external ontologies that are used in the current project. All prefixes
are composed of the actual prefix and an IRI. The prefix is used as an abbreviation so one does not have to write the
full qualified IRI each time it is used. So, instead of writing a property called "familyname" as
`http://xmlns.com/foaf/0.1/familyName` one can simply use `foaf:familyName`.

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  }
}
```

### "$schema" object

The `$schema` object refers to the JSON schema for DSP data model definitions and is mandatory.

`"$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json"`

### "project" object

`"project": {"key": "<value>", ...}`

The `project` object contains all resources and properties of the ontology as well as some information about the
project. It requires all the following data fields:

- shortcode
- shortname
- longname
- keywords
- ontologies

The following fields are optional (if one or more of these fields are not used, they should be omitted):

- descriptions
- lists
- groups
- users

A simple example definition of the `project` object looks like this:

```json
{
  "project": {
    "shortcode": "0809",
    "shortname": "test",
    "longname": "Test Example",
    "descriptions": {
      "en": "This is a simple example project",
      "de": "Dies ist ein einfaches Beispielprojekt"
    },
    "keywords": [
      "example",
      "simple"
    ],
    "lists": [
      ...
    ],
    "groups": [
      ...
    ],
    "users": [
      ...
    ],
    "ontologies": [
      ...
    ]
  }
}
```

## "project" object in detail

In the following section all fields of the `project` object are explained in detail.

### Shortcode

`"shortcode": "<4-hex-characters>"`

The shortcode has to be unique and is represented by a 4 digit hexadecimal string. The shortcode has to be provided by the DaSCH.

### Shortname

`"shortname": "<string>"`

The shortname has to be unique. It should be in the form of a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This means a
string without blanks or special characters but `-` and `_` are allowed (although not as first character).

### Longname

`"longname": "<string>"`

The longname is a string that provides the full name of the project.

### Descriptions

`"descriptions": {"<lang>": "<string>", ...}`

The description is represented as a collection of strings with language tags (currently "en", "de", "fr" and "it" are
supported). It is the description of the project.

### Keywords

`"keywords": ["<string>", "<string>", ...]`

Keywords are represented as an array of strings and are used to describe and/or tag the project.

### Lists

`"lists": [<list-definition>,<list-definition>,...]`

Lists can be used to provide controlled vocabularies and can be "flat" or "hierarchical". One advantage of the use of
hierarchical lists is that it allows a user to sub-categorize objects. This helps in the formulation of specific search
requests. If there is a list node "Vocal music" and sub-nodes "Song" and "Opera", a search for "Vocal Music" would
return objects classified as "Song" and "Opera". But a search for "Song" would only return objects classified as "Song".

In dsp-tools the structure of a list is mapped using JSON. Only a single root node is allowed which also contains the
name of the list. Inside the root node any number of child nodes and sub-nodes of child nodes are allowed.

A resource can be assigned to a list node within its properties. For example, a resource of type "Musical work" with the
title "La Traviata" would have a property like "hasMusicGenre" with the value "Grand opera". Within DSP, each property
has a cardinality. Sometimes, a taxonomy allows an object to belong to multiple categories. In these cases, a
cardinality greater than 1 has to be used.

A node of a list may have the following elements:

- _name_: Name of the node as string. It is mandatory and has to be unique within the list.
- _labels_: Label with language tags in the form `{ "<lang>": "<label>", "<lang>": "<label>", ... }`. The `labels`
  element is mandatory. It needs to specify at least one language. Currently, "de", "en", "fr" and "it" are supported.
- _comments_: Comment with language tags in the form `{ "<lang>": "<comment>", "<lang>": "<comment>", ... }`.
  Currently, "de", "en", "fr" and "it" are supported. The `comments` element is mandatory for the root node of the list.
  For all other nodes, it is optional. If not used, the element should be omitted.
- _nodes_: Array of sub-nodes. The `nodes` element is optional and can be omitted in case of a flat list.

Example of a list:

```json
{
  "lists": [
    {
      "name": "my_list",
      "labels": {
        "en": "Disciplines of the Humanities"
      },
      "comments": {
        "en": "This is just an example.",
        "fr": "C'est un example."
      },
      "nodes": [
        {
          "name": "node_1_1",
          "labels": {
            "en": "Performing arts"
          },
          "comments": {
            "en": "Arts that are events",
            "de": "Künste mit performativem Character"
          },
          "nodes": [
            {
              "name": "node_2_2",
              "labels": {
                "en": "Music"
              },
              "nodes": [
                {
                  "name": "node_3_3",
                  "labels": {
                    "en": "Chamber music"
                  }
                },
                {
                  "name": "node_4_3",
                  "labels": {
                    "en": "Church music"
                  }
                },
                {
                  "name": "node_5_3",
                  "labels": {
                    "en": "Conducting"
                  },
                  "nodes": [
                    {
                      "name": "node_6_4",
                      "labels": {
                        "en": "Choirs"
                      }
                    },
                    {
                      "name": "node_7_4",
                      "labels": {
                        "en": "Orchestras"
                      }
                    }
                  ]
                },
                {
                  "name": "node_8_3",
                  "labels": {
                    "en": "Music history"
                  }
                },
                {
                  "name": "node_9_3",
                  "labels": {
                    "en": "Musictheory"
                  }
                },
                {
                  "name": "node_10_3",
                  "labels": {
                    "en": "Musicology"
                  }
                },
                {
                  "name": "node_11_3",
                  "labels": {
                    "en": "Jazz"
                  }
                },
                {
                  "name": "node_12_3",
                  "labels": {
                    "en": "Pop/Rock/Blues"
                  }
                }
              ]
            }
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
  ]
}
```

#### Lists from Excel

A list can be directly imported from one or several Excel files. The Excel sheet must have the following format:

![img-list-example.png](assets/images/img-list-example.png)

If there are several languages, a separate Excel file for each language has to be provided. The folder with the Excel
file(s) can be directly referenced inside the list definition by defining it as new list node:

```json
{
  "name": "List-from-excel",
  "labels": {
    "en": "List from an Excel file",
    "de": "Liste von einer Excel-Datei"
  },
  "comments": {
    "en": "This is just an example.",
    "fr": "C'est un example."
  },
  "nodes": {
    "folder": "excel-lists"
  }
}
```

The nodes section must contain the field:

- _folder_: Path to the folder where the Excel files are stored

Further details to this functionality can be found
[here](dsp-tools-excel#create-a-list-from-one-or-several-excel-files).

The `lists` element is optional. If not used, it should be omitted.

### Groups

`"groups": [<group-definition>, <group-definition>,...]`

The `groups` object contains groups definitions. This is used to specify the permissions a user gets. A project may
define several groups such as "project-admins", "editors" etc. in order to provide their members specific permissions.

A group definition has the following elements:

- _name_: name of the group, mandatory
- _descriptions_: description of the group with language tags in the form `"descriptions": {"<lang>": "<string>", ...}` (
  currently "en", "de", "fr" and "it" are supported), mandatory
- _selfjoin_: true if users are allowed to join the group themselves, false if an administrator has to add the users,
  optional
- _status_: true if the group is active, false if the group is inactive, optional

Example:

```json
{
  "groups": [
    {
      "name": "biz-editors",
      "descriptions": {"en" : "Editors for the BiZ project"},
      "selfjoin": false,
      "status": true
    }
  ]
}
```

The `groups` element is optional. If not used, it should be omitted. It is currently not recommended using it.

### Users

`"users": [<user-definition>, <user-definition>,...]`

This object contains user definitions. A user has the following elements:

- _username_: username used for login
- _email_: email that identifies the user, has to be unique within DSP
- _givenName_: firstname of the user
- _familyName_: surname of the user
- _password_: password of the user
- _lang_: the default language of the user: "en", "de", "fr", "it" (optional, default: "en")
- _groups_: List of groups the user belongs to. The name of the group has to be provided with the ontology's namespace,
  p.ex. "onto:editors". The given ontology defined in the same ontology file has no name, so only ":editors" is required
  if the user belongs to the group "editors". (optional)
- _projects_: List of projects the user belongs to. The project name has to be followed by a ":" and either "member"
  or "admin". This indicates if the new user has admin rights in the given project or is an ordinary
  user. `myproject:admin` would add the user as admin to the project "myproject". The given project defined in the same
  ontology file has no name, so only ":admin"or ":member" is required. (optional)

Example:

```json
{
  "users": [
    {
      "username": "bizedit",
      "email": "bizedit@test.org",
      "givenName": "biz-given",
      "familyName": "biz-family",
      "password": "biz1234",
      "lang": "en",
      "groups": [
        ":biz-editors"
      ],
      "projects": [
        ":admin",
        "otherProject:member"
      ]
    }
  ]
}
```

The `users` element is optional. If not used, it should be omitted.

### Ontologies

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

`"ontologies": [<ontology-definition>, <ontology-definition>, ...]`

Inside the `ontologies` section all resources and properties are described. A project may have multiple ontologies. It
requires the following data fields:

- name
- label
- properties
- resources

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

#### Name

`"name": "<string>"`

The ontology's (short) name should be in the form of a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This
means a string without blanks or special characters but `-` and `_` are allowed (although not as first character).

#### Label

`"label": "<string>"`

A string that provides the full name of the ontology.

#### Properties

`"properties": [<property-definition>, <property-definition>, ...]`

A `properties` array contains all properties used to describe resources in the ontology. A property has to be of a
certain data type. It is not possible to create a custom data type.

The following fields are mandatory:

- name
- labels
- object
- gui_element

Please note that `object` is used to define the data type. The `gui_element` depends on the value of the `object`.

The following fields are optional (they can be omitted):

- super
- gui_attributes

The `gui_attributes` depends on the value of the `gui_element`.

##### Name

`"name": "<string>"`

A name for the property, e.g. "pageOf", "hasBirthdate", "createdBy". It should be in the form of
a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This means a string without blanks or special characters
but `-` and `_` are allowed (although not as first character).

##### Labels

`"labels": {"<language>": "<string>", ...}`

Collection of `labels` for the property as strings with language tag (currently "en", "de", "fr"
and "it" are supported).

##### Object / gui_element / gui_attribute

`"object": "<data-type>"`

The `object` defines the data type of the value that the property will store. The following data types are allowed:

###### TextValue

`"object": "TextValue"`

Represents a text that may contain standoff markup.

*gui\_elements / gui\_attributes*:

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

###### ColorValue

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
    "hasValue"
  ],
  "object": "ColorValue",
  "labels": {
    "en": "Color"
  },
  "gui_element": "Colorpicker"
}
```

###### DateValue

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

*gui-elements / gui_attributes*:

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

###### TimeValue

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

###### DecimalValue

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

###### GeomValue

`"object": "GeomValue"`

Represents a geometrical shape as JSON. Geometrical shapes are used to define regions of interest (ROI) on still images
or moving images.

*gui-elements / gui_attributes*:

- `Geometry`: not yet implemented.
    - _gui_attributes_: No attributes
- `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
  "maxlength=integer" and "size=integer" are optional.
    - _gui_attributes_:
        - `maxlength=integer` (optional): The maximum number of characters accepted
        - `size=integer` (optional): The size of the input field

*Example*:

```json
{
  "name": "hasGeometry",
  "super": [
    "hasValue"
  ],
  "object": "GeomValue",
  "labels": "Geometry",
  "gui_element": "SimpleText"
}
```

###### GeonameValue

Represents a location ID in geonames.org. The DSP platform uses identifiers provided by
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

###### IntValue

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

###### BooleanValue

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

###### UriValue

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

###### IntervalValue

`"object": "IntervalValue"`

Represents a time-interval

*gui-elements / gui_attributes*:

- `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
  "maxlength=integer" and "size=integer" are optional.
    - _gui_attributes_:
        - `maxlength=integer` (optional): The maximum number of characters accepted
        - `size=integer` (optional): The size of the input field
- `Interval`: not yet implemented.
    - _gui_attributes_: No attributes

*Example:*

```json
{
  "name": "hasInterval",
  "super": [
    "hasValue"
  ],
  "object": "IntervalValue",
  "labels": {
    "en": "Time interval"
  },
  "gui_element": "Interval"
}
```

###### ListValue

`"object": "ListValue"`

Represents a node of a (possibly hierarchical) list

*gui-elements / gui_attributes*:

- `Radio`: A GUI element for _ListValue_. A set of radio buttons. This works only with flat lists.
    - _gui_attributes_:
        - `hlist=<list-name>` (mandatory): The reference of a [list](#lists) root node
- `List`: A GUI element for _ListValue_. A list of values to select one from. This GUI element should be chosen for
  hierarchical lists or flat lists that could be expanded to hierarchical lists in the future.
    - _gui_attributes_:
        - `hlist=<list-name>` (mandatory): The reference of a [list](#lists) root node

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

###### LinkValue

`"object": ":<resource-name>"`

LinkValues do not follow the pattern of the previous data types, because they do not connect to a final value but to
another resource which has to be defined. Thus, the "object" denominates the resource class the link will point to. If
the resource is defined in the same ontology, the name has to be prepended by a ":", if the resource is defined in
another (previously defined)
ontology, the ontology name has to be prepended separated by a colon ":", e.g.
"other-onto:MyResource". The "super"-element has to be "hasLinkTo" or at least derived from "hasLinkTo" (how to derive a
resource or property from another one is not part of this documentation).

*gui-elements/gui_attributes*:

- `Searchbox`: Has to be used with _hasLinkTo_ property. Allows searching resources by entering a resource that the given resource
  should link to. It has one gui_attribute that indicates how many properties of the found resources should be
  indicated. This is mandatory.
    - _gui_attributes_:
        - `numprops=integer` (optional): While dynamically displaying the search result, the number of properties that
          should be displayed.

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

Like already mentioned before: The following two fields are optional (can be omitted), with the notable exception of
the "super"
clause in case of LinkValues where the super clause is mandatory:

##### Super

`"super": ["<super-property>", "<super-property>, ...]`

A property has to be derived from at least one base property. The most generic base property that the DSP offers is
_hasValue_. In addition, the property may be a sub-property of properties defined in external or other ontologies.
External ontologies like `dcterms` or `foaf` must be defined in the "prefix" section.

In this case the qualified name - including the prefix of the external or internal ontology - has to be given.

The following base properties are defined by DSP:

- `hasValue`: This is the most generic base.
- `hasLinkTo`: This value represents a link to another resource. You have to indicate the "_object_" as a prefixed name
  that identifies the resource class this link points to (a ":" prepended to the name is sufficient if the resource is
  defined in the current ontology).
- `hasColor`: Defines a color value (_ColorValue_)
- `hasComment`: Defines a "standard" comment
- `hasGeometry`: Defines a geometry value (a JSON describing a polygon, circle or rectangle), see _ColorValue_
- `isPartOf`: A special variant of _hasLinkTo_. It says that an instance of the given resource class is an integral part
  of another resource class. E.g. a "page" is part of a "book".
- `isRegionOf`: A special variant of _hasLinkTo_. It means that the given resource class is a "region" of another
  resource class. This is typically used to describe regions of interest in images.
- `isAnnotationOf`: A special variant of _hasLinkTo_. It denotes the given resource class as an annotation to another
  resource class.
- `seqnum`: An integer that is used to define a sequence number in an ordered set of instances, e.g. the ordering of the
  pages in a book (independent of the page naming)

Example of a `properties` object:

```json
{
  "properties": [
    {
      "name": "schulcode",
      "object": "TextValue",
      "super": [
          "hasValue"
      ],
      "labels": {
        "de": "Schulcode"
      },
      "gui_element": "SimpleText",
      "gui_attributes": {
        "size": 32,
        "maxlength": 128
      }
    },
    {
      "name": "schulname",
      "object": "TextValue",
      "super": [
          "hasValue"
      ],
      "labels": {
        "de": "Name der Schule"
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

#### Resources

The resource classes are the primary entities of the data model. They are the actual objects inside a terminology space.
A resource class can be seen as a template for the representation of a real object that is represented in the DSP. A
resource class defines properties (_data fields_). For each of these properties a data type as well as the cardinality
has to be provided.

`"resources": [<resource-definition>, <resource-definition>, ...]`

A resource object needs to have the following fields:

- name
- labels
- super
- cardinalities

The following field is optional:

- comments

##### Name

`"name": "<string>"`

A name for the resource, e.g. "Book", "Manuscript", "Person". It should be in the form of
a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This means a string without blanks or special characters
but `-` and `_` are allowed (although not as first character).

##### Labels

`"labels": {"<language>": "<string>", ...}`

Collection of `labels` for the resource as strings with language tag (currently "en", "de", "fr"
and "it" are supported).

##### Super

`"super": ["<super-resource>", "<super-resource>", ...]`

A resource is always derived from at least one other resource. The most generic resource class for DSP is `Resource`. A
resource may be derived from resources defined in external ontologies.

The following predefined resources are provided by DSP:

- `Resource`: A generic resource that represents an item from the real world
- `StillImageRepresentation`: An object that is connected to a still image
- `TextRepresentation`: An object that is connected to an (external) text (not yet implemented)
- `AudioRepresentation`: An object representing audio data (not yet implemented)
- `DDDRepresentation`: An object representing a 3-D representation (not yet implemented)
- `DocumentRepresentation`: An object representing an opaque document (e.g. a PDF)
- `MovingImageRepresentation`: An object representing a moving image (video, film)
- `Annotation`: A predefined annotation object. It has automatically the following predefined properties defined:
    - `hasComment` (1-n)
    - `isAnnotationOf` (1)
- `LinkObj`: A resource class linking together several other, generic, resource classes. The class has the following
  properties:
    - `hasComment` (1-n)
    - `hasLinkTo` (1-n)
- `Region`: Represents a simple region. The class has the following properties:
    - `hasColor` (1)
    - `isRegionOf` (1)
    - `hasGeometry` (1)
    - `isRegionOf` (1)
    - `hasComment` (0-n)

##### Cardinalities

`"cardinalities": [...]`

An array that contains information about the relation between resources and properties. It tells what properties a
resource can have as well as how many times the relation is established.

- `cardinalities`: Array of references to the properties that the resource may hold including the cardinality. A
  cardinality has the following properties:
    - `propname`: The name of the property. If it's used in the form `:my_propname`, the current ontology is referenced.
      Otherwise, the prefix of the ontology the property is part of has to be used.
    - `gui_order`: An integer number which will help the GUI to display the properties in the desired order (optional)
    - `cardinality`: Indicates how often a given property may occur. The possible values are:
        - `"1"`: exactly once (mandatory one value and only one)
        - `"0-1"`: The value may be omitted, but can occur only once.
        - `"1-n"`: At least one value must be present, but multiple values may be present.
        - `"0-n"`: The value may be omitted, but may also occur multiple times.

##### Comments

`"comments": { "<lang>": "<comment>", "<lang>": "<comment>", ... }`

Comments with language tags. The `comments` element is optional. Currently, "de", "en", "fr" and "it" are supported.

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

## Fully fleshed out example ontology

Finally, here is a complete example of an ontology definition:

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json",
  "project": {
    "shortcode": "0170",
    "shortname": "teimp",
    "longname": "Test Import",
    "descriptions": {
      "en": "This is a project for testing the creation of ontologies and data",
      "de": "Dies ist ein Projekt, um die Erstellung von Ontologien und Datenimport zu testen"
    },
    "keywords": [
      "test",
      "import"
    ],
    "lists": [
      {
        "name": "orgtpye",
        "labels": {
          "en": "Organization Type",
          "de": "Organisationsart",
        },
        "comments": {
          "en": "List of different organization types",
          "de": "Liste unterschiedlicher Organisationstypen"
        },
        "nodes": [
          {
            "name": "business",
            "labels": {
              "en": "Commerce",
              "de": "Handel"
            },
            "nodes": [
              {
                "name": "transport",
                "labels": {
                  "en": "Transportation",
                  "de": "Transport"
                }
              },
              {
                "name": "finances",
                "labels": {
                  "en": "Finances",
                  "de": "Finanzen"
                }
              }
            ]
          },
          {
            "name": "society",
            "labels": {
              "en": "Society",
              "de": "Gesellschaft"
            }
          }
        ]
      }
    ],
    "ontologies": [
      {
        "name": "teimp",
        "label": "Test import ontology",
        "properties": [
          {
            "name": "firstname",
            "super": [
              "hasValue",
              "foaf:givenName"
            ],
            "object": "TextValue",
            "labels": {
              "en": "Firstname",
              "de": "Vorname"
            },
            "gui_element": "SimpleText",
            "gui_attributes": {
              "size": 24,
              "maxlength": 32
            }
          },
          {
            "name": "lastname",
            "super": [
              "hasValue",
              "foaf:familyName"
            ],
            "object": "TextValue",
            "labels": {
              "en": "Lastname",
              "de": "Nachname"
            },
            "gui_element": "SimpleText",
            "gui_attributes": {
              "size": 24,
              "maxlength": 64
            }
          },
          {
            "name": "member",
            "super": [
              "hasLinkTo"
            ],
            "object": "teimp:organization",
            "labels": {
              "en": "member of",
              "de": "Mitglied von"
            },
            "gui_element": "Searchbox"
          },
          {
            "name": "name",
            "super": [
              "hasValue"
            ],
            "object": "TextValue",
            "labels": {
              "en": "Name",
              "de": "Name"
            },
            "gui_element": "SimpleText",
            "gui_attributes": {
              "size": 64,
              "maxlength": 64
            }
          },
          {
            "name": "orgtype",
            "super": [
              "hasValue"
            ],
            "object": "ListValue",
            "labels": {
              "en": "Organizationtype",
              "de": "Organisationstyp"
            },
            "comments": {
              "en": "Type of organization",
              "de": "Art der Organisation"
            },
            "gui_element": "Pulldown",
            "gui_attributes": {
              "hlist": "orgtype"
            }
          }
        ],
        "resources": [
          {
            "name": "person",
            "super": "Resource",
            "labels": {
              "en": "Person",
              "de": "Person"
            },
            "comments": {
              "en": "Represents a human being",
              "de": "Repräsentiert eine Person/Menschen"
            },
            "cardinalities": [
              {
                "propname": ":firstname",
                "gui_order": 1,
                "cardinality": "1"
              },
              {
                "propname": ":lastname",
                "gui_order": 2,
                "cardinality": "1"
              },
              {
                "propname": ":member",
                "gui_order": 3,
                "cardinality": "0-n"
              }
            ]
          },
          {
            "name": "organization",
            "super": "Resource",
            "labels": {
              "en": "Organization",
              "de": "Organisation"
            },
            "comments": {
              "en": "Denotes an organizational unit",
              "de": "Eine Institution oder Trägerschaft"
            },
            "cardinalities": [
              {
                "propname": ":name",
                "gui_order": 1,
                "cardinality": "1-n"
              },
              {
                "propname": ":orgtype",
                "gui_order": 2,
                "cardinality": "1-n"
              }
            ]
          }
        ]
      }
    ]
  }
}
```
