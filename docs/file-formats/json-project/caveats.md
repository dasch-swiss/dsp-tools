[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Caveats when Working With a JSON Project File

## Referencing Ontologies

For several fields (e.g. `super` in both `resources` and `properties`, or `propname` in `cardinalities`),
it is necessary to reference entities that are defined elsewhere. The following cases are possible:

- DSP-API internals: 
    - They are referenced as such and do not have a leading colon,  
      e.g. `Resource`, `DocumentRepresentation` or `hasValue`
- An external ontology: 
    - The prefix of the ontology must be declared in the ["prefixes"](./overview.md#prefixes) object.
    - The prefix can then be used for referencing the corresponding external ontology,  
      e.g. `foaf:familyName` or `sdo:Organization`
- The current ontology: 
    - Within the same ontology, references can be made by prepending a colon without a prefix `:`,  
      e.g. `:hasName`.
    - Optionally, the current ontology can be referenced by its `name`,  
      e.g. `sameOnto:hasName`
    - It is not necessary to add `sameOnto` to the ["prefixes"](./overview.md#prefixes) object.
- A different ontology defined in the same file: 
    - Within one data model file, multiple ontologies can be defined.
      These will be created in the exact order they appear in the `ontologies` array. 
    - Once an ontology has been created,
      it can be referenced by the following ontologies by its `name`,  
      e.g. `first-onto:hasName`
    - It is not necessary to add `first-onto` to ["prefixes"](./overview.md#prefixes) object.




## DSP Base Resources and Base Properties to be Used Directly in the XML File

From several DSP base resources, no subclasses can be created in a project ontology. 
However, they can be used directly in the XML data file:

- `Annotation` is an annotation to another resource of any class. 
  It can be used in the XML file with the [&lt;annotation&gt; tag](../xml-data-file.md#annotation) and 
  has the following predefined properties:
    - `hasComment` (1-n)
    - `isAnnotationOf` (1)
- `LinkObj` is a resource linking together several other resources of different classes. 
  It can be used in the XML file with the [&lt;link&gt; tag](../xml-data-file.md#link) and 
  has the following predefined properties:
    - `hasComment` (1-n)
    - `hasLinkTo` (1-n)
- A `Region` resource defines a region of interest (ROI) in an image. 
  It can be used in the XML file with the [&lt;region&gt; tag](../xml-data-file.md#region) and 
  has the following predefined properties:
    - `hasColor` (1)
    - `isRegionOf` (1)
    - `hasGeometry` (1)
    - `hasComment` (1-n)

There are some DSP base properties that are used directly in the above-mentioned resource classes. 
Subclasses can be created from some of them in the project ontology.

- `hasLinkTo`: a link to another resource
    - subclasses can be created from it ([hasLinkTo Property](./ontologies.md#haslinkto-property))
    - can be used directly in the XML data file in the [&lt;link&gt; tag](../xml-data-file.md#link)
- `hasColor`: Defines a color value. 
    - subclasses can be created from it ([ColorValue](./ontologies.md#colorvalue))
    - can be used directly in the XML data file in the [&lt;region&gt; tag](../xml-data-file.md#region)
- `hasComment`: Defines a standard comment. 
    - subclasses can be created from it ([hasComment Property](./ontologies.md#hascomment-property))
    - can be used directly in the XML data file in the [&lt;region&gt; tag](../xml-data-file.md#region) or 
      [&lt;link&gt; tag](../xml-data-file.md#link)
- `hasGeometry`: Defines a geometry value (a JSON describing a polygon, circle or rectangle). 
    - must be used directly in the XML data file in the [&lt;region&gt; tag](../xml-data-file.md#region)
- `isRegionOf`: A special variant of `hasLinkTo`. 
  It means that the given resource class is a region of interest in an image. 
    - must be used directly in the XML data file in the [&lt;region&gt; tag](../xml-data-file.md#region)
- `isAnnotationOf`: A special variant of `hasLinkTo`. It means that the given resource class is an annotation to another
  resource class. 
    - must be used directly in the XML data file in the 
  [&lt;annotation&gt; tag](../xml-data-file.md#annotation)
