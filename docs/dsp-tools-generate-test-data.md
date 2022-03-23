[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Generation of test data for the DSP API

 - Some properties will be created always, based on the mandatory cardinalities of the chosen resource classes
 - Every resource (that allows it) will have the indicated number of every property. The hasLinkTo will point to every 
   resource class, evenly distributed. 
   Example: If there are 5 resource classes with 10 resources each, and hasLinkTo is set to 10, there are 5*10-1 
   possible targets. From every of the 5 classes, 2 resources will be chosen randomly. This means that 5 different  
   link-properties need to be defined, one for each target class (the target needs to be defined in the JSON onto)
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
            "classesPerInheritanceLevel": [1-10, 1-10, 1-10],           # default=[1]
            "resourcesPerClass": [1-10000, 1-10000, 1-10000],           # default=[10]
            "cardinalities": {...}                                      # definition see below
        },
        "StillImageRepresentation": {
            "inheritanceDepth": 1-3,                                    # default=1
            "classesPerInheritanceLevel": [1-10, 1-10, 1-10],           # default=[1]
            "resourcesPerClass": [1-10000, 1-10000, 1-10000],           # default=[10] 
            "AnnotationsPerResource": [1-100, 1-100, 1-100],            # default=[0]
            "RegionsPerResource": [1-100, 1-100, 1-100],                # default=[0]
            "fileSize": ["5KB"-"100MB", "5KB"-"100MB", "5KB"-"100MB"],  # default=["5KB"]
            "cardinalities": {...}                                      # definition see below
            "isCompoundedOf": {                                         # default=None
                "resclass": another resource class (one),
                "numOfResources": 1-1000
            }
        },
        "TextRepresentation" | "AudioRepresentation" | "DDDRepresentation" | "DocumentRepresentation" | 
        "MovingImageRepresentation" | "ArchiveRepresentation" : {
            "inheritanceDepth": 1-3,                                    # default=1
            "classesPerInheritanceLevel": [1-10, 1-10, 1-10],           # default=[1]
            "resourcesPerClass": [1-10000, 1-10000, 1-10000],           # default=[10] 
            "AnnotationsPerResource": [1-100, 1-100, 1-100],            # default=[0]
            "fileSize": ["5KB"-"100MB", "5KB"-"100MB", "5KB"-"100MB"],  # default=["5KB"]
            "cardinalities": {...}                                      # definition see below
            "isCompoundedOf": {                                         # default=None
                "resclass": another resource class (one),
                "numOfResources": 1-1000
            }
        },
        "LinkObj": {
            "numOfLinkObjects": 1-10000,
            "ResourcesPerLink": 2-10,
            "InvolvedResClasses" [list of resource classes]
        }
    },
    "properties": {     #these definitions are complimentary to the property definitions in each resclass
        define if they are shared among resclasses, or if each resclass has its own
        Sub-Properties
    },
    "lists": {
    },
    "salsah-links": {
        "linksPerTextField": 1-10,
        "pointToOtherResclasses": true | false
    }
    outputFiles={true,false}
    ...
}
```


The structure of the cardinalities:
```
cardinalities: {
    "hasValue_TextValue": 0-100 | {                                     # 0-100 is the "n"
                    "gui_element": "SimpleText" | "Richtext" | "Textarea"       # default="SimpleText"
                    "encoding": "xml" | "utf8",                         # default="utf8"
                    "salsah-links": true | false                        # default determined by definition below
                    "cardinality": "0-1" | "0-n" | "1" | "1-n"          # default="0-n"
                    "n": 0-100                                          # default=1
    },
    "hasValue_ColorValue": 0-11 | {},
    "hasValue_DateValue": 0-11 | {},
    "hasValue_TimeValue": 0-11 | {},
    "hasValue_DecimalValue": 0-11 | {},
    "hasValue_GeomValue": 0-11 | {},
    "hasValue_GeonameValue": 0-11 | {},
    "hasValue_IntValue": 0-11 | {},
    "hasValue_BooleanValue": 0-11 | {},
    "hasValue_UriValue": 0-11 | {},
    "hasValue_IntervalValue": 0-11 | {},
    "hasValue_ListValue": 0-11 | {},
    "hasColor": 0-11 | {},
    "hasComment": 0-11 | {},
    "hasLinkTo"  --> any Resource
    "hasRepresentation" --> Representation (XML: different <resptr>s with point to Image, Audio, PDF, ...)
```
