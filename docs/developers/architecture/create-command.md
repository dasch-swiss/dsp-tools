# `create` Command

The JSON schema validation takes over a lot of validation,
therefore there are only minimal errors we may encounter after a successful validation,
primarily relating to inexistent references to other objects that can be caused by typos.

If the user provided incorrect input, we do not try and extrapolate a fix, but communicate the problem precisely
so that the user may easily fix it themselves.

We aim for a fast-fail approach before we begin with the upload.
If we have upload failures during the upload, we will not stop the entire process, but continue to create as much of
the project and ontologies as possible.
The upload failures should be communicated at the end of an upload in a precise and user-friendly message.

```mermaid
---
title: Overview of Code Flow for create
---
stateDiagram-v2
    state "JSON Schema Validation" as val
    state "JSON File" as jsonFile1
    state "JSON File" as jsonFile2
    state "JSON into Python representation" as jsonPy
    state "ParsedProject" as parsedProj1
    state "ParsedProject" as parsedProj2
    state "Sorting Dependencies" as sortingDeps
    state "ProcessedProject" as processedProj1
    state "Upload" as upload
    state "ProcessedProject" as processedProj2
    state "Upload all Information" as uploadAll
    state "Collected Creation Errors" as collErr
    state "Print Upload Failures Message" as printErr
    state "Print Success Message" as printSucc
    [*] --> val
    state val {
        jsonFile1 --> [*]: error
        jsonFile1 --> jsonFile2: success
    }

    state jsonPy {
        jsonFile2 --> [*]: IRI resolving error
        jsonFile2 --> parsedProj1: IRI resolving
        parsedProj1 --> parsedProj2
    }

    state sortingDeps {
        parsedProj2 --> [*]: dependencies could not be resolved
        parsedProj2 --> processedProj1: finding dependencies<br/>generating upload order
        processedProj1 --> processedProj2
    }

    state upload {
        processedProj2 --> uploadAll: upload all information
        uploadAll --> collErr: collect errors on the way
        collErr --> printErr: print all error messages
        uploadAll --> printSucc: print success message
    }
```

## Upload Order to API

Within one project we have several dependencies that dictate the upload order.

While the Groups, Users, Lists and Cardinalities do not have to be sorted "within",
the order of Classes and Properties are relevant as they may have dependencies on others.

The following table contains the possible dependencies. The first column is the object type we are looking at,
the other columns indicate how they may depend on other object types.

| Object Type     | List            | Class                             | Propery                 | Group     | User |
|-----------------|-----------------|-----------------------------------|-------------------------|-----------|------|
| **List**        |                 |                                   |                         |           |      |
| **Class**       |                 | super-classes                     |                         |           |      |
| **Property**    | list properties | object / subject class constraint | super-properties        |           |      |
| **Cardinality** |                 | cardinality on class              | cardinality on property |           |      |
| **Group**       |                 |                                   |                         |           |      |
| **User**        |                 |                                   |                         | if custom |      |

Note, that one project may have more than one ontology,
in that case it is permissible to reference classes and properties from the other ontologies.
Therefore, we need to handle the classes of all ontologies first, before we may move on to the properties.

```mermaid
---
title: Upload Order
---
stateDiagram-v2
    state "ProcessedProject" as processedProj
    state "Create Project" as crProj
    state "Create Groups" as crGr
    state "Create Users" as crUser
    state "Create Lists" as crLists
    state "Create Ontology & Classes" as crCls
    state "Create Properties" as crProp
    state "Create Cardinalities" as crCards
    state "Upload Finished" as upFini
    state "Collected Creation Errors" as collErr
    state "Print Upload Failures Message" as printErr
    state "Print Success Message" as printSucc
    processedProj --> crProj
    crProj --> [*]: project creation error
    crProj --> crGr
    crGr --> crUser: continue
    crUser --> collErr: add to
    crUser --> crLists: continue
    crLists --> collErr: add to
    crLists --> crCls: continue
    crCls --> collErr: add to
    crCls --> crProp: continue
    crProp --> collErr: add to
    crProp --> crCards: continue
    crCards --> collErr: add to
    crCards --> upFini: continue
    upFini --> printErr: with errors
    collErr --> printErr: continue
    upFini --> printSucc: no errors
```

Unless the upload stopped (which is indicated by a circle),
a failure in a previous step does not prevent the upload of the next object categories.
The following section explains how we deal with dependencies that were not created.

## Dependency Checks During an Upload

Properties, Classes and Cardinalities may depend on the existence of other Classes, Properties and Lists.
If the dependencies of an object were not successfully created, we should not upload the object and generate additional
errors.

See the table above for the dependencies one object type may have, and consequently which checks are required.

```mermaid
---
title: Upload Mechanism of a Single Object
---
stateDiagram-v2
    state "Processing one Object" as preUp
    state "Object" as preObj
    state "dependency failed" as checkFail1
    state "FailureCollection" as checkFail2
    state "dependency exists" as checkSucc
    state "Upload" as upload
    state "Object" as upObj
    state "Failure" as upFail
    state "Success" as upSucc
    state "FailureCollection" as upFailColl
    state "SuccessCollection" as upSuccColl

    state preUp {
        preObj --> checkFail1: dependencies in failures
        checkFail1 --> checkFail2: add to failures
        preObj --> checkSucc: dependencies successfully uploaded
        checkSucc --> upload: continue upload
    }

    state upload {
        upObj --> upFail: upload failed
        upFail --> upFailColl: add
        upObj --> upSucc: upload success
        upSucc --> upSuccColl: add
    }
```
