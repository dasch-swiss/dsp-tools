import pytest
from rdflib import Graph
from rdflib import Namespace

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
    g.parse("testdata/data-validate/onto.ttl")
    return g


@pytest.fixture
def one_res_one_prop() -> Graph:
    ttl = f"""{PREFIXES}
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
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def one_prop() -> Graph:
    ttl = f"""{PREFIXES}
    onto:testBoolean a owl:ObjectProperty ;
        rdfs:label "Test Boolean" ;
        knora-api:isEditable true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType knora-api:BooleanValue ;
        salsah-gui:guiElement salsah-gui:Checkbox ;
        rdfs:subPropertyOf knora-api:hasValue .
    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def card_1() -> Graph:
    ttl = f"""{PREFIXES}
    onto:ClassMixedCard a owl:Class ;
        knora-api:isResourceClass true ;
        knora-api:canBeInstantiated true ;
        rdfs:subClassOf [ 
                a owl:Restriction ;
                salsah-gui:guiOrder 0 ;
                owl:cardinality 1 ;
                owl:onProperty onto:testBoolean
                         ] .
    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def card_0_1() -> Graph:
    ttl = f"""{PREFIXES}
    onto:ClassMixedCard a owl:Class ;
        knora-api:isResourceClass true ;
        knora-api:canBeInstantiated true ;
        rdfs:subClassOf [ 
                a owl:Restriction ;
                salsah-gui:guiOrder 1 ;
                owl:maxCardinality 1 ;
                owl:onProperty onto:testDecimalSimpleText
                         ] .
    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def card_1_n() -> Graph:
    ttl = f"""{PREFIXES}
    onto:ClassMixedCard a owl:Class ;
        knora-api:isResourceClass true ;
        knora-api:canBeInstantiated true ;
        rdfs:subClassOf [ 
                a owl:Restriction ;
                salsah-gui:guiOrder 2 ;
                owl:minCardinality 1 ;
                owl:onProperty onto:testGeoname
                         ] .
    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def card_0_n() -> Graph:
    ttl = f"""{PREFIXES}
    onto:ClassMixedCard a owl:Class ;
        knora-api:isResourceClass true ;
        knora-api:canBeInstantiated true ;
        rdfs:subClassOf [ 
                a owl:Restriction ;
                salsah-gui:guiOrder 3 ;
                owl:minCardinality 0 ;
                owl:onProperty onto:testSimpleText
                         ] .
    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def one_bool_prop() -> Graph:
    ttl = f"""{PREFIXES}
    onto:testBoolean a owl:ObjectProperty ;
        rdfs:label "Test Boolean" ;
        knora-api:isEditable true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType knora-api:BooleanValue ;
        salsah-gui:guiElement salsah-gui:Checkbox ;
        rdfs:subPropertyOf knora-api:hasValue .
    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def one_richtext_prop() -> Graph:
    ttl = f"""{PREFIXES}
    onto:testRichtext a owl:ObjectProperty ;
        rdfs:label "Test Richtext" ;
        knora-api:isEditable true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType knora-api:TextValue ;
        salsah-gui:guiElement salsah-gui:Richtext ;
        rdfs:subPropertyOf knora-api:hasValue .
    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def link_prop_card_1() -> Graph:
    ttl = f"""{PREFIXES}
    onto:ClassMixedCard a owl:Class ;
    rdfs:label "Resource with all cardinality options" ;
    knora-api:canBeInstantiated true ;
    knora-api:isResourceClass true ;
    rdfs:subClassOf [ 
            a owl:Restriction ;
            salsah-gui:guiOrder 1 ;
            owl:cardinality 1 ;
            owl:onProperty onto:testHasLinkToCardOneResourceValue 
            ] ,
            [ a owl:Restriction ;
            salsah-gui:guiOrder 1 ;
            owl:cardinality 1 ;
            owl:onProperty onto:testHasLinkToCardOneResource ] .
            
    onto:testHasLinkToCardOneResource a owl:ObjectProperty ;
        rdfs:label "Super-class" ;
        knora-api:isEditable true ;
        knora-api:isLinkProperty true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType onto:CardOneResource ;
        salsah-gui:guiElement salsah-gui:Searchbox ;
        rdfs:subPropertyOf knora-api:hasLinkTo .
    
    onto:testHasLinkToCardOneResourceValue a owl:ObjectProperty ;
        rdfs:label "Super-class" ;
        knora-api:isEditable true ;
        knora-api:isLinkValueProperty true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType knora-api:LinkValue ;
        salsah-gui:guiElement salsah-gui:Searchbox ;
        rdfs:subPropertyOf knora-api:hasLinkToValue .

    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g


@pytest.fixture
def link_prop_card_01() -> Graph:
    ttl = f"""{PREFIXES}
    onto:ClassMixedCard a owl:Class ;
    rdfs:label "Resource with all cardinality options" ;
    knora-api:canBeInstantiated true ;
    knora-api:isResourceClass true ;
    rdfs:subClassOf [ 
            a owl:Restriction ;
            salsah-gui:guiOrder 1 ;
            owl:maxCardinality 1 ;
            owl:onProperty onto:testHasLinkToCardOneResourceValue 
            ] ,
            [ a owl:Restriction ;
            salsah-gui:guiOrder 1 ;
            owl:maxCardinality 1 ;
            owl:onProperty onto:testHasLinkToCardOneResource ] .

    onto:testHasLinkToCardOneResource a owl:ObjectProperty ;
        rdfs:label "Super-class" ;
        knora-api:isEditable true ;
        knora-api:isLinkProperty true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType onto:CardOneResource ;
        salsah-gui:guiElement salsah-gui:Searchbox ;
        rdfs:subPropertyOf knora-api:hasLinkTo .

    onto:testHasLinkToCardOneResourceValue a owl:ObjectProperty ;
        rdfs:label "Super-class" ;
        knora-api:isEditable true ;
        knora-api:isLinkValueProperty true ;
        knora-api:isResourceProperty true ;
        knora-api:objectType knora-api:LinkValue ;
        salsah-gui:guiElement salsah-gui:Searchbox ;
        rdfs:subPropertyOf knora-api:hasLinkToValue .

    """
    g = Graph()
    g.parse(data=ttl, format="ttl")
    return g
