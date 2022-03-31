[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Generation of test data for the DSP API
 - Due to exponential growth, the chosen parameters in config.json can easily lead to a high amount of data. If a 
   certain threshold is reached, the user is asked if he wants to continue or not.
 - for the multimedia files, only one file will be created, and then it will be referenced & uploaded multiple times 
 - available file sizes are "5KB" | "10KB" | "50KB" | "100KB" | "500KB" | "1MB" | "5MB" | "10MB" | "50MB" | "100MB"


## Usage
`dsp-tools generate-test-data config.json`

## Structure of config.json
```
{
    "identicalOntologies": 1-3,                                         # default=1
    "resources": {
        "Resource": {
            "inheritanceDepth": 1-3,                                    # default=1
            "classesPerInheritanceLevel": 1-10 | [1-10, 1-10, ...],     # default=1
            "resourcesPerClass": 1-10000 | [1-10000, 1-10000, ...],     # default=10
            "annotationsPerResource": 1-100 | [1-100, 1-100, ...],      # default=0
            "cardinalities": {...}                                      # definition see below
            "isCompoundedOf": {                                         # default=None
                "resclass": another resource class (one),
                "numOfResources": 1-1000
            }
        },
        "StillImageRepresentation": {
            # same as in "Resource", plus:
            "regionsPerResource": 1-100 | [1-100, 1-100, ...],          # default=0
            "fileSize": "100MB" | ["100MB", ...],                       # default="5KB"
        },
        "TextRepresentation" | "AudioRepresentation" | "DDDRepresentation" | "DocumentRepresentation" | 
        "MovingImageRepresentation" | "ArchiveRepresentation" : {
            # same as in "Resource", plus:
            "fileSize": "100MB" | ["100MB", ...],                       # default="5KB"
        },
        "LinkObj": {                                                    # not implemented yet in dsp-tools
            "numOfLinkObjects": 1-10000,
            "resourcesPerLink": 2-10,                                   # default=2
            "involvedResClasses": [list of resource classes]            # default=all
        }
    },
    "properties": {                                                     # optional
        "hasValue_TextValue": {                                         # only propclasses used in "cardinalities" can appear here
            "inheritanceDepth": 1-3,                                    # default=1
            "propertiesPerLevel": 1-3                                   # default=1
            "gui_elements": (see below)
        },
        ...
    },
    "lists": {                                                          # if omitted, no lists are created
        "numOfLists": 1-20,                                             # default=2
        "numOfDepthLevels": 1-5,                                        # default=2
        "nodesPerDepthLevel": 1-10 | [1-10, 1-10, ...]                  # default=2
    },
    "salsah-links": {                                                   # if omitted, no salsah-links are created
        "inProperties": [one or more text properties with links],       # default=all text properties
        "linksPerTextField": 1-10,                                      # default=1
        "pointToOtherResclasses": true | false                          # default=true
    },
    "permissions": {                                                    # if omitted, the ex. below is applied everywhere
        "res-default": [V, V, CR, CR],                                  # "allows" for UnknownUser, KnownUser, Creator, 
        ...                                                             # ProjectAdmin (in this order)
    },
    "outputFiles": true | false                                         # default=true
}
```

### Structure of the "properties" section

Each property class in the "properties" section can define its "gui_elements" in a list. The list 
can contain more than one entry, if more than one prop of that class is created. The available options
depend on the object of the property class:
| super             | object        | gui_elements                               | default            |
| ----------------- | ------------- | ------------------------------------------ | ------------------ |
| hasValue          | TextValue     | ["SimpleText", "Richtext", "Textarea"]     | ["SimpleText"]     |
| hasValue          | DecimalValue  | ["Slider", "SimpleText"]                   | ["SimpleText"]     |
| hasValue          | IntValue      | ["Spinbox", "SimpleText"]                  | ["SimpleText"]     |
| hasValue          | IntervalValue | ["Interval", "SimpleText"]                 | ["SimpleText"]     |

In addition, some properties need further specifications:
"hasValue_ListValue": {
        "hlist": 1-20                                                   # number of list from lists[numOfLists]; default=1
},
"hasLinkTo": {
    "objects": "resclass" | ["objectClassOfProp1", ...]              # default="Resource" (resources from all classes
                                                                        # derived from that class can become a target)
                                                                        # list length delimited by num of props 
                                                                        # ("inheritanceDepth" * "propertiesPerLevel")
}
"hasRepresentation": {
    "targets": "targetClass" | ["targetClassOfProp1", ...]              # default=resources from all classes derived from
                                                                        # a multimedia representation can become a target.
                                                                        # list length delimited by num of props 
                                                                        # ("inheritanceDepth" * "propertiesPerLevel")
}


### Structure of the "cardinalities" section

There are some shared elements that can be used in every cardinality:
```
cardinalities: {
    "hasValue_TextValue" | "hasValue_ColorValue" | "hasValue_DateValue" | "hasValue_TimeValue" | 
    "hasValue_DecimalValue" | "hasValue_GeomValue" | "hasValue_GeonameValue" | "hasValue_IntValue" | 
    "hasValue_BooleanValue" | "hasValue_UriValue" | "hasValue_IntervalValue" | "hasValue_ListValue" | 
    "hasColor" | "hasComment" | "hasLinkTo" | 
    "hasRepresentation" : 0-x  | {                                      # 0-x is the "numOfProps"
        "numOfProps": 1-x,                                              # default=1, x=existing props as defined in "properties"
                                                                        # ("inheritanceDepth" * "propertiesPerLevel")
        "numOfValuesPerProp": 1-100 | [1-100, 1-100, ...],              # default=1
        "cardinality": "0-1|0-n|1|1-n" | ["0-1|0-n|1|1-n", ...],        # default, or if in conflict with "numOfValuesPerProp": "0-n"
        "permissions": [one or more permission strings from above],     # default=the first permission from above
        "comment": "Your comment" | ["Your comment", ...]               # default=None
}
```

In addition to the elements common to every cardinality, some cardinalities can contain individual definitions:
```
cardinalities: {
    "hasValue_TextValue": {                                      
        "gui_elements": ["SimpleText", "Richtext", "Textarea"],         # default=["SimpleText"], delimited by "numOfProps" and "properties"
        "encodings": ["xml", "utf8"],                                   # default=["utf8"], can be overridden by salsah-links
        "salsah-links": true | false                                    # default determined by definition above
    },
    "hasValue_DateValue": {
        "dateRanges": true | false,                                     # default=false
        "calendars": ["JULIAN", "GREGORIAN"],                           # default=["GREGORIAN"]
        "epochs": ["BCE", "CE"],                                        # default=["CE"]
        "precisionsUpTo": ["year", "month", "day"]                       # default=["day"]
    },
    "hasValue_TimeValue": {
        "rangeOfYears": "0001-2022",                                    # default="0001-2022"
        "rangeOfMonthes": "01-12",                                      # default="01-12"
        "rangeOfDays": "01-31",                                         # default="01-31"
        "rangeOfHours": "00-23",                                        # default="00-23"
        "rangeOfMinutes": "00-59",                                      # default="00-59"
        "rangeOfSeconds": "00-59",                                      # default="00-59"
        "rangeOfFractionalSeconds": "01-02",                            # default="000000000000-999999999999"
        "rangeOfTimeZones": ["Z", "+01:00", "-05:00", "-14:00"]         # default=["Z"]
    },
    "hasValue_DecimalValue": {
        "range": "2.30-2.39",                                           # default="0.000-9999.999"
        "gui_elements": ["Slider", "SimpleText"]                        # default=["SimpleText"], delimited by "numOfProps" and "properties"
    },
    "hasValue_GeomValue": {
        "status": ["active", "deleted"],                                # default=["active"]
        "types": ["circle", "rectangle", "polygon"],                    # default=["circle"]
        "lineColors": ["#ff0000", ...],                                 # default=["#ff0000"]
        "lineWidths": [1-20, 1-20, ...],                                # default=[1]
        "numOfPoints": 3-10                                             # for polygons; default=3
    },
    "hasValue_IntValue": {
        "gui_elements": ["Spinbox", "SimpleText"]                       # default=["SimpleText"], delimited by "numOfProps" and "properties"
    },
    "hasValue_IntervalValue": {
        "gui_elements": ["Interval", "SimpleText"],                     # default=["SimpleText"]
        "decimalMin": 0.0001-9999.99,                                   # default=0.0001
        "decimalMax": 0.0001-9999.99                                    # default=9999.99
    },
    "hasValue_ListValue": {
        "gui_elements": ["Radio", "List"],                              # default=["List"], delimited by "numOfProps" and "properties"
        "hlist": 1-20                                                   # number of list from lists[numOfLists]; default=1
    },
    "hasComment": {
        "commentText": "Your text"                                      # default="My comment"
    },
    "hasLinkTo": {
        "targets": "targetClass" | ["targetClassOfProp1", ...]          # default="Resource" (resources from all classes
                                                                        # derived from that class can become a target)
    }
    "hasRepresentation": {
        "targets": "targetClass" | ["targetClassOfProp1", ...]          # default=resources from all classes derived from
                                                                        # a multimedia representation can become a target
    }
```

## Explanations
### properties
Every propclass that appears in "cardinalities" can appear in this section. Here is defined how many 
propclasses of this class will be created. Depending on how a resource is defined, there will 
be a big number of resclasses that all hold the same cardinalities. These cardinalities can be composed
of the same propclass again and again, or of different propclasses that are akin. Exactly this is defined
here. An example may clarify it. The following is a valid `config.json`:
```
{
    "resources": {
        "Resource": {
            "inheritanceDepth": 1,
            "classesPerInheritanceLevel": 3,
            "resourcesPerClass": 1,
            "cardinalities": {
                "hasValue_TextValue" : 1,
                "hasValue_IntValue" : 1
            }
        },
        "StillImageRepresentation": {
            "inheritanceDepth": 1,
            "classesPerInheritanceLevel": 3,
            "resourcesPerClass": 1,
            "cardinalities": {
                "hasValue_TextValue" : 1,
                "hasValue_IntValue" : 1
            }
        }
    },
    "properties": {
        "hasValue_TextValue": {
            "inheritanceDepth": 2,
            "propertiesPerLevel": 2
        }
    }
}
```

This `config.json` demonstrates the influence of the "properties" section on the cardinalities:
 - There will be 4 property classes derived from "hasValue_TextValue", and they will be distributed on
the resource classes.
 - "hasValue_IntValue" doesn't appear in the "properties", so the default values 1 and 1 are used, so
every resource class receives "hasValue_IntValue_class_1"

This `config.json` will create the following ontology:
 - Resource_class_1
   - hasValue_TextValue_class_1
   - hasValue_IntValue_class_1
 - Resource_class_2
   - hasValue_TextValue_class_1_subclass_1
   - hasValue_IntValue_class_1
 - Resource_class_3
   - hasValue_TextValue_class_1_subclass_2
   - hasValue_IntValue_class_1
 - StillImageRepresentation_class_1
   - hasValue_TextValue_class_2
   - hasValue_IntValue_class_1
 - StillImageRepresentation_class_2
   - hasValue_TextValue_class_2_subclass_1
   - hasValue_IntValue_class_1
 - StillImageRepresentation_class_3
   - hasValue_TextValue_class_2_subclass_2
   - hasValue_IntValue_class_1
