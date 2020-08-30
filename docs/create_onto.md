[![PyPI version](https://badge.fury.io/py/knora.svg)](https://badge.fury.io/py/knora)

# knora-create-ontology

`knora-create-ontology` creates an ontology. Furthermore, the script reads a JSON file containing the data model (ontology) definition, connects to the Knora server and creates the data model.

## Usage

```bash
$ knora-create-ontology data_model_definition.json
```
The JSON file supports the following options:

- _"-s server" | "--server server"_: URL of the Knora server [default: localhost:3333].
- _"-u username" | "--user username"_: Username to log into Knora [default: root@example.com].
- _"-p password" | "--password password"_: Password for login to the Knora server [default: test].
- _"-v" | "--validate"_: If this flag is set, only the validation of the JSON runs.
- _"-l" | "--lists"_: This only creates the lists using a [simplified schema](#json-for-lists). Please note
  that in this case the project __must__ exist.

## JSON ontology definition format

### Introduction
This documentation holds any relevant informations you need to know how to create an ontology that's used by Knora.

In the first section you find a rough overview of the ontology definition, all the necessary components with a definition and a short example of the definition.

### A short overview
In the following section, you find all the mentioned parts with a detailed explanation. Right at the beginning we look at the basic fields that belong to an ontology definition. This serves as an overview for you to which you can return at any time while you read the description.

A complete ontology definition looks like this:

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "project": {
    "shortcode": "0123",
    "shortname": "BiZ",
    "longname": "Bildung in Zahlen",
    "descriptions": {},
    "keywords": [],
    "lists": [],
    "groups": [],
    "users": [],
    "ontologies": []
  }
}
```
Doubtless, you see that only two umbrella terms define our ontology: the "prefixes" object and the "project" object. In the following we take a deeper look into both of them since, as you can see in the example above, 
both objects have further fine grained definition levels.


#### "Prefixes" object
The "prefixes" object contains - as you may already have guessed by the name - the `prefixes` of *external* ontologies that are also used in the current project. All prefixes are composed of a keyword, followed by its iri. This is used as a shortcut for later so that you don't always have to specify the full qualified iri but can use the much shorter keyword instead. That means that e.g. instead of addressing a property called "familyname" via `http://xmlns.com/foaf/0.1/familyName` you can simply use foaf:familyName. 

As you can see in the example below, you can have more then one prefix too. In the example we have "foaf" as well as "dcterms" as our prefixes.

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  }
}
```

#### "Project" object

Right after the "prefix" object the "project" object has to follow, which contains all resources and properties of the ontology. The "project" object is the bread and butter of the ontology. All its important properties are specified therein. 

As you saw in the complete ontology definition in the beginning, the project definitions requires ***exactly*** all of the following datafields:

- shortcode
- shortname
- longname
- keywords
- ontologies

Whereas the following fields are optional (if one or more of these fields are not
used, it must be omitted):

- descriptions
- lists
- groups
- users

So a simple example definition of the "project" object could look like this:
  
```json
"project": {
   "shortcode": "0809",
   "shortname": "test" ,
   "longname": "Test Example",
   "descriptions": {
     "en": "This is a simple example project",
     "de": "Dies ist ein einfaches Beispielprojekt"
   }
   "keywords": ["example", "simple"],
   "lists": […],
   "groups": […],
   "users": […],
   "ontology": {…}
}
```

 
### Simple key/value pairs
At that point we will go through all of this step by step and take a more in depth view on the individual fields of the "project" object. The first four fields of the "project" object are "key"/"value" pairs. Therefore they are quite simple. 

#### Shortcode

It's a hexadecimal string in the range between "0000" and "FFFF" that's used to uniquely identifying the project. The shortcode has to be provided by the DaSCH.

#### Shortname

This is a short name (string) for the project. It's ment to be like a nickname. If the name of the project is e.g. "Albus Percival Wulfric", then the shortname for it could be "Albi".

#### Longname

A longer string that provides the full name of the project. In our example, the longname would be "Albus Percival Wulfric".

#### Descriptions

The descriptions specify the content of the project in *exactly* one or more strings. These descriptions can be supplied in several languages (currently _"en"_, _"de"_, _"fr"_ and _"it"_ are supported). The descriptions have to be given as a JSON object with the language as "key" and the description as "value".  See the example above inside the curly brackets after "descriptions" to see what that means.

### Key/object pairs
The following fields are **not** simple "key"/"value" pairs. They do have a key, the value however is another object and therefore has an internal structure. Due to the increased complexity of these objects, they are looked at in more detail.

#### Keywords

An array of keywords is used to roughly describe the project in single words. A project that deals e.g. with old monastery manuscripts could possess the keywords "monastery", "manuscripts", "medieval", (...). The array can be empty as well e.i. "keywords": [].

#### Lists 
<!--- Hier sollte eine *gutes" Beispiel aus den GW rein! --->
An array contains flat or hierarchical ordered terms. For example these terms 
are used to further define the scope of the project. If your project is all about letters written in different paper formats, then use a list that contains the terms ["A4", A3", "A2", "A1"]. This would be ordered hierarchically. If your project is about diplomatic texts between the different cantons, then use a list such as ["BL", "BS", "VS", ...]. This would be a flat list. And as before the list array can be empty as well.

A list consists of a root node identifing the list and an array of subnodes.
Each subnode may contain again subnodes (hierarchical list).
A node has the following elements:

- _name_: Name of the node. This should be unique for the given list.
- _labels_: Language dependent labels in the form ```{ "<lang>": "<label>, ... }```
- _comments_: Language dependent comments (optional) in the form ```{ "<lang>": "<comment>, ... }```
- _nodes_: Array of subnodes. This is optional – leave it out if there are no subnodes. That is a flat list.

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
As already mentioned before, the _lists_ element is optional. If there are no lists, this element has to be omitted.

#### Groups

This object contains _groups_-definitions. This is (only) used to specify the permissions a user gets. A project may define user groups such as "project-admins", "students" etc. and give the members of each group individual permissions.

A _group_-defintion has the following elements:
- _name_: The name of the group.
- _description_: Description of the purpose of the group.
- _selfjoin_: True, if users are able to join the group; false, if an administrator must add the users.
- _status_: Has the value true if the group is active and false if the group is not active.

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
The _groups_ element is optional and can therefore be left out.

#### Users

This object contains _user_-definitions. You can set user traits here. A user has the following elements:
- _username_: The short username for the login. Similar to a nickname. 
- _email_: Unique email that identifies the user.
- _givenName_: Firstname of the user.
- _familyName_: Surname of the user.
- _password_: Password of the user.
- _lang_: The preferred language of the user: "en", "de", "fr", "it" [optional, default: "en"].
- _projects_: List of projects the user belongs to.

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
The _users_ element is optional and can therefore be omitted.

#### Ontology

Most of the definitions for our ontology will be done under the category "ontology": {} inside of the curly brackets. 
This is the core of the ontology definition. We know, you've already read a whole lot of text so far, but this section is probably the most important one.

Firstly lets talk about what an ontology actually is. This is necessary so that afterwards it will get easier to understand, what the different fields of the ontology definition do. 

An ontology is a formally ordered representation of a set of terminologies. Dependencies, relationships and relations between the individual components of the set are recorded and noted in a logical, formal language. In contrast to a 
taxonomy, which defines a mere hierarchical structure within a range of terms, an ontology is much more a network of information of logical dependencies of term elements. 
 
A full-fledged ontology thus has to offer at least *two* things: a set of objects or terms (called resources) - the actual elements of the terminology set - as well as dependency rules that describe the dependencies of the individual resources between one and another (called properties). 

To fully capture everything an ontology has to provide, we use *four* different elements that describe the resources as well as the dependencies inside our ontology. They are: 

- _name_
- _label_
- _properties_
- _resources_

Example:
```json
    "ontology": {
      "name": "seworon",
      "label": "Secrets of the world ontology",
      "properties": […],
      "resources": […]
    }
```
Now lets see what each field does.

#### Name

First of all, our overall ontology needs a name. After all, we want to create a ontology about a specific subject or set of terms. 

As a "speciality", the *name of the ontology* has to be a NCNAME conformant name that can be used as prefix. NCNAME means that it has to be a single word without any special characters (like e.g. " . : ! ? # + (...) ") and without any blanks. 

#### Label

Since the "name" of your ontology needs to be in this special format, we like to have a human readable and understandable name of the ontology. This is done in the "label".

#### Properties

At first, it seems a bit illogical to have to define the properties *before* the resources. After all, a property always describes the characteristics of a *resource*. However, it is necessary to define the properties *before* the 
resources. The reason for that is that a property - a dependency between resources - can be used in our program not only for a single resource but for several. If we would e.g. have a property that describes "is descendent of", we can use this property not only to describe the family relations of a human family but at the same time use the same property to describe the relations of e.g. an animal family. 

A properties-array describes all the properties that are used for our terminology space. It's all the properties that describe all the possible connections and dependencies between our entire set of terms.

The following should also be mentioned: We are restricted to a list of properties, we can choose from. We can't create our own "new" properties. However, the list is exceptionally large and should cover all the needs for properties we want to choose for our ontology.

A property has mandatory and optional fields. The following fields are mandatory:
- _name_
- _labels_
- _object_
- _gui_element_

The following fields are optional (can be omitted):
- _super_
- _gui_attributes_

*name*

A name for the property e.g. "idesof"

*labels*

Use language dependent, human readable names e.g. "is descendent of".
The labels-field has the following form: `{ "<lang>": "<value>", …}`
where `<lang>` is either "en", "de", "fr" or "it", and `<value>` is a string.
    
*object*

The "object" defines the data type of the value that the property will store.
  The following object types are allowed:
  - `TextValue`: Represents a text that may contain standoff markup  
    *gui\_elements / gui\_attributes*:
    - `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes are:
      _gui_attributes_:
      - `maxlength=integer` (optional): Maximal length (number of character accepted)
      - `size=integer` (optional):  Size (width) of widget
    - `Textarea`: A GUI element for _TextValue_. Presents a multiline text entry box. The optional attributes are:  
      _gui_attributes_:
      - `cols=integer` (optional): Number of cols of the text area
      - `rows=integer` (optional): Number of rows of the text area
      - `width=percent` (optional): Width of the field on screen
      - `wrap=soft|hard` (optional): Wrapping of text
    - `Richtext`: A GUI element for _TextValue_. Provides a rich text editor.
      - _gui_attributes_: No attributes
      
  - `ColorValue`: A string in the form "#rrggbb" (standard web color format)  
    *gui-elements / gui_attributes*:
    - `Colorpicker`: The only GUI element for _ColorValue_. 
      _gui_attributes_:
      - `ncolors=integer` (mandatory): Number of colors the color picker should present
      
  - `DateValue`: represents a date. It's a string with the format `calendar:start:end`
    - _calender_ is either _GREGORIAN_ or _JULIAN_
    - _start_ has the form _yyyy_-_mm_-_dd_. If only the year is given, the precision is to the year. If only the year and month is given, the precision is to the month.
    - _end_ is optional if the date represents a clearly defined period or uncertainty.  
  
    In total, a DateValue has the following form: "GREGORIAN:1925:1927-03-22"
    which means anytime in between 1925 and the 22nd March 1927.  
    *gui-elements / gui_attributes*:
    - `Date`: The only GUI element for _DateValue_. A date picker gui.  
      _gui_attributes_: No attributes
      
  - `DecimalValue`: A number with decimal point  
    *gui-elements / gui_attributes*:
    - `Slider`: A GUI element for _DecimalValue_. Provides a slider to select a decimal value.  
      _gui_attributes_:
      - `max=decimal` (mandatory): Maximal value
      - `min=decimal` (mandatory): Minimal value
    - `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
      "maxlength=integer" and "size=integer" are optional.  
      _gui_attributes_:
      - `maxlength=integer` (optional): The maximum number of characters accepted
      - `size=integer"` (optional): The size of the input field
      
  - `GeomValue`: Represents a geometrical shape as JSON.  
    *gui-elements / gui_attributes*:
    - `Geometry`: Not Yet Implemented.  
      _gui_attributes_: No attributes
    - `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
      "maxlength=integer" and "size=integer" are optional.  
      _gui_attributes_:
      - `maxlength=integer` (optional): The maximum number of characters accepted
      - `size=integer"` (optional): The size of the input field
      
  - `GeonameValue`: Represents a location ID in geonames.org  
    *gui-elements / gui_attributes*:
    - `Geonames`: The only GUI element for _GeonameValue_. Interfaces with geonames.org allow to select a location  
      _gui_attributes_: No attributes
      
  - `IntValue`: Represents an integer value  
    *gui-elements / gui_attributes*:
    - `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
      "maxlength=integer" and "size=integer" are optional.  
      _gui_attributes_:
      - `maxlength=integer` (optional): The maximum number of characters accepted
      - `size=integer"` (optional): The size of the input field
    - `Spinbox`: A GUI element for _IntegerValue_. A text field with and "up"- and "down"-button for
      increment/decrement. The attributes "max=decimal" and "min=decimal" are optional.  
      _gui_attributes_:
      - `max=integer` (optional): Maximal value
      - `min=integer` (optional): Minimal value
      
  - `BooleanValue`: Represents a Boolean ("true" or "false)  
    *gui-elements / gui_attributes*:
    - `Checkbox`: A GUI element for _BooleanValue_.  
      _gui_attributes_: No attributes
      
  - `UriValue`: : Represents an URI  
    *gui-elements / gui_attributes*:
    - `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
      "maxlength=integer" and "size=integer" are optional.  
      _gui_attributes_:
      - `maxlength=integer` (optional): The maximum number of characters accepted
      - `size=integer"` (optional): The size of the input field
      
  - `IntervalValue`: Represents a time-interval  
    *gui-elements / gui_attributes*:
    - `SimpleText`: A GUI element for _TextValue_. A simple text entry box (one line only). The attributes
      "maxlength=integer" and "size=integer" are optional.  
      _gui_attributes_:
      - `maxlength=integer` (optional): The maximum number of characters accepted
      - `size=integer"` (optional): The size of the input field
    - `Interval`: Not Yet Implemented.  
      _gui_attributes_: No attributes
      
  - `ListValue`: Represents a node of a (possibly hierarchical) list  
    *gui-elements / gui_attributes*:
    - `Radio`: A GUI element for _ListValue_. A set of radio buttons. This works only with flat lists!  
      _gui_attributes_:
      - `hlist=<list-name>` (mandatory): The reference of a [list](#lists) root node
    - `List`: A GUI element for _ListValue_. A list of values to select one from.  
      _gui_attributes_:
      - `hlist=<list-name>` (mandatory): The reference of a [list](#lists) root node
    - `Pulldown`: A GUI element for _ListValue_. Pulldown for list values. Works also for hierarchical lists.  
      _gui_attributes_:
      - `hlist=<list-name>` (mandatory): The reference of a [list](#lists) root node
      
  - `LinkValue`: Represents a link to another resource  
    *gui-elements/gui_attributes*:
    - `Searchbox`: Must be used with _hasLinkTo_ properties. Allows to search and enter a resource that the
      given resource should link to. 
      It has one gui_attribute that indicates how many properties of the found resources should be indicated.
      It's mandatory!  
      _gui_attributes_:
      - `numprops=integer` (mandatory): While dynamically displaying the search result, the number of properties that
        should be displayed.

  - `--`: Not yet documented  
    *gui-elements/gui_attributes*:
    - `Fileupload`: not yet documented!  
    _gui_attributes_: No attributes

*super*

A property ***must*** be derived from at least one base property. The most generic base property that Knora offers is _hasValue_. In addition the property may be a subproperty of properties defined in external ontologies. In this case the qualified name - including the prefix - has to be given.
  The following base properties are defined by Knora:
  - `hasValue`: This is the most generic base.
  - `hasLinkTo`: This value represents a link to another resource. You have to indicate the "_object_" as a prefixed IRI that identifies the resource class this link points to.
  - `hasColor`: Defines a color value (_ColorValue_)
  - `hasComment`: Defines a "standard" comment
  - `hasGeometry`: Defines a geometry value (a JSON describing a polygon, circle or rectangle), see _ColorValue_
  - `isPartOf`: A special variant of _hasLinkTo_. It says that an instance of the given resource class is an integral part of another resource class. E.g. a "page" is part of a "book".
  - `isRegionOf`: A special variant of _hasLinkTo_. It means that the given resource class is a "region" of another resource class. This is typically used to describe regions of interest in images.
  - `isAnnotationOf`: A special variant of _hasLinkTo_. It denotes the given resource class as an annotation to another resource class.
  - `seqnum`: An integer that is used to define a sequence number in an ordered set of instances.

Example for a properties definition:
````json
        "properties": [
          {
            "name": "schulcode",
            "object": "TextValue",
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

````
#### Resources
The resource classes are the primary entities of the data model. They are the actual objects/terms inside our terminology space. A resource class is a template for the representation of a real object that is represented in the DaSCH database. A resource class defines properties (aka _data fields_). For each of these properties a data type as well as the cardinality have to defined.

A resource needs to have the following fields:

#### _name_
A name for the resource.
#### _label_
The string displayed of the resource is being accessed.
#### _super_
A resource class is always derived from an other resource. The most generic resource class Knora offers is _"Resource"_. 
The following parent predefined resources are provided by Knora:
  - _Resource_: A generic "thing" that represents an item from the real world
  - _StillImageRepresentation_: An object that is connected to a still image
  - _TextRepresentation_: An object that is connected to an (external) text (Not Yet Implemented)
  - _AudioRepresentation_: An object representing audio data (Not Yet Implemented)
  - _DDDRepresentation_: An object representing a 3-D representation (Not Yet Implemented)
  - _DocumentRepresentation_: An object representing an opaque document (e.g. a PDF)
  - _MovingImageRepresentation_: An object representing a moving image (video, film)
  - _Annotation_: A predefined annotation object. It has the following properties
  defined:
    - _hasComment_ (1-n), _isAnnotationOf_ (1)
  - _LinkObj_: A resource class linking together several other, generic, resource classes. The class
  has the following properties: _hasComment_ (1-n), _hasLinkTo_ (1-n)
  - _Region_: Represents a simple region. The class has the following properties:
  _hasColor_ (1), _isRegionOf_ (1) _hasGeometry_ (1), _isRegionOf_ (1), _hasComment_ (0-n)
  
- _cardinalities_: Array of references to the properties that the resource may hold including the
   cardinality. A cardinality has the following properties:
   - _propname_: The name of the property. If it's used in the form ":"propname, the current ontology is referenced. If the ":" is omitted, a Knora standard ontology is referenced, otherwise the full prefix of the ontology has to be used.
   - _gui_order_: An integer number which will help the GUI to display the properties in the desired
     order
   - _cardinality_: Indicates how often a given property may occur. The possible values
     are:
     - "1": Exactly once (mandatory one value and only one)
     - "0-1": The value may be omitted, but can occur only once
     - "1-n": At least one value must be present. But multiple values may be present
     - "0-n": The value may be omitted, but may also occur multiple times
   
Example for a resource definition:
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
