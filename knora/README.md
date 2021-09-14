# Knora Library

This library offers classes and methods to manipulate a Knora based repository. Most importantly, it allows importing data by
providing methods to create new ontologies and resources.

## Contents

- [Basic methods](#basic-methods)
    - [Knora()](#knora)
    - [login()](#login)
    - [logout](#logout)
- [Project methods()](#project-specific-methods)
    - [get_existing_projects()](#get_existing_projects)
    - [get_project()](#get_project)
    - [project_exists()](#project_exists)
    - [create_project()](#create_project)
    - [update_project()](#update_project)
    - [get_users()](#get_users)
    - [create_user()](#create_user)
    - [add_user_to_project()](#add_user_to_project)
- [Ontology methods](#ontology-methods)
    - [get_existing_ontologies()](#get_existing_ontologies)
    - [get_project_ontologies()](#get_project_ontologies)
    - [ontology_exists()](#ontology_exists)
    - [get_ontology_lastmoddate()](#get_ontology_lastmoddate)
    - [create_ontology()](#create_ontology)
    - [delete_ontology()](#delete_ontology)
    - [get_ontology_graph()](#get_ontology_graph)
    - [create_res_class()](#create_res_class)
    - [create_property()](#create_property)
    - [create_cardinality()](#create_cardinality)
- [Lists](#lists)
    - [create_list_node()](#create_list_node)
    - [get_lists()](#get_lists)
    - [get_complete_list()](#get_complete_list)
- [Creating instances](#creating-instances)
    - [create_resource()](#create_resource)
        - [values parameter](#values-parameter)
        - [Stillimage parameter](#stillimage-parameter)
- [Other methods](#other-methods)
    - [create_schema()](#create_schema)
    - [reset_triplestore_content()](#reset_triplestore_content)
- [SIPI](#sipi)
    - [Sipi()](#Sipi)
    - [upload_image()](#upload_image)
- [BulkImport](#bulkImport)
    - [Bulkimport()](#bulkimport)
    - [add_resource()](#add_resource)
    - [upload()](#upload)

## Knora

Knora is the base class which handles all the communication with the DSP API. In order to use Knora, the user has to submit
his/her credentials to the DSP API

### Basic methods

#### Knora()

Creates an access object for Knora.

```python
Knora(
    server: str,
    prefixes: Dict[str, str] = None)
```

- server: URL of the Knora API server
- prefixes: List of extra RDF prefixes that are being used

Example:

```
con = Knora(args.server)
```

#### login()

This method performs a login and stored the access token.

```python
login(email: str, password: str)
```

- email: Email address of user
- password: Password of user

Example:

```
con.login(args.user, args.password)
```

#### logout()

This method is used to log out from Knora and remove the access token.

```python
logout()
```

Example:

```
con.logout()
```

### Project specific methods

The following methods are used to add and modify projects and users

#### get_existing_projects()

Returns a list of all projects. Usually returns only the IRI's. If full ist true, returns all information.

```python
get_existing_projects(full: bool = False)
``` 

- full: if True, returns not only ontology IRI's

#### get_project()

Returns information about a project given its shortcode.

```python
get_project(shortcode: str) -> dict
```

#### project_exists()

Returns true if a project given by the IRI is existing in the repository.

```python
project_exists(proj_iri: str) -> bool
```

- proj_iri: IRI of the project

#### create_project()

This method is used to create a new project.

```python
create_project(
        shortcode: str,
        shortname: str,
        longname: str,
        descriptions: Optional[Dict[str, str]] = None,
        keywords: Optional[List[str]] = None,
        logo: Optional[str] = None) -> str
```

- shortcode: The Knora short code of the project
- shortname: The short name of the project
- longname: The long name of the project
- descriptions: [optional] Dict with the language code (e.g. "en", "de"...) as key
- keywords: [optional] List of keywords
- logo: [optional] Path to logo file (the logo must be already on the server)

#### update_project()

This method is used to modify existing project data. All parameters except the shortcode (which cannot be changed)
are optional.

```python
update_project(
        shortcode: str,
        shortname: str,
        longname: str,
        descriptions: Optional[Dict[str, str]] = None,
        keywords: Optional[List[str]] = None,
        logo: Optional[str] = None) -> str
```

- shortcode: The Knora short code of the project
- shortname: The short name of the project
- longname: The long name of the project
- descriptions: [optional] Dict with the language code (e.g. "en", "de"...) as key
- keywords: [optional] List of keywords
- logo: [optional] Path to logo file

#### get_users()

Get all users

```
get_users()
```

#### get_user()

Get information about a specific user

```python
get_user(user_iri: str)
```

- user_iri: Knora IRI identifying the user

#### create_user()

Creates a new user and returns its IRI.

```python
create_user(
        username: str,
        email: str,
        givenName: str,
        familyName: str,
        password: str,
        lang: str = "en")
```

- username: Username (short name)
- email: Email address of user – is used to identify the user
- givenName: First name of the user
- familyName: Family name of the user
- password: Password
- lang: [optional] Language code of default language

#### add_user_to_project()

Add an existing user to a project.

```python
add_user_to_project(
        user_iri: str,
        project_iri: str)
```

- user_iri: IRI of the user
- project_iri: IRI of the project

### Ontology methods

Since several instances could modify an ontology at the same time, a simple mechanism has been implemented to avoid race
conditions:
Each modification of an ontology requires the timestamp of its last modification time. Each manipulation of an ontology returns
its new modification time. If the ontology has been modified before an update is submitted, the submitted modification time will
not fit and the modification is rejected.

Many methods need the ontology IRI and the ontology name – the reason for this are performance issues which eliminate a round trip
to the Knora backend.

#### get_existing_ontologies()

Get short information about all ontologies existing.

```python
get_existing_ontologies()
```

#### get_project_ontologies()

Returns the ontologies of a given project.

```python
get_project_ontologies(project_code: str) -> Optional[dict]
```

- project_code: Short code of project

#### ontology_exists()

Tests if an ontology exists.

```python
ontology_exists(onto_iri: str)
```

- onto_iri: IRI of the ontology

#### get_ontology_lastmoddate()

Get the last modification date of a given ontology.

```python
get_ontology_lastmoddate(self, onto_iri: str)
```

- onto_iri: IRI of the ontology

#### create_ontology()

Create a new ontology.

```python
create_ontology(
        onto_name: str,
        project_iri: str,
        label: str
) -> Dict[str, str]
```

- onto_name: Name of the ontology
- project_iri: IRI of the project the ontology belongs to
- returns: Dict with "onto_iri" and "last_onto_date"

#### delete_ontology()

Deletes the given ontology.

```python
delete_ontology(
        onto_iri: str
        last_onto_date = None)
```

- onto_iri: IRI of the ontology
- last_onto_date: Timestamp of the last modification of the ontology. It cannot be deleted if the given timestamp doesn't fit.

#### get_ontology_graph()

Get the whole ontology as RDF (text/turtle).

```python
get_ontology_graph(
        shortcode: str,
        name: str)
```

- shortcode: Short code of the project
- name: Name of the ontology

#### create_res_class()

Create a new resource class in the ontology.

```python
create_res_class(
        onto_iri: str,
        onto_name: str,
        last_onto_date: str,
        class_name: str,
        super_class: List[str],
        labels: Dict[str, str],
        comments: Optional[Dict[str, str]] = None
) -> Dict[str, str]
```

- onto_iri: IRI of the ontology the new resource class should be added to
- onto_name: Name of the ontology
- last_onto_date: Last modification time of ontology
- class_name: Name of the new class
- super_class: A list of super classes this class is derived from. Usually this is just "Resource" for "knora-api:Resource" or
  another resource class including the prefix.
- labels: Dict with the language specific labels, e.g. ```{"en": "English label", "de": "German label"}```.
- comments: [optional] Dict with language specifics comments to the resource class.

#### create_property()

Create a new property.

```python
create_property(
        onto_iri: str,
        onto_name: str,
        last_onto_date: str,
        prop_name: str,
        super_props: List[str],
        labels: Dict[str, str],
        gui_element: str,
        gui_attributes: List[str] = None,
        subject: Optional[str] = None,
        object: Optional[str] = None,
        comments: Optional[Dict[str, str]] = None
) -> Dict[str, str]
```

- onto_iri: IRI of the ontology.
- onto_name: Name of the ontology.
- last_onto_date: Last modification time of ontology.
- prop_name: Name of the property to be created
- super_props: List of super-properties, must be at least ```[knora-api:hasValue]```. But it is possible to declare a property to
  be a descendant from another property from another ontology or from an external ontology (e.g. foaf:familyName). Please note
  that all the prefixes used have to be declared at the construction of the Knora instance.
- labels: Dict of language dependent labels (```{"en": "English label", "de": "Deutsches Label"```).
- gui_element: GUI element dependent on object (data type). They are a hint for a (generic) graphical user interface (e.g. SALSAH)
  on how to display the field. Available GUI elements are:
    - salsah-gui:Colorpicker (attributes: ncolors='integer')
    - salsah-gui:Date
    - salsah-gui:Geometry
    - salsah-gui:Geonames
    - salsah-gui:Interval
    - salsah-gui:List (attributes [required]: hlist='iri')
    - salsah-gui:Pulldown (attributes [required]: hlist='iri')
    - salsah-gui:Radio (attributes [required]: hlist='iri')
    - salsah-gui:Richtext
    - salsah-gui:Searchbox (attributes: numprops='integer')
    - salsah-gui:SimpleText (attributes: maxlength='integer', size='integer')
    - salsah-gui:Slider (attributes [required]: max='decimal', min='decimal')
    - salsah-gui:Spinbox (attributes: max='decimal', min='decimal')
    - salsah-gui:Textarea (attributes: cols='integer', rows='integer', width='percent'%, wrap="soft"|"hard")
    - salsah-gui:Checkbox
    - salsah-gui:Fileupload
- gui_attributes: see above
- subject: [optional] The resource the property belongs to. If a resource is used by several resourced, this field can b left
  empty.
- object: The value type the property points to, e.g. "TextValue", "IntValue" etc. (all value types supportted by Knora). The
  following object types are supported by Knora:
    - salsah-gui:TextValue (gui_element: salsah-gui:SimpleText, salsah-gui:TextArea) A simple text value
    - salsah-gui:ColorValue (gui_element: salsah-gui:Colorpicker) A web-color.
    - salsah-gui:DateValue (gui_elment: Date): A Knora calendar date.
    - salsah_gui:DecimalValue (gui_element: salsah-gui:SimpleText) A Decimal value.
    - salsah_gui:GeomValue (gui_element: salsah-gui:Geometry) A geometry (region in an image)
    - salsah_gui:GeonameValue (gui_element: salsah-gui:Geonames) A geographical locatiuoin identified by a geonames.org code.
    - salsah_gui:IntValue (gui_element: salsah-gui:SimpleText, salsah-gui:Slider, salsah-gui:Spinbox) An integer value.
    - salsah_gui:BooleanValue (gui_element: salsah-gui:Checkbox) A boolean value.
    - salsah_gui:UriValue (gui_element: salsah-gui:SimpleText) An URI.
    - salsah_gui:IntervalValue (gui_element: No Yet Implemented) An interval or time span.
    - salsah_gui:ListValue (gui_element: salsah-gui:Pulldown, salsah-gui:Radio, salsah-gui:List) An entry from a list.
- comments: [optional] Dict with language specifics comments to the resource class.

#### create_cardinality()

Associates a property with a given resource and indicates the cardinality restriction.

```python
create_cardinality(
        onto_iri: str,
        onto_name: str,
        last_onto_date: str,
        class_iri: str,
        prop_iri: str,
        occurrence: str
) -> Dict[str, str]
```

- onto_iri: IRI of the ontology.
- onto_name: Name of the ontology.
- last_onto_date: Last modification time of ontology.
- class_iri: IRI of the resource class the property should be associated with.
- prop_iri: IRI of the property to be associated with the resource class.
- occurrence: must be one of: "1", "0-1", "0-n" or "1-n" (as string).

### Lists

Lists (flat or hierarchical) are ordered named nodes that can be used to describe controlled vocabularies, selections or
hierarchical thesauri. A list has a root node which gives the list a name. Subnodes define the list elements. In case of
hierarchical lists a subnode may hold further subnodes (recursively).  
Lists are associated with a project.

#### create_list_node()

Creates a list node (root or subnode, depending on parameters).

```python
create_list_node(
        project_iri: str,
        labels: Dict[str, str],
        comments: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        parent_iri: Optional[str] = None
) -> str
```

- project_iri: The IRI of the project the list is associated with
- labels: Language dependent labels, e.g. ```{"en": "yes", "de": "nein"}```.
- comments: Language dependent comments to the node
- parent_iri: If None, it is a root note, otherwise the IRI of the parent list node (possibly the root note of the list).

#### get_lists()

Get information about the lists of a given project

```python
get_lists(
        shortcode: str
) -> Dict
```

- shortcode: Short code of the project.

#### get_complete_list()

Get all the data (nodes) of a specific list

```python
get_complete_list(
        list_iri: str
) -> Dict
```

- list_iri: IRI of the list.

### Creating instances

In order to fill the repository with data, resource instances have to be created.

#### create_resource()

This Method is used to create a new instance of a given resource. All the data has to be passed to this function.

```python
create_resource(
        schema: Dict,
        res_class: str,
        label: str,
        values: Dict,
        stillimage = None
) -> Dict
```

- schema: The schema is a Dict that contains information about the ontology. It will by created by a call to "create_schema()",
  e.g. ```schema = con.create_schema(args.projectcode, args.ontoname)```. It is used to validate the data supplied to
  create_resource for consistency with the ontology.
- res_class: IRI of the resource class that should be instanciated
- label: A string describing the instance
- values: a Dict describing all the values. See description below.
- stillimage: In case the Resource is a descendant of StillImagerepresentation, this parameter is indicating where the uploaded
  file is to be found. See below

##### Values parameter

The values are a Dict in the form:

```python
{
    "propertyname": value,
    "propertyname": value,
    ...
}
```

If the property belongs to the same ontology as the resource, the prefix should be omitted. The value can either be a string or a
Dict of the following form:

```python
{
    "value": "the value",
    "comment": "a comment to the value"
}
```

_Note_: If the value is text with markup (standard mapping only allowed), then the value must be an instance of KnoraStandoffXml,
e.g.:

```python
   ...
"richtextprop": {
    'value': KnoraStandoffXml(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<text><p><strong>this is</strong> text</p> with standoff</text>"),
    'comment': "Text with Markup"
},
...
```

##### Still image parameter:

A still image has to be uploaded to Knora before its SillImageRepresentation instance can be created:

```python
sipi = Sipi(args.sipi, con.get_token())
img = sipi.upload_image("example.tif")
...
an_image = con.create_resource(schema,
                               "object2",
                               {
                                   "titleprop": "Stained glass",
                                   "linkprop": inst1_info['iri']
                               },
                               img['uploadedFiles'][0]['internalFilename']
                               )
```

### Other methods

#### create_schema()

This method extracts the ontology from the ontology information it gets from Knora. It gets the ontology information as n3-data
using the Knora API and concerts into a convenient python dict that can be used for further processing. It is required by the bulk
import processing routines and be create_resource().

```python
create_schema(
        shortcode: str,
        shortname: str
) -> Dict
```

- shortcode: Shortcode of the ontology
- shortname: Shortname of the ontology

#### reset_triplestore_content()

Empty the triple store. _Use with uttermost caution_  
Used on local test servers to clean up the local backend.

## SIPI

Sipi is the IIIF conformant image backend.

### Methods of Sipi class

#### Sipi()

Constructor for Sipi

```python
Sipi(
    sipiserver: str,
    token: str
)
```

- sipiserver: URL of the SIPI server/endpoint
- token: Access token from Knora

Example:

```python
sipi = Sipi(args.sipi, con.get_token())
```

#### upload_image()

Uploads an image to the SIPI server.

```
upload_image(
  filepath: str
) -> Dict
```

- filepath: Path to file on local filesystem. J2K, TIF, JPEG and PNG images are supported.

## Bulk import

The bulk import is used to import multiple resources at once.

### BulkImport

The BulkImport class handles the bulk import

#### Bulkimport()

Constructor of a BulkImport instance

```python
Bulkimport(
        schema: Dict
) -> Bulkimport
```

- schema: see create_schema()

#### add_resource()

Add an instance to the bulk import.

```python
add_resource(
        resclass: str,
        id: str,
        label: str,
        properties: Dict
)
```

- resclass: Name of resource class (prefix may be omitted)
- id: a user defined ID that can be used to reference this resource by later resources.
- label: String desribing the instance
- properties: Dict of property name/value pairs.

#### upload()

Upload the data using the bulk import route.

```python
upload(
        user: str,
        password: str,
        hostname: str,
        port: int
)
```

- user: username
- password: Password
- hostname: Hostname of Knora backend
- port: Port number the Knora backend uses
