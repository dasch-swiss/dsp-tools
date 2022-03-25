[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Generation of test data for the DSP API

 - Every resource (that allows it) will have the indicated number of every property. The hasLinkTo will point to every 
   resource class, evenly distributed. 
   Example: If there are 5 resource classes with 10 resources each, and hasLinkTo is set to 10, there are 5*10-1 
   possible targets. From every of the 5 classes, 2 resources will be chosen randomly. This means that 5 different  
   link-properties need to be defined, one for each target class (the target needs to be defined in the JSON onto)
 - Due to exponential growth, the chosen parameters in config.json can easily lead to a high amount of data. If a 
   certain threshold is reached, the user is asked if he wants to continue or not.
 - for the multimedia files, only one file will be created, and then it will be referenced & uploaded multiple times 
 - available file sizes are "5KB" | "10KB" | "50KB" | "100KB" | "500KB" | "1MB" | "5MB" | "10MB" | "50MB" | "100MB"


## Usage
`dsp-tools generate-test-data config.json`

Structure of config.json:
```
{
    "identicalOntologies": 3,                                           # default=1
    "resources": {
        "Resource": {
            "inheritanceDepth": 1-3,                                    # default=1
            "classesPerInheritanceLevel": 1-10 | [1-10, 1-10, ...],     # default=1
            "resourcesPerClass": 1-10000 | [1-10000, 1-10000, ...],     # default=[10]
            "cardinalities": {...}                                      # definition see below
        },
        "StillImageRepresentation": {
            "inheritanceDepth": 1-3,                                    # default=1
            "classesPerInheritanceLevel": 1-10 | [1-10, 1-10, ...],     # default=1
            "resourcesPerClass": 1-10000 | [1-10000, 1-10000, ...],     # default=[10]
            "AnnotationsPerResource": 1-100 | [1-100, 1-100, ...],      # default=[0]
            "RegionsPerResource": 1-100 | [1-100, 1-100, ...],          # default=[0]
            "fileSize": "5KB"-"100MB" | ["5KB"-"100MB", ...],           # default=["5KB"]
            "cardinalities": {...}                                      # definition see below
            "isCompoundedOf": {                                         # default=None
                "resclass": another resource class (one),
                "numOfResources": 1-1000
            }
        },
        "TextRepresentation" | "AudioRepresentation" | "DDDRepresentation" | "DocumentRepresentation" | 
        "MovingImageRepresentation" | "ArchiveRepresentation" : {
            "inheritanceDepth": 1-3,                                    # default=1
            "classesPerInheritanceLevel": 1-10 | [1-10, 1-10, ...],     # default=1
            "resourcesPerClass": 1-10000 | [1-10000, 1-10000, ...],     # default=[10]
            "AnnotationsPerResource": 1-100 | [1-100, 1-100, ...],      # default=[0]
            "fileSize": "5KB"-"100MB" | ["5KB"-"100MB", ...],           # default=["5KB"]
            "cardinalities": {...}                                      # definition see below
            "isCompoundedOf": {                                         # default=None
                "resclass": another resource class (one),
                "numOfResources": 1-1000
            }
        },
        "LinkObj": {                                                    # not implemented yet in dsp-tools
            "numOfLinkObjects": 1-10000,
            "ResourcesPerLink": 2-10,                                   # default=2
            "InvolvedResClasses": [list of resource classes]            # default=all
        }
    },
    "properties": {     #these definitions are complimentary to the "cardinalities" definitions in each resclass
        define if they are shared among resclasses, or if each resclass has its own
        Sub-Properties
    },
    "lists": {
        "numOfLists": 1-20,                                             # default=2
        "numOfDepthLevels": 1-5,                                        # default=2
        "nodesPerDepthLevel": 1-10 | [1-10, 1-10, ...]                  # default=2
    },
    "salsah-links": {
        "inProperties": [list of text properties with links]            # default=all text properties
        "linksPerTextField": 1-10,                                      # default=1
        "pointToOtherResclasses": true | false                          # default=true
    },
    "permissions": {                                                    # default=one single permission that will be applied everywhere (the one from the example below)
        "res-default": [V, V, CR, CR],                                  # "allows" for UnknownUser, KnownUser, Creator, ProjectAdmin (in this order)
        ...
    }
    "outputFiles": true | false                                         # default=true
}
```


The structure of the cardinalities:

There are some shared elements that can be used in every cardinality:
```
cardinalities: {
    "hasValue_TextValue" | "hasValue_ColorValue" | "hasValue_DateValue" | "hasValue_TimeValue" | 
    "hasValue_DecimalValue" | "hasValue_GeomValue" | "hasValue_GeonameValue" | "hasValue_IntValue" | 
    "hasValue_BooleanValue" | "hasValue_UriValue" | "hasValue_IntervalValue" | "hasValue_ListValue" | 
    "hasColor" | "hasComment" | "hasLinkTo" | 
    "hasRepresentation" : 0-10 | {                                      # 0-10 is the "numOfProps"
        "numOfProps": 1-10,                                             # default=1
        "numOfValuesPerProp": 1-100,                                    # default=1
        "cardinality": "0-1" | "0-n" | "1" | "1-n"                      # default, or if in conflict with "numOfValuesPerProp": "0-n"
        "permissions": [one or more permissions from above]             # default=the first permission from above
        "comment": "Your comment text"                                  # default=None
}
```

In addition to the elements common to every cardinality, there are special definitions:
```
cardinalities: {
    "hasValue_TextValue": {                                      
        "gui_element": "SimpleText" | "Richtext" | "Textarea",          # default="SimpleText"
        "encoding": "xml" | "utf8",                                     # default="utf8"
        "salsah-links": true | false,                                   # default determined by definition above
    },
    "hasValue_DateValue": {
        "dateRanges": true | false                                      # default=false
        "calendars": ["JULIAN", "GREGORIAN"]                            # default=["GREGORIAN"]
        "epochs": ["BCE", "CE"]                                         # default=["CE"]
        "precisionUpTo": ["year", "month", "day"]                       # default=["day"]
    },
    "hasValue_TimeValue": {
    },
    "hasValue_DecimalValue": {
    },
    "hasValue_GeomValue": {
    },
    "hasValue_GeonameValue": {
    },
    "hasValue_IntValue": {
    },
    "hasValue_BooleanValue": {
    },
    "hasValue_UriValue": {
    },
    "hasValue_IntervalValue": {
    },
    "hasValue_ListValue": {
    },
    "hasColor": {
    },
    "hasComment": {
    },
    "hasLinkTo"  --> any Resource
    "hasRepresentation" --> Representation (XML: different <resptr>s with point to Image, Audio, PDF, ...)
```
