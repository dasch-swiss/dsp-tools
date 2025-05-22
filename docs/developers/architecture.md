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
state "Collected Results" as coll

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
processedres-->coll: return result
processedationval-->coll: return result
processedfile-->coll: return result
coll-->ResourceInputProcessingFailure: resolving errors
ResourceInputProcessingFailure-->[*]
coll-->ProcessedResource: successful processed resources
```
