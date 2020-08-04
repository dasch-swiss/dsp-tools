[![PyPI version](https://badge.fury.io/py/knora.svg)](https://badge.fury.io/py/knora)

# knora-create-ontology

Creating an ontology with `knora-create-ontology`
This script reads a JSON file containing the data model (ontology) definition,
connects to the Knora server and creates the data model.

## Usage:

```bash
$ knora-create-ontology data_model_definition.json
```
It supports the foloowing options:

- _"-s server" | "--server server"_: The URl of the Knora server [default: localhost:3333]
- _"-u username" | "--user username"_: Username to log into Knora [default: root@example.com]
- _"-p password" | "--password password"_: The password for login to the Knora server [default: test]
- _"-v" | "--validate"_: If this flag is set, only the validation of the json is run
- _"-l" | "--lists"_: Only create the lists using [simplyfied schema](#json-for-lists). Please note
  that in this case the project __must__ exist.

## JSON ontology definition format

The first object listed in the JSON file contains the ```prefixes``` of external ontologies that are also used in the 
current project. 

### Prefixes

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  }
}
```

### Project data
Right after the prefix object must come the ```project``` object, which contains all resources and properties of the current 
project.

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "project": {}
}
```

The "project" object is the bread and butter of the ontology. All important properties of the ontology are 
specified therein. 

The project definitions ***requires exactly*** all of the following datafields:

- _"shortcode"_: A hexadecimal string in the range between "0000" and "FFFF" that's used to uniquely identifying the 
project. The shortcode has to be provided by the DaSCH.
- _"shortname"_: A short name (string) for the project. It's ment like a nickname. Is the name of the Project e.g. 
Albus Percival Wulfric Brian Dumbledore? A shortname for him could be "Albi"
- a _"longname"_: A longer string giving the full name for the project. In our case, the longname would be "Albus 
Percival Wulfric Brian Dumbledore"
- _descriptions_: *Exactly* one or more strings describing the projects content. These
  descriptions can be supplied in several languages (currently _"en"_, _"de"_, _"fr"_ and _"it"_ are supported).
  The descriptions have to be given as JSON object with the language as key
  and the description as value. (See the example down below in the curly bracket after "desctiptions" to see what that means)
- _keywords_: An array of keywords describing the project. (Array can be empty as well e.i. "keywords": [] )
- _lists_: An array containing flat or hierarchical ordered terms. These terms 
are used to further define the scope of the project. Is your project all about letters written in different paper formats? 
Use a list that contains the terms ["A4", A3", "A2", "A1"] (This would be ordered hierarchically). 
Is your project about diplomatic texts between the different cantons? A list such as ["BL", "BS", "VS", ...] could be ideal
 (this would be a flat list). (This array can be empty as well)
- _users_: Array of user definitions that will be added (Can be empty as well)
- _ontology_: The definition of the data model (ontology)

This a project definition lokks like follows:
  
```json
"project": {
   "shortcode": "0809",
   "shortname": "test"
   "longname": "Test Example",
   "descriptions": {
     "en": "This is a simple example project with no value.",
     "de": "Dies ist ein einfaches, wertloses Beispielproject"
   }
   "keywords": ["example", "senseless"],
   "lists": [],
   "users": [],
   "ontology": {}
}
```

### Lists
A List consists of a root node identifing the list and an array of subnodes.
Each subnode may contain again subnodes (hierarchical list).
A node has the following elements:

- _name_: Name of the node. Should be unique for the given list
- _labels_: Language dependent labels in the form ```{ "<lang>": "<label>, ... }```
- _comments_: language dependent comments (optional) in the form ```{ "<lang>": "<comment>, ... }```
- _nodes_: Array of subnodes (optional – leave out if there are no subnodes, that is a flat list)

The _lists_ object contains an _array of lists_. Here an example:

```json
    "lists": [
      {
        "name": "orgtpye",
        "labels": { "de": "Organisationsart", "en": "Organization Type" },
        "nodes": [
          {
            "name": "business",
            "labels": { "en": "Commerce", "de": "Handel" },
            "comments": { "en": "no comment", "de": "kein Kommentar" },
            "nodes": [
              {
                "name": "transport",
                "labels": { "en": "Transportation", "de": "Transport" }
              },
              {
                "name": "finances",
                "labels": { "en": "Finances", "de": "Finanzen" }
              }
            ]
          },
          {
            "name": "society",
            "labels": { "en": "Society", "de": "Gesellschaft" }
          }
        ]
      }
    ]
```
The _lists_ element is optional.

### Groups
This is an array of _groups_-definition. A project may define user groups such as "project-admins", "students" etc.
and give the members of each group permissions.
A _group_-defintion has the following elements:
- _name_: The name of the group
- _description_: Description of the purpose of the group
- _selfjoin_: True, if users are able to join the group; false, if an administrator must add the users
- _status_: True, the group is active; false, the group is not active

Example:
```json
    "groups": [
      {
        "name": "biz-editors",
        "description": "Editors for the BiZ-project",
        "selfjoin": false,
        "status": true
      }
    ],

```

### Users
This is an array of _user_-definitions. A user has the following elements:
- _username_: The short username for login
- _email_: Unique email that identifies the user
- _givenName_: Firstname of the user
- _familyName_: Name of the user
- _password_: Clear initial password of the user
- _lang_: The preferred language of the user: "en", "de", "fr", "it" [optional, default: "en"]
- _projects_: List of projects the user belongs to

Example:
```json
    "users": [
      {
        "username": "bizedit",
        "email": "bizedit@test.org",
        "givenName": "biz-given",
        "familyName": "biz-family",
        "password": "biz1234",
        "lang": "en",
        "groups": [":biz-editors"],
        "projects": [":admin","anything:member"]
      }
    ],

```
The _users_ element is optional.

### Ontology

The _ontology_ object contains the definition of the data model. The ontology has
the following elemens:

- _name_: The name of the ontology. This has to be a NCNAME conformant name that can be use as prefix!
- _label_: Human readable and understandable name of the ontology
- _resources_: Array defining the resources (entities) of the data model

```json
    "ontology": {
      "name": "teimp",
      "label": "Test import ontology",
      "properties": [],
      "resources": []
    }
```

### Properties
Properties are the definition of the data fields a resource class may or must have.
The properties object has the following fields:

- _name_: A name for the property
- _labels_: Language dependent, human readable names
- _super_: A property has to be derived from at least one base property. The most generic base property
  Knora offers is _hasValue_. In addition the property may by als a subproperty of
  properties defined in external ontologies. In this case the qualified name including
  the prefix has to be given.
  The following base properties are definied by Knora:
  - _hasValue_: This is the most generic base.
  - _hasLinkTo_: This value represents a link to another resource. You have to indicate the
    the "_object_" as a prefixed IRI that identifies the resource class this link points to.
  - _hasColor_: Defines a color value (_ColorValue_)
  - _hasComment_: Defines a "standard" comment
  - _hasGeometry_: Defines a geometry value (a JSON describing a polygon, circle or rectangle), see _ColorValue_
  - _isPartOf_: A special variant of _hasLinkTo_. It says that an instance of the given resource class
    is an integral part of another resource class. E.g. a "page" is a prt of a "book".
  - _isRegionOf_: A special variant of _hasLinkTo_. It means that the given resource class
    is a "region" of another resource class. This is typically used to describe regions
    of interest in images.
  - _isAnnotationOf_: A special variant of _hasLinkTo_.  It denotes the given resource class
    as an annotation to another resource class.
  - _seqnum_: An integer that is used to define a sequence number in an ordered set of
    instances.
- _object_: The "object" defines the data type of the value that the property will store.
  The following object types are allowed:
  - _TextValue_: Represents a text that may contain standoff markup
  - _ColorValue_: A string in the form "#rrggbb" (standard web color format)
  - _DateValue_: represents a date. It is a string having the format "_calendar":"start":"end"
    - _calender_ is either _GREGORIAN_ or _JULIAN_
    - _start_ has the form _yyyy_-_mm_-_dd_. If only the year is given, the precision
      is to the year, of only the year and month are given, the precision is to a month.
    - _end_ is optional if the date represents a clearely defined period or uncertainty.
    In total, a DateValue has the following form: "GREGORIAN:1925:1927-03-22"
    which means antime in between 1925 and the 22nd March 1927.
  - _DecimalValue_: a number with decimal point
  - _GeomValue_: Represents a geometrical shape as JSON.
  - _GeonameValue_: Represents a location ID in geonames.org
  - _IntValue_: Represents an integer value
  - _BooleanValue_: Represents a Boolean ("true" or "false)
  - _UriValue_: : Represents an URI
  - _IntervalValue_: Represents a time-interval
  - _ListValue_: Represents a node of a (possibly hierarchical) list
- _gui_element_: The gui_element is – strictly seen – not part of the data. It gives the
  generic GUI a hint about how the property should be presented to the used. Each gui_element
  may have associated gui_attributes which contain further hints.
  There are the following gui_elements available:
  - _Colorpicker_: The only GUI element for _ColorValue_. Let's You pick a color. It requires the attribute "ncolors=integer"
  - _Date_: The only GUI element for _DateValue_. A date picker gui. No attributes
  - _Geometry_: Not Yet Implemented.
  - _Geonames_: The only GUI element for _GeonameValue_. Interfaces with geonames.org and allows to select a location
  - _Interval_: Not Yet Implemented.
  - _List_: A list of values. The Attribute "hlist=<list-iri>" is mandatory!
  - _Pulldown_: A GUI element for _ListValue_. Pulldown for list values. Works also for hierarchical lists. The Attribute "hlist=<list-iri>" is mandatory!
  - _Radio_: A GUI element for _ListValue_. A set of radio buttons. The Attribute "hlist=<list-iri>" is mandatory!
  - _SimpleText_: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes "maxlength=integer" and "size=integer" are optional.
  - _Textarea_: A GUI element for _TextValue_. Presents a multiline textentry box. Optional attributes are "cols=integer",  "rows=integer", "width=percent" and "wrap=soft|hard".
  - _Richtext_: A GUI element for _TextValue_. Provides a richtext editor.
  - _Searchbox_: Must be used with _hasLinkTo_ properties. Allows to search and enter a resource that the given resource should link to. The Attribute "numprops=integer"
     indicates how many properties of the found resources should be indicated. It's mandatory!
  - _Slider_: A GUI element for _DecimalValue_. Provides a slider to select a decimal value. The attributes "max=decimal" and "min=decimal" are mandatory!
  - _Spinbox_: A GUI element for _IntegerValue_. A text field with and "up"- and "down"-button for increment/decrement. The attributes "max=decimal" and "min=decimal" are optional.
  - _Checkbox_: A GUI element for _BooleanValue_. 
  - _Fileupload_: not yet documented!
- _gui_attributes_: See above

### Resources
The resource classes are the primary entities of the data model. A resource class
is a template for the representation of a real object that is represented in
the DaSCh database. A resource class defines properties (aka _data fields_). For each of
these properties a data type as well as the cardinality have to defined.

A resource consists of the following definitions:

- _name_: A name for the resource
- _label_: The string displayed of the resource is being accessed
- _super_: A resource class is always derived from an other resource. The
  most generic resource class Knora offers is _"Resource"_. The following
  parent predefined resources are provided by knora:
  - _Resource_: A generic "thing" that represents an item from the reral world
  - _StillImageRepresentation_: An object that is connected to a still image
  - _TextRepresentation_: An object that is connected to an (external) text (Not Yet Implemented)
  - _AudioRepresentation_: An object representing audio data (Not Yet Implemented)
  - _DDDRepresentation_: An object representing a 3d representation (Not Yet Implemented)
  - _DocumentRepresentation_: An object representing a opaque document (e.g. a PDF)
  - _MovingImageRepresentation_: An object representing a moving image (video, film)
  - _Annotation_: A predefined annotation object. It has the following properties
  defined:
    - _hasComment_ (1-n), _isAnnotationOf_ (1)
  - _LinkObj_: An resource class linking together several other, generic, resource classes. The class
  has the following properties: _hasComment_ (1-n), _hasLinkTo_ (1-n)
  - _Region_: Represents a simple region. The class has the following properties:
  _hasColor_ (1), _isRegionOf_ (1) _hasGeometry_ (1), _isRegionOf_ (1), _hasComment_ (0-n)
  
- _cardinalities: Array of references to the properties that the resource may hold including the
   cardinality. A cardinality has the following properties:
   - _propname_: The of the property. If its used in the form ":"propname, the current ontology is
     references, if the ":" is omitted, a knora standard ontology is refrences, otherwise the full
     prefix of the ontology has to be used.
   - _gui_order_: An integer number which will help the GUI to display the properties in the desired
     order
   - _cardinality_: Indicates how often a given property may occur. The possible values
     are:
     - "1": Exactly once (mandatory one value and only one)
     - "0-1": The value may be omitted, but can occur only once
     - "1-n": At least one value must be present. But multiple values may be present.
     - "0-n": The value may be omitted, but may also occur multiple times.
   
   The cardinality 

Example:

```json
"resources": [
          {
            "name": "Schule",
            "super": "Resource",
            "labels": {
              "de": "Schule"
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
          }]
```
