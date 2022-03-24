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
    }
    "outputFiles": true | false                                         # default=true
    ...
}
```


The structure of the cardinalities:
```
cardinalities: {
    "hasValue_TextValue": 0-10 | {                                      # 0-10 is the "numOfProps"
        "numOfProps": 1-10,                                             # default=1
        "numOfValuesPerProp": 1-100,                                    # default=1
        "cardinality": "0-1" | "0-n" | "1" | "1-n",                     # default, or if in conflict with "numOfValuesPerProp": "0-n"
        "gui_element": "SimpleText" | "Richtext" | "Textarea",          # default="SimpleText"
        "encoding": "xml" | "utf8",                                     # default="utf8"
        "salsah-links": true | false,                                   # default determined by definition above
    },
    "hasValue_ColorValue": 0-10 | {                                     # 0-10 is the "numOfProps"
        "numOfProps": 1-10,                                             # default=1
        "numOfValuesPerProp": 1-100,                                    # default=1
        "cardinality": "0-1" | "0-n" | "1" | "1-n"                      # default, or if in conflict with "numOfValuesPerProp": "0-n"
    },
    "hasValue_DateValue": 0-10 | {                                      # 0-10 is the "numOfProps"
        "numOfProps": 1-10,                                             # default=1
        "numOfValuesPerProp": 1-100,                                    # default=1
        "cardinality": "0-1" | "0-n" | "1" | "1-n"                      # default, or if in conflict with "numOfValuesPerProp": "0-n"
    },
    "hasValue_TimeValue": 0-10 | {                                      # 0-10 is the "numOfProps"
    },
    "hasValue_DecimalValue": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasValue_GeomValue": 0-10 | {                                      # 0-10 is the "numOfProps"
    },
    "hasValue_GeonameValue": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasValue_IntValue": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasValue_BooleanValue": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasValue_UriValue": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasValue_IntervalValue": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasValue_ListValue": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasColor": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasComment": 0-10 | {                                     # 0-10 is the "numOfProps"
    },
    "hasLinkTo"  --> any Resource
    "hasRepresentation" --> Representation (XML: different <resptr>s with point to Image, Audio, PDF, ...)
```
