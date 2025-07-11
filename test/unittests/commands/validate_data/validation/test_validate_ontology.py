from rdflib import Graph

from dsp_tools.commands.validate_data.validation.validate_ontology import _reformat_ontology_validation_result


def test_reformat_ontology_validation_result() -> None:
    val_result = """
    @prefix api-shapes: <http://api.knora.org/ontology/knora-api/shapes/v2#> .
    @prefix knora-api: <http://api.knora.org/ontology/knora-api/v2#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    
    [ a sh:ValidationResult ;
            sh:focusNode <http://0.0.0.0:3333/ontology/9991/error/v2#ImageWithKnoraProp_MissingSeqnum> ;
            sh:resultMessage "Message from the turtle file" ;
            sh:resultPath knora-api:isPartOf ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraint _:n5badee8ae46f40828e18b000160a9e58b9 ;
            sh:sourceConstraintComponent sh:SPARQLConstraintComponent ;
            sh:sourceShape api-shapes:FindCardinalityMismatchSeqnum_OntologyShape ;
            sh:value <http://0.0.0.0:3333/ontology/9991/error/v2#ImageWithKnoraProp_MissingSeqnum> ] .
    """
    g = Graph()
    g.parse(data=val_result, format="ttl")
    reformatted = _reformat_ontology_validation_result(g)
    assert len(reformatted) == 1
    result = reformatted.pop(0)
    assert result.res_iri == "error:ImageWithKnoraProp_MissingSeqnum"
    assert result.msg == "Message from the turtle file"
