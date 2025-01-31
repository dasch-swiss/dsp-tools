# Input from user

```
:nonRelatedProp a owl:Objectproperty .

:hasText0 a owl:Objectproperty .

:hasTextSubProp1 a owl:Objectpropert ;
	rdfs:subPropertyOf :hasText0 .


:Resource0 a owl:Class .

:Resource0 cardinality 1 for property :nonRelatedProp .
:Resource0 cardinality 1 for property :hasText0 .

:ResourceSubCls1 a owl:Class ;
	rdfs:subClassOf :Resource0 .

:ResourceSubCls1 cardinality 1 for property :hasTextSubProp1 .
```


# Resulting ontology from API

```
:ResourceSubCls1 cardinality 1 for property :nonRelatedProp .  # this is inherited from :Resource0
:ResourceSubCls1 cardinality 1 for property :hasTextSubProp1 .
```

-> `:Resource0` has a cardinality for `:hasText0`, and `:ResourceSubCls1` inherits the cardinalities from `:Resource0`, as shown in `:nonRelatedProp` .
-> If the cardinality is on a property where the sub-class (`:ResourceSubCls1`) has a cardinality for a sub-property (`:hasTextSubProp1`) the cardinality from the super-class (`:Resource0`) on the super-property (`:hasText0`) is not inherited.
-> An instance of `:ResourceSubCls1` does not require `:hasTextSubProp1` for the API. The following is correct:

```
data:InstanceResourceSubCls1 a :ResourceSubCls1 ;
	:hasTextSubProp1 "Required Property 1" .
```

-> In SHACL it expects `data:InstanceResourceSubCls1` to have a `:hasText0` . The following is correct:

```
data:InstanceResourceSubCls1 a :ResourceSubCls1 ;
	:hasText0 "Required Property 0" ;
	:hasTextSubProp1 "Required Property 1" .
```

-> The API does not accept that it reacts to it with:
`OntologyConstraintException: Resource class <http://0.0.0.0:3333/ontology/9990/onto/v2#ResourceSubCls1> has no cardinality for property <http://www.knora.org/ontology/9990/onto#hasText0>`

-> What behaviour do we want?
-> Why is rdfs inference not taking care of this?

# Test with real data

- Check out the branch to use the command (validation is different)

- `dsp-tools create testdata/validate-data/inheritance/project_inheritance.json`

- `dsp-tools validate-data testdata/validate-data/inheritance/inheritance_correct.xml`

-> here `inheritance_correct_for_api` will be wrong


- `dsp-tools xmlupload testdata/validate-data/inheritance/inheritance_correct.xml`

-> here `inheritance_correct_for_shacl` will not be uploaded