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
state "CLI: xmlupload" as transform
state "ParsedResource" as parsedres1
state "ParsedResource" as parsedres2
state "ParsedResource" as parsedres3
state "IntermediaryResource" as intermediaryres
state "CLI: validate-data" as valdata

[*]-->eroot1
state rootwork {
    eroot1-->eroot2: xsd validation success
    eroot1-->[*]: xsd validation error raised
}
eroot2-->pywork
state pywork {
    eroot3-->parsedres1: transform representation
}
pywork-->transform
state transform {
    ResourceInputConversionFailure-->[*]: transformation error raised
    parsedres2-->intermediaryres: transformation success
    parsedres2-->ResourceInputConversionFailure: transformation failure
}
pywork-->valdata
state valdata {
    parsedres3-->ResourceDeserialised: transformations
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
            valtree-->valpars: transform special tags<br/><br/>resolve prefixes into absolute IRIs<br/><br/>resolve value type to Python Class
        }
        transval-->respars: add to resource

        state transfile {
            filetree-->filepars: resolve file type
        }
        transfile-->respars: add to resource
    }
```

<!-- markdownlint-enable MD013 -->


### From `ParsedResource` to `IntermediaryResource` in `xmlupload`

```mermaid
---
title: Transformations from ParsedResource for xmlupload
---
stateDiagram-v2

state "Transform Resource" as transformres
state "Transform Value" as transformationval
state "Transform FileValues" as transformfile
state "ParsedValue" as parsedval
state "ParsedResource" as parsedres
state "IntermediaryValue" as valdes
state "Collected Transformations" as coll

parsedres-->transformfile
parsedres-->transformationval
parsedres-->transformres
state transformres {
    ParsedResource-->Permissions: resolve permissions
}
state transformationval {
    parsedval-->valdes: resolve permissions<br/><br/>resolve listnodes to IRIs
}
state transformfile {
    ParsedFileValue-->IntermediaryFileValue: resolve permissions<br/><br/>resolve metadata
}
transformres-->coll: return result
transformationval-->coll: return result
transformfile-->coll: return result
coll-->ResourceInputConversionFailure: resolving errors
ResourceInputConversionFailure-->[*]
coll-->IntermediaryResource: successful transformations
```
