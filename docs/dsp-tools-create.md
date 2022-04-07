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

(optional)

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

It is not necessary to define prefixes for the ontologies that are defined in this file. Ontologies in the same
file can refer to each other via their name. See also [here](./dsp-tools-create-ontologies.md#referencing-ontologies).

### "$schema" object

(required)

The `$schema` object refers to the JSON schema for DSP data model definitions and is mandatory.

`"$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json"`

### "project" object

(required)

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

(required)

`"shortcode": "<4-hex-characters>"`

The shortcode has to be unique and is represented by a 4 digit hexadecimal string. The shortcode has to be provided by the DaSCH.

### Shortname

(required)

`"shortname": "<string>"`

The shortname has to be unique. It should be in the form of a [xsd:NCNAME](https://www.w3.org/TR/xmlschema11-2/#NCName). This means a
string without blanks or special characters but `-` and `_` are allowed (although not as first character).

### Longname

(required)

`"longname": "<string>"`

The longname is a string that provides the full name of the project.

### Descriptions

(required)

`"descriptions": {"<lang>": "<string>", ...}`

The description is represented as a collection of strings with language tags (currently "en", "de", "fr" and "it" are
supported). It is the description of the project.

### Keywords

(required)

`"keywords": ["<string>", "<string>", ...]`

Keywords are represented as an array of strings and are used to describe and/or tag the project.

### Lists

(optional)

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

A list can be directly imported from one or several Excel files. The folder with the Excel file(s) can then directly 
be referenced inside the list definition by defining it as new list node:

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

The `nodes` section has to contain the field:

- _folder_: Path to the folder containing the Excel files

Further information about the expected format of the Excel lists and details to this functionality can be found
[here](./dsp-tools-excel.md#create-a-list-from-one-or-several-excel-files).

The `lists` element is optional. If not used, it should be omitted.

### Groups

(optional)

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

### Users

(optional)

`"users": [<user-definition>, <user-definition>,...]`

This object contains user definitions. A user has the following elements:

- _username_: username used for login
- _email_: email that identifies the user, has to be unique within DSP
- _givenName_: firstname of the user
- _familyName_: surname of the user
- _password_: password of the user
- _lang_: the default language of the user: "en", "de", "fr", "it" (optional, default: "en")
- _groups_: List of groups the user belongs to. The name of the group has to be provided with the project's shortname,
  p.ex. "shortname:editors". The project defined in the same ontology file has no name, so only ":editors" is required
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

(required)

`"ontologies": [<ontology-definition>, <ontology-definition>, ...]`

Inside the `ontologies` section all resources and properties are described. A project may have multiple ontologies. It
requires the following data fields:

- `name`
- `label`
- `properties`
- `resources`

A detailed description of `ontologies` can be found [here](dsp-tools-create-ontologies.md)

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
