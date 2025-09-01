[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# JSON Project Definition Format

This document describes the structure of a JSON project definition file 
that can be uploaded to a DSP server
with the [`create`](../../cli-commands.md#create) command.

A project on a DSP server is like a container for data. 
It defines some basic metadata, the data model(s) 
and optionally the user(s) who will be able to access the data. 
After the creation of a project, 
data can be uploaded that conforms with the data model(s).

This documentation is divided into the following parts:

- Overview of the project description file (this page)
- [The "ontologies" section](./ontologies.md) explained in detail
- Some [caveats](./caveats.md) to have in mind



## A Short Overview

A complete project definition looks like this:

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json",
  "project": {
    "shortcode": "0123",
    "shortname": "BiZ",
    "longname": "Bildung in Zahlen",
    "descriptions": {
      "en": "This is a simple example project",
      "de": "Dies ist ein einfaches Beispielprojekt"
    },
    "keywords": [
      "example",
      "simple"
    ],
    "enabled_licenses": [
        ...
    ],
    "default_permissions": "public|private",
    "default_permissions_overrule": {
        "private": [...],
        "limited_view": "all" | [...],
    }
    "groups": [
      ...
    ],
    "users": [
      ...
    ],
    "lists": [
      ...
    ],
    "ontologies": [
      ...
    ]
  }
}
```



### `prefixes`

(optional)

`"prefixes": { "prefix": "<iri>", ...}`

The `prefixes` object contains the prefixes of external ontologies that are used in the current file. All prefixes
are composed of the prefix and a URI. The prefix is used as namespace, so one does not have to write the
fully qualified name of the referenced object each time it is used. Instead of writing a property called `familyName` 
as `http://xmlns.com/foaf/0.1/familyName` one can simply write `foaf:familyName`.

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  }
}
```

It is not necessary to define prefixes for the ontologies that are defined in the same file. Ontologies in the same
file can be referenced by their name. See [this section](./caveats.md#referencing-ontologies) for
more information about referencing ontologies.



### `$schema`

(required)

The `$schema` object refers to the JSON schema for DSP data model definitions and is mandatory.

`"$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json"`



### `project`

(required)

`"project": {"key": "<value>", ...}`

The `project` object contains the basic metadata about the project. The following fields are required:

- shortcode
- shortname
- longname
- descriptions
- keywords
- default_permissions
- enabled_licenses
- ontologies

The following fields are optional (if one or more of these fields are not used, they should be omitted):

- default_permissions_overrule (only if default_permissions = public)
- groups
- users
- lists



## The `project` Object in Detail

In the following section, all fields of the `project` object are explained in detail.



### `shortcode`

(required)

`"shortcode": "<4-hex-characters>"`

The shortcode has to be unique and is represented by a 4 digit hexadecimal string. The shortcode has to be provided by 
the DaSCH.



### `shortname`

(required)

`"shortname": "<string>"`

The shortname has to be unique. 
It should be in the form of a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). 
This means a string without blanks or special characters,
but with `-` and `_` are allowed (although not as first character).



### `longname`

(required)

`"longname": "<string>"`

The longname is a string that provides the full name of the project.



### `descriptions`

(required)

`"descriptions": {"<lang>": "<string>", ...}`

The description is represented as a collection of strings with language tags
(currently, `en`, `de`, `fr`, `it`, and `rm` are supported).



### `keywords`

(required)

`"keywords": ["<string>", "<string>", ...]`

Keywords are represented as an array of strings and are used to describe and/or tag the project.


### `enabled_licenses`

(required)

`"enabled_licenses": ["<license-iri>", "<license-iri>", ...]`

In order for files/IIIF-URIs to reference a license, the license must be enabled here.
Only licenses that exist in DSP can be enabled. They must be referenced by their IRI.
For example: `http://rdfh.ch/licenses/cc-by-4.0` is a valid license IRI.
All the licenses listed here will be enabled. Licenses can be disabled by omitting them.

See [the API documentation for details](https://docs.dasch.swiss/latest/DSP-API/01-introduction/legal-info/#license).


### `default_permissions`

(required)

`"default_permissions": "public|private"`

Defines the permissions that will be applied to new resources/values.

- `public`: All users can view resources/values.
- `private`: Only ProjectMembers/ProjectAdmins can view resources/values.

If you work with the Excel templates,
this setting is available in the [`json_header.xlsx` file](../excel2json.md#the-json_headerxlsx).

!!! info

    When creating a new resource/value via xmlupload,
    it is possible to overrule this default with `<resource permissions="something-else">`.
    See [here](../xml-data-file.md#defining-permissions-with-the-permissions-element) for details.


### `default_permissions_overrule`

(optional)

If the `default_permissions` are `public`,
you can define exceptions, by marking certain classes or properties as `private` or `limited_view`:

- `private`: classes and/or properties that will only be visible for ProjectAdmins and ProjectMembers
    - For a class, it means that the resources of that class will be invisible for people outside of your project.
    - For a property, it means that the content of that property will be invisible for people outside of your project,
      while the rest of the resource is still public.
- `limited_view`: image classes which will be blurred/watermarked for users outside of your project.
    - Only the image will be blurred, the rest of the resource will be public.
    - `all` means all image classes, also the ones created in the future.

```json
"default_permissions": "public|private",
"default_permissions_overrule": {  // only "public" can be overruled
    "private": [
        "my-onto:PrivateResource",
        "my-onto:privateProp"
    ],
    "limited_view": "all" | [  // "all" means all subclasses of StillImageRepresentation
      "my-onto:Image1",
      "my-onto:Image2",  // only subclasses of StillImageRepresentation can appear here
    ],
}
```

If you work with the Excel templates,
these settings are available in the [`resources.xlsx` file](../excel2json.md#the-resources-section)
and in the [`properties.xlsx` file](../excel2json.md#the-properties-section).



### `groups`

(optional)

`"groups": [<group-definition>, <group-definition>,...]`

The `groups` object contains **project specific** group definitions. As opposed to the 
[**built-in** groups](../xml-data-file.md#groups), the membership of the users to the project specific groups 
can be freely chosen by the `ProjectAdmin`. A project may define several groups such as "student-assistant", 
"editors", etc. in order to provide their members specific permissions.
The groups that were created here are then available in the XML file in the 
[&lt;permissions&gt; element](../xml-data-file.md#defining-permissions-with-the-permissions-element).

A project specific group definition has the following elements:

- _name_ (mandatory): name of the group
- _descriptions_ (mandatory): description of the group with language tags in the form 
  `"descriptions": {"<lang>": "<string>", ...}` 
  (currently, `en`, `de`, `fr`, `it`, and `rm` are supported).
- _selfjoin_ (optional): true if users are allowed to join the group themselves, 
  false (default) if a `ProjectAdmin` has to add them
- _status_ (optional): true (default) if the group is active, false if the group is inactive

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



### `users`

(optional)

`"users": [<user-definition>, <user-definition>,...]`

This object contains user definitions. A user has the following elements:

- `username`: username used for login
- `email`: email that identifies the user, has to be unique within DSP
- `givenName`: first name of the user
- `familyName`: surname of the user
- `password`: password of the user
- `lang`: the default language of the user: `en`, `de`, `fr`, `it`, `rm` (optional, default: `en`)
- `groups` (optional): List of groups the user belongs to. The group names must be provided in one of the following forms:
    - `other_project_shortname:groupname`
    - `:groupname` (for groups defined in the current JSON project file)
- `projects` (optional): List of projects the user belongs to. The project name has to be followed by a `:` and either 
  `member` or `admin`. This indicates if the new user has admin rights in the given project or is an ordinary
  user. `myproject:admin` would add the user as admin to the project `myproject`. The project defined in the same
  JSON project file can be omitted, so only `:admin` or `:member` is enough. Note that in order to give a user `:admin` 
  rights, he also needs to be a `:member` of the project.
    - If _projects_ is omitted, the user won't be part in any project.
- `status` (optional): true (default) if the user is active, false if the user is deleted/inactive

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
      ], 
      "status": true
    }
  ]
}
```

The `users` element is optional. If not used, it should be omitted.



### `lists`

(optional)

`"lists": [<list-definition>,<list-definition>,...]`

Lists can be used to provide controlled vocabularies. They can be flat or hierarchical. One advantage of the use of
hierarchical lists is that it allows a user to sub-categorize objects. This helps in the formulation of specific search
requests. If there is a list node "Vocal music" and sub-nodes "Song" and "Opera", a search for "Vocal Music" would
return objects classified as "Song" and "Opera". But a search for "Song" would only return objects classified as "Song".
 
The "lists" section is an array of list definitions. A list definition has one root node whose name is used to identify 
the list. The children of the root node are the list nodes. If the list is hierarchical, the list nodes can have
children, and these children can again have children, etc.

When a project defines a list, resources can use the list values by defining a list property, e.g. a property with 
[object "ListValue"](./ontologies.md#listvalue).

A node of a list may have the following elements:

- `name` (mandatory): Name of the node. Has to be unique within the entire "lists" section.
- `labels` (mandatory): Label with language tags in the form `{"<lang>": "<label>", "<lang>": "<label>", ... }`. 
  At least one language needs to be specified. Currently, `en`, `de`, `fr`, `it`, and `rm` are supported.
- `comments` (mandatory for root node, optional for all other nodes): Comment with language tags in the form 
  `{"<lang>": "<comment>", "<lang>": "<comment>", ... }`. Currently, `en`, `de`, `fr`, `it`, and `rm` are supported.
- `nodes` (optional): Array of sub-nodes.

Example of a "lists" section that contains the two lists "color" and "category":

```json
{
    "lists": [
        {
            "name": "color",
            "labels": {
                "de": "Farbe",
                "en": "Color"
            },
            "comments": {
                "de": "Eine Liste mit einigen Farben",
                "en": "A list with some colors"
            },
            "nodes": [
                {
                    "name": "red",
                    "labels": {
                        "de": "rot",
                        "en": "red"
                    }
                },
                {
                    "name": "yellow",
                    "labels": {
                        "de": "gelb",
                        "en": "yellow"
                    }
                },
                {
                    "name": "blue",
                    "labels": {
                        "de": "blau",
                        "en": "blue"
                    }
                },
                {
                    "name": "green",
                    "labels": {
                        "de": "grün",
                        "en": "green"
                    }
                }
            ]
        },
        {
            "name": "category",
            "labels": {
                "de": "Kategorie",
                "en": "category"
            },
            "comments": {
                "de": "Eine Liste mit Kategorien",
                "en": "A list with categories"
            },
            "nodes": [
                {
                    "name": "artwork",
                    "labels": {
                        "de": "Kunstwerk",
                        "en": "artwork"
                    }
                },
                {
                    "name": "vehicles",
                    "labels": {
                        "de": "Fahrzeuge",
                        "en": "vehicles"
                    }
                },
                {
                    "name": "nature",
                    "labels": {
                        "de": "Natur",
                        "en": "nature"
                    },
                    "nodes": [
                        {
                            "name": "humanes",
                            "labels": {
                                "de": "Menschen",
                                "en": "Humanes"
                            }
                        },
                        {
                            "name": "animals",
                            "labels": {
                                "de": "Tiere",
                                "en": "Animals"
                            },
                            "nodes": [
                                {
                                    "name": "mammals",
                                    "labels": {
                                        "de": "Säugetiere",
                                        "en": "Mammals"
                                    }
                                },
                                {
                                    "name": "insects",
                                    "labels": {
                                        "de": "Insekten",
                                        "en": "Insects"
                                    }
                                },
                                {
                                    "name": "birds",
                                    "labels": {
                                        "de": "Vögel",
                                        "en": "Birds"
                                    }
                                },
                                {
                                    "name": "amphibians",
                                    "labels": {
                                        "de": "Ambhibien",
                                        "en": "Amphibians"
                                    }
                                },
                                {
                                    "name": "reptiles",
                                    "labels": {
                                        "de": "Reptilien",
                                        "en": "Reptiles"
                                    }
                                }
                            ]
                        },
                        {
                            "name": "plants",
                            "labels": {
                                "de": "Pflanzen",
                                "en": "Plants"
                            }
                        },
                        {
                            "name": "weather",
                            "labels": {
                                "de": "Wetter",
                                "en": "Weather"
                            }
                        },
                        {
                            "name": "physics",
                            "labels": {
                                "de": "Physik",
                                "en": "Physics"
                            }
                        }
                    ]
                }
            ]
        }
    ]
}
```




### `ontologies`

(required)

`"ontologies": [<ontology-definition>, <ontology-definition>, ...]`

Inside the `ontologies` array, a project may have multiple ontology definitions. 
An ontology definition consists of the following fields:

- `name`
- `label`
- `properties`
- `resources`

The `ontologies` array is [documented here](./ontologies.md)



## Fully Fleshed-Out Example of a JSON Project File

DaSCH provides you with two example repositories that contain everything which is necessary to create a project and 
upload data. Both of them also contain a JSON project definition file. You can find them here:

- [https://github.com/dasch-swiss/00A1-import-scripts](https://github.com/dasch-swiss/00A1-import-scripts)
- [https://github.com/dasch-swiss/082E-rosetta-scripts](https://github.com/dasch-swiss/082E-rosetta-scripts)

In addition, there is another complete example of a JSON project file here:

```json
{
  "prefixes": {
    "foaf": "http://xmlns.com/foaf/0.1/",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json",
  "project": {
    "shortcode": "0170",
    "shortname": "teimp",
    "longname": "Test Import",
    "descriptions": {
      "en": "This is a project for testing the creation of ontologies and data.",
      "de": "Dies ist ein Projekt, um die Erstellung von Ontologien und Datenimport zu testen."
    },
    "keywords": [
      "test",
      "import"
    ],
    "enabled_licenses": [
        "http://rdfh.ch/licenses/cc-by-4.0",
        "http://rdfh.ch/licenses/cc-by-sa-4.0",
        "http://rdfh.ch/licenses/ai-generated",
        "http://rdfh.ch/licenses/unknown"
    ],
    "lists": [
      {
        "name": "orgtype",
        "labels": {
          "en": "Organization Type",
          "de": "Organisationsart"
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
            "object": ":organization",
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
              "en": "Organization type",
              "de": "Organisationstyp"
            },
            "comments": {
              "en": "Type of organization",
              "de": "Art der Organisation"
            },
            "gui_element": "List",
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
