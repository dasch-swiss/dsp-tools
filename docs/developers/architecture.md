# Architectural Design

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

[*]-->eroot1
state rootwork {
    eroot1-->eroot2: xsd validation success
    eroot1-->[*]: xsd validation error raised
}
eroot2-->pywork
state pywork {
    eroot3-->parsedres1: processed representation
}
pywork-->processed
state processed {
    valdata-->[*]: validation failure
    valdata-->parsedres2: validation success
    parsedres2-->Processedres: resolve data
}
pywork-->valdata
state valdata {
    parsedres3-->RdfLikeResource: processing
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

[*]-->r1: Parse file

r4-->transpy
    state eroot {
        state "etree root" as r1
        state "etree root" as r2
        state "etree root" as r3
        state "etree root" as r4
        r1-->r2: Remove Comments
        r2-->[*]: xsd validation failure
        r2-->r3: xsd validation success
        r3-->r4: make localnames
    }
    state transpy {
        resetree1-->transval: extract values
        resetree1-->transfile: extract file or iiif
        resetree1-->respars: transform special tags<br/><br/>resolve prefixes into absolute IRIs

        state transval {
            valtree-->valpars: transform special tags<br/><br/>resolve prefixes into absolute IRIs<br/><br/>resolve value type to Python Class<br/><br/>strip whitespaces from content
        }
        transval-->respars: add to resource

        state transfile {
            filetree-->filepars: resolve file type<br/><br/>strip whitespaces from content
        }
        transfile-->respars: add to resource
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

parsedres-->processedfile
parsedres-->processedationval
parsedres-->processedres
state processedres {
    ParsedResource-->Permissions: resolve permissions
}
state processedationval {
    parsedval-->valdes: resolve permissions<br/><br/>resolve listnodes to IRIs
}
state processedfile {
    ParsedFileValue-->ProcessedFileValue: resolve permissions<br/><br/>resolve metadata
}
processedres-->ProcessedResource: return result
processedationval-->ProcessedResource: return result
processedfile-->ProcessedResource: return result
ProcessedResource--> cont: success
ProcessedResource-->[*]: unexpected transformation failure
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
