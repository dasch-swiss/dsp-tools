# Architectural Design

## Parsing XML Files and Transformations for `xmlupload` and `validate-data`

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


### From `ParsedResource` to `ResourceDeserialised` in `xmlupload`

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
        ParasedFileValue-->FileValueDeserialised: map permissions</br></br>map metadata
    }
    transformfile-->ResourceDeserialised: add File
    transfomrationval-->ResourceDeserialised: add Values
    transformres-->ResourceDeserialised: add permissions
}
```


