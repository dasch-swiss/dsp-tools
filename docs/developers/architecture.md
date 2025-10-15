# Architectural Design

## Code Flow For the `create` Command

The JSON schema validation takes over a lot of validation,
therefore there are only minimal errors we may encounter a successful validation,
primarily relating to inexistent references to other objects that can be caused by typos.

If the user provided incorrect input we do not try and extrapolate a fix but communicate the problem precisely
so that the user may easily fix it themselves.

We aim for a fast-fail approach before we begin with the upload.
If we have upload failures during the upload we will not stopp the entire process but continue to create as much of
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

### Upload Order to API

Within one project we have several dependencies that dictate the upload order.

While the Groups, Users, Lists and Cardinalities to do not have to be sorted "within",
the order of Classes and Properties are relevant as they may have dependencies on others.

The following table contains the possible dependencies, the first column is the object type we are looking at,
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

Unless the upload stopped which is indicated by a circle,
a failure in a previous step does not prevent the upload of the next object categories.
The following section explains how we deal with dependencies that were not created.

### Dependency Checks During an Upload

Properties, Classes and Cardinalities may depend on the existence of other Classes, Properties and Lists.
If these dependencies were not successfully created, we do not need to an upload and generate additional errors.

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

## Parsing XML Files and Transformations for `xmlupload` and `validate-data`

### Overview

```mermaid
---
title: Overview of Code Flow for xmlupload and validate-data
---
stateDiagram-v2
    state "etree Root" as eroot1
    state "etree Root" as eroot2
    state "etree Root" as eroot3
    state "Root Modifications" as rootwork
    state "etree Into Python Representation" as pywork
    state "CLI: xmlupload" as processed
    state "ParsedResource" as parsedres1
    state "ParsedResource" as parsedres2
    state "ParsedResource" as parsedres3
    state "ProcessedResource" as Processedres
    state "CLI: validate-data" as valdata
    [*] --> eroot1
    state rootwork {
        eroot1 --> eroot2: xsd validation success
        eroot1 --> [*]: xsd validation error raised
    }
    eroot2 --> pywork
    state pywork {
        eroot3 --> parsedres1: processed representation
    }
    pywork --> processed
    state processed {
        valdata --> [*]: validation failure
        valdata --> parsedres2: validation success
        parsedres2 --> Processedres: resolve data
    }
    pywork --> valdata
    state valdata {
        parsedres3 --> RdfLikeResource: processing
    }
```

### Parsing XML Files

<!-- markdownlint-disable MD013 -->

```mermaid
---
title: Parsing of XML File and Transformations Into ParsedResource
---
stateDiagram-v2
    state "Transform etree Root" as eroot
    state "Transform etree Root Into Python Representation" as transpy
    state "Resource etree" as resetree1
    state "ParsedResource" as respars
    state "Value etree" as valtree
    state "IIIF/bitstream etree" as filetree
    state "ParsedValue" as valpars
    state "ParsedFileValue" as filepars
    state "Transform Value" as transval
    state "Transform FileValue" as transfile
    [*] --> r1: Parse file
    r4 --> transpy
    state eroot {
        state "etree root" as r1
        state "etree root" as r2
        state "etree root" as r3
        state "etree root" as r4
        r1 --> r2: Remove Comments
        r2 --> [*]: xsd validation failure
        r2 --> r3: xsd validation success
        r3 --> r4: make localnames
    }
    state transpy {
        resetree1 --> transval: extract values
        resetree1 --> transfile: extract file or iiif
        resetree1 --> respars: transform special tags<br/><br/>resolve prefixes into absolute IRIs

        state transval {
            valtree --> valpars: transform special tags<br/><br/>resolve prefixes into absolute IRIs<br/><br/>resolve value type to Python Class<br/><br/>strip whitespaces from content
        }
        transval --> respars: add to resource

        state transfile {
            filetree --> filepars: resolve file type<br/><br/>strip whitespaces from content
        }
        transfile --> respars: add to resource
    }
```

<!-- markdownlint-enable MD013 -->

### From `ParsedResource` to `ProcessedResource` in `xmlupload`

```mermaid
---
title: Transformations from ParsedResource for xmlupload
---
stateDiagram-v2
    state "Process Resource" as processedres
    state "Process Value" as processedationval
    state "Process FileValues" as processedfile
    state "ParsedValue" as parsedval
    state "ParsedResource" as parsedres
    state "ProcessedValue" as valdes
    state "Continue" as cont
    parsedres --> processedfile
    parsedres --> processedationval
    parsedres --> processedres
    state processedres {
        ParsedResource --> Permissions: resolve permissions
    }
    state processedationval {
        parsedval --> valdes: resolve permissions<br/><br/>resolve listnodes to IRIs
    }
    state processedfile {
        ParsedFileValue --> ProcessedFileValue: resolve permissions<br/><br/>resolve metadata
    }
    processedres --> ProcessedResource: return result
    processedationval --> ProcessedResource: return result
    processedfile --> ProcessedResource: return result
    ProcessedResource --> cont: success
    ProcessedResource --> [*]: unexpected transformation failure
```

## `validate-data` Validation Logic

### Validation Process

```mermaid
stateDiagram-v2
    state "XSD validation" as XSD
    state "<b>STOP<b>" as stopXSD
    state "Check for Unknown Classes<br>(Python Logic)" as unknownCls
    state "<b>STOP<b>" as stopUnknown
    state "Ontology Validation<br>(SHACL-CLI)" as ontoVal
    state "<b>STOP<b>" as ontoViolation
    state "flag <em>--ignore-duplicate-files-warning<em>" as ignoreF
    state "Check for Duplicate Filepaths<br>(Python Logic)" as duplicFile
    state "severity: WARNING" as warning
    state "severity: INFO" as info
    state "severity: ERROR" as err
    state "Data Validation<br>(SHACL-CLI)" as dataSH
    [*] --> XSD
    XSD --> stopXSD: validation failure
    XSD --> unknownCls: success
    unknownCls --> stopUnknown: unknown found
    unknownCls --> ontoVal: success
    ontoVal --> ontoViolation: violations found
    ontoVal --> ignoreF: success
    ignoreF --> dataSH: present
    ignoreF --> duplicFile: not present
    duplicFile --> dataSH: continue
    duplicFile --> warning: duplicates found
    dataSH --> info: problems
    dataSH --> err: problems
    dataSH --> warning: problems
```

### Determine Validation Success

The validation success, i.e. if an `xmlupload` would be possible and is allowed to continue, is dependent on the server.

Some validation problems are allowed on test environments (including localhost),
while the "prod-like" servers are stricter.
Prod like servers include prod, ls-prod, stage, and rdu-stage.

|         | TEST ENVIRONMENTS | PROD-LIKE ENVIRONMENTS |
|---------|-------------------|------------------------|
| INFO    | success           | success                |
| WARNING | success           | failure                |
| ERROR   | failure           | failure                |
