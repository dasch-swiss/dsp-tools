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
state "Root" as rootwork
state "etree to Python Representation" as pywork
state "xmlupload" as transform
state "ParsedResource" as parsedres1
state "ParsedResource" as parsedres2
state "ParsedResource" as parsedres3
state "IntermediaryResource" as intermediaryres
state "validate-data" as valdata

[*]-->rootwork
state rootwork {
    eroot1-->eroot2: xsd validation success
    eroot1-->[*]: xsd validation error
}
eroot2-->pywork
state pywork {
    eroot3-->parsedres1: transform representation
}
parsedres1-->transform
state transform {
    ResourceInputConversionFailure-->[*]: transformation error
    parsedres2-->intermediaryres: transformation success
    parsedres2-->ResourceInputConversionFailure: transformation failure
}
parsedres1-->valdata
state valdata {
    parsedres3-->ResourceDeserialised: transformations
}
```

### Parsing XML Files

```mermaid
---
title: Parsing of XML File and Transformations Into ParsedResource
---
stateDiagram-v2
state "Transform etree Root" as eroot
state "Transform etree Root into Python Representation" as transpy

r3-->transpy
    state eroot {
        state "etree root" as r1
        state "etree root" as r2
        state "etree root" as r3
        [*]-->r1: Parse file
        r1-->r2: Remove Comments
        r2-->[*]: xsd validation failure
        r2-->r3: xsd validation success
    }
    state transpy {
        state "Resource etree" as resetree
        state "ParsedResource" as respars
        state "Value etree" as valtree
        state "ParsedValue" as valpars
        resetree-->valtree: extract values
        valtree-->valpars: transform special tags</br></br>resolve prefixes into absolute IRIs</br></br>map value type into Python
        resetree-->respars: transform special tags</br></br>resolve prefixes into absolute IRIs
        valpars-->respars: add to resource
    }
```


### From `ParsedResource` to `IntermediaryResource` in `xmlupload`

```mermaid
---
title: Transformations from ParsedResource for xmlupload
---
stateDiagram-v2

state "ParsedResource" as start
state "Transform Entire Resource" as transformall
state "Transform Resource" as transformres
state "Transform Value" as transfomrationval
state "Transform FileValues" as transformfile
state "ParsedValue" as parsedval
state "ParsedResource" as parsedres
state "ValueDeserialised" as valdes
state "Collected Transformations" as coll

start-->transformall

state transformall {
    parsedres-->transformfile
    parsedres-->transfomrationval
    parsedres-->transformres
    state transformres {
        ParsedResource-->Permissions: resolve permissions
    }
    state transfomrationval {
        parsedval-->valdes: map permissions</br></br>map listnodes to IRIs</br></br>map file metadata
    }
    state transformfile {
        ParsedFileValue-->IntermediaryFileValue: map permissions</br></br>map metadata
    }
    transformfile-->coll: return result
    transfomrationval-->coll: return result
    transformres-->coll: return result
    coll-->ResourceInputConversionFailure: mapping errors
    ResourceInputConversionFailure-->[*]
    coll-->IntermediaryResource: successful transformations
}
```