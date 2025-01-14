# Change Log: validate-data


## PR: https://github.com/dasch-swiss/dsp-tools/pull/1360

Changing the internal Python representation of the data.
A Python dataclass structure between the input XML and the data as an `rdflib` graph is added
that is agnostic to both the specifications of the XML and the data structure required by the API.

The structure of the main Python classes `PropertyObject` and `ReifiedPropertyObject` are generic
and do not rely on a specific property, object or object data type.
Both of these classes represent a part of an RDF triple,
the subject of the triple is the dataclass which contains the `PropertyObject` and `ReifiedPropertyObject`.

Below are graphs to illustrate where the information contained in the classes will be located in the final graph.

**`PropertyObject`**

```
flowchart TD
    A(Resource or Value) -->|:RDF/RDFS/knora Property| B[object Value]
```


**`ReifiedPropertyObject`**

```
flowchart TD
    C(Resource) -->|:ontologyProperty| D[PropertyObject]
    D -->|:RDF/RDFS/knora Property| E[object Value]
```
