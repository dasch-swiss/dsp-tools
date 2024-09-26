import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.xml_validate.sparql.resource_shacl import _construct_resource_nodeshape
from dsp_tools.commands.xml_validate.sparql.resource_shacl import construct_resource_class_node_shape

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")
PREFIXES = """
@prefix knora-api: <http://api.knora.org/ontology/knora-api/v2#> .
@prefix onto: <http://0.0.0.0:3333/ontology/9999/onto/v2#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix salsah-gui: <http://api.knora.org/ontology/salsah-gui/v2#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""


@pytest.fixture
def onto_graph() -> Graph:
    g = Graph()
    g.parse("testdata/xml-validate/onto.ttl")
    return g


@pytest.fixture
def one_res_one_prop() -> Graph:
    ttl = (
        PREFIXES
        + """
    onto:CardOneResource a owl:Class ;
    rdfs:label "Resource with One Cardinality" ;
    knora-api:canBeInstantiated true ;
    knora-api:isResourceClass true ;
    rdfs:subClassOf 
        knora-api:Resource ,
        [ a owl:Restriction ;
            knora-api:isInherited true ;
            owl:maxCardinality 1 ;
            owl:onProperty knora-api:versionDate ],
        [ a owl:Restriction ;
            knora-api:isInherited true ;
            salsah-gui:guiOrder 0 ;
            owl:cardinality 1 ;
            owl:onProperty onto:testBoolean ] .
    
    onto:testBoolean a owl:ObjectProperty ;
        rdfs:label "Test Boolean" ;
        knora-api:isEditable true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType knora-api:BooleanValue ;
        salsah-gui:guiElement salsah-gui:Checkbox ;
        rdfs:subPropertyOf knora-api:hasValue .
    """
    )
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def one_prop() -> Graph:
    ttl = (
        PREFIXES
        + """
    onto:testBoolean a owl:ObjectProperty ;
        rdfs:label "Test Boolean" ;
        knora-api:isEditable true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType knora-api:BooleanValue ;
        salsah-gui:guiElement salsah-gui:Checkbox ;
        rdfs:subPropertyOf knora-api:hasValue .
    """
    )
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def card_1() -> Graph:
    ttl = (
        PREFIXES
        + """
    onto:ClassMixedCard a owl:Class ;
        rdfs:subClassOf [ 
                a owl:Restriction ;
                salsah-gui:guiOrder 0 ;
                owl:cardinality 1 ;
                owl:onProperty onto:testBoolean
                         ] .
    """
    )
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def card_0_1() -> Graph:
    ttl = (
        PREFIXES
        + """
    onto:ClassMixedCard a owl:Class ;
        rdfs:subClassOf [ 
                a owl:Restriction ;
                salsah-gui:guiOrder 1 ;
                owl:maxCardinality 1 ;
                owl:onProperty onto:testDecimalSimpleText
                         ] .

    """
    )
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def card_1_n() -> Graph:
    ttl = (
        PREFIXES
        + """
    onto:ClassMixedCard a owl:Class ;
        rdfs:subClassOf [ 
                a owl:Restriction ;
                salsah-gui:guiOrder 2 ;
                owl:minCardinality 1 ;
                owl:onProperty onto:testGeoname
                         ] .

    """
    )
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def card_0_n() -> Graph:
    ttl = (
        PREFIXES
        + """
    onto:ClassMixedCard a owl:Class ;
        rdfs:subClassOf [ 
                a owl:Restriction ;
                salsah-gui:guiOrder 3 ;
                owl:minCardinality 0 ;
                owl:onProperty onto:testSimpleText
                         ] .
    """
    )
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


def test_construct_resource_class_nodeshape(onto_graph: Graph) -> None:
    result = construct_resource_class_node_shape(onto_graph)
    num_triples = 42
    assert len(result) == num_triples
    shape_iri = next(result.subjects(SH.targetClass, ONTO.ClassInheritedCardinality))
    assert shape_iri == ONTO.ClassInheritedCardinality_Shape
    shape_iri = next(result.subjects(SH.targetClass, ONTO.ClassMixedCard))
    assert shape_iri == ONTO.ClassMixedCard_Shape
    shape_iri = next(result.subjects(SH.targetClass, ONTO.CardOneResource))
    assert shape_iri == ONTO.CardOneResource_Shape
    shape_iri = next(result.subjects(SH.targetClass, ONTO.ClassWithEverything))
    assert shape_iri == ONTO.ClassWithEverything_Shape
    shape_iri = next(result.subjects(SH.targetClass, ONTO.TestStillImageRepresentation))
    assert shape_iri == ONTO.TestStillImageRepresentation_Shape
    shape_iri = next(result.subjects(SH.targetClass, ONTO.ClassInheritedCardinalityOverwriting))
    assert shape_iri == ONTO.ClassInheritedCardinalityOverwriting_Shape


def test_construct_resource_nodeshape_one_res(one_res_one_prop: Graph) -> None:
    result = _construct_resource_nodeshape(one_res_one_prop)
    subjects = {iri for x in result.triples((None, None, None)) if not isinstance(iri := x[0], BNode)}
    assert len(subjects) == 1
    subject_iri = subjects.pop()
    assert subject_iri == ONTO.CardOneResource_Shape
    node_triples = list(result.triples((subject_iri, None, None)))
    num_triples = 5
    assert len(node_triples) == num_triples
    assert next(result.subjects(RDF.type, SH.NodeShape)) == subject_iri
    assert next(result.subjects(SH.property, API_SHAPES.RDFS_label)) == subject_iri
    assert next(result.subjects(SH.ignoredProperties)) == subject_iri
    assert next(result.objects(subject_iri, SH.closed)) == Literal(True)


def test_construct_resource_nodeshape_no_res(one_prop: Graph) -> None:
    result = _construct_resource_nodeshape(one_prop)
    assert len(result) == 0


if __name__ == "__main__":
    pytest.main([__file__])
