import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.validation import CardinalityValidationResult
from dsp_tools.commands.validate_data.models.validation import ContentValidationResult
from dsp_tools.commands.validate_data.models.validation import ResourceValidationReportIdentifiers
from test.unittests.commands.validate_data.constants import DASH
from test.unittests.commands.validate_data.constants import DATA
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO
from test.unittests.commands.validate_data.constants import PREFIXES


@pytest.fixture
def id_card_one() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
    gstr = f"""{PREFIXES}
    [ a sh:ValidationResult ;
            sh:focusNode <http://data/id_card_one> ;
            sh:resultMessage "1" ;
            sh:resultPath onto:testBoolean ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
            sh:sourceShape [ ] ] .
    """
    result = Graph()
    result.parse(data=gstr, format="ttl")
    datastr = f"""{PREFIXES}
    <http://data/id_card_one> a onto:ClassInheritedCardinalityOverwriting ;
        rdfs:label "Bool Card 1"^^xsd:string .
    """
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(result.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/id_card_one"), ONTO.ClassInheritedCardinalityOverwriting
    )
    return result, data, identifiers


@pytest.fixture
def id_simpletext() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
    gstr = f'''{PREFIXES}
    [ a sh:ValidationResult ;
            sh:detail _:bn_id_simpletext ;
            sh:focusNode <http://data/id_simpletext> ;
            sh:resultMessage """Value does not have shape 
                    <http://api.knora.org/ontology/knora-api/shapes/v2#SimpleTextValue_ClassShape>""" ;
            sh:resultPath onto:testTextarea ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:NodeConstraintComponent ;
            sh:sourceShape onto:testTextarea_PropShape ;
            sh:value <http://data/value_id_simpletext> ] .
            
    _:bn_id_simpletext a sh:ValidationResult ;
        sh:focusNode <http://data/value_id_simpletext> ;
        sh:resultMessage "TextValue without formatting" ;
        sh:resultPath knora-api:valueAsString ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
        sh:sourceShape api-shapes:SimpleTextValue_PropShape .
    '''
    g = Graph()
    g.parse(data=gstr, format="ttl")
    datastr = f"""{PREFIXES}
    <http://data/id_simpletext> a onto:ClassWithEverything ;
        rdfs:label "Simpletext"^^xsd:string ;
        onto:testTextarea <http://data/value_id_simpletext> .
        
    <http://data/value_id_simpletext> a knora-api:TextValue ;
        knora-api:textValueAsXml "Text"^^xsd:string .
    """
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/id_simpletext"), ONTO.ClassWithEverything
    )
    return g, data, identifiers


@pytest.fixture
def id_uri() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
    gstr = f'''{PREFIXES}
    [ a sh:ValidationResult ;
                sh:detail _:bn_id_uri ;
                sh:focusNode <http://data/id_uri> ;
                sh:resultMessage """Value does not have shape 
            <http://api.knora.org/ontology/knora-api/shapes/v2#UriValue_ClassShape>""" ;
                sh:resultPath onto:testUriValue ;
                sh:resultSeverity sh:Violation ;
                sh:sourceConstraintComponent sh:NodeConstraintComponent ;
                sh:sourceShape onto:testUriValue_PropShape ;
                sh:value <http://data/value_id_uri> ] .
    
    _:bn_id_uri a sh:ValidationResult ;
        sh:focusNode <http://data/value_id_uri> ;
        sh:resultMessage "UriValue" ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:ClassConstraintComponent ;
        sh:sourceShape api-shapes:UriValue_ClassShape ;
        sh:value <http://data/value_id_uri> .
    '''
    g = Graph()
    g.parse(data=gstr, format="ttl")
    datastr = f"""{PREFIXES}
    <http://data/id_uri> a onto:ClassWithEverything ;
        rdfs:label "Uri"^^xsd:string ;
        onto:testUriValue <http://data/value_id_uri> .
    
    <http://data/value_id_uri> a knora-api:TextValue ;
        knora-api:valueAsString "https://dasch.swiss"^^xsd:string .
    """
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(val_bn, URIRef("http://data/id_uri"), ONTO.ClassWithEverything)
    return g, data, identifiers


@pytest.fixture
def geoname_not_number() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
    gstr = f'''{PREFIXES}
    [ a sh:ValidationResult ;
                sh:detail _:bn_geoname_not_number ;
                sh:focusNode <http://data/geoname_not_number> ;
                sh:resultMessage """Value does not have shape 
                        <http://api.knora.org/ontology/knora-api/shapes/v2#GeonameValue_ClassShape>""" ;
                sh:resultPath onto:testGeoname ;
                sh:resultSeverity sh:Violation ;
                sh:sourceConstraintComponent sh:NodeConstraintComponent ;
                sh:sourceShape onto:testGeoname_PropShape ;
                sh:value <http://data/value_geoname_not_number> ] .
                
    _:bn_geoname_not_number a sh:ValidationResult ;
        sh:focusNode <http://data/value_geoname_not_number> ;
        sh:resultMessage "The value must be a valid geoname code" ;
        sh:resultPath knora-api:geonameValueAsGeonameCode ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:PatternConstraintComponent ;
        sh:sourceShape api-shapes:geonameValueAsGeonameCode_Shape ;
        sh:value "this-is-not-a-valid-code" .
    '''
    g = Graph()
    g.parse(data=gstr, format="ttl")
    datastr = f"""{PREFIXES}
    <http://data/geoname_not_number> a onto:ClassWithEverything ;
        rdfs:label "Geoname is not a number"^^xsd:string ;
        onto:testGeoname <http://data/value_geoname_not_number> .
        
    <http://data/value_geoname_not_number> a knora-api:GeonameValue ;
        knora-api:geonameValueAsGeonameCode "this-is-not-a-valid-code"^^xsd:string .
    """
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/geoname_not_number"), ONTO.ClassWithEverything
    )
    return g, data, identifiers


@pytest.fixture
def id_closed_constraint() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
    gstr = f'''{PREFIXES}
    [ a sh:ValidationResult ;
                sh:focusNode <http://data/id_closed_constraint> ;
                sh:resultMessage """Property onto:testIntegerSimpleText 
                                is not among those permitted for any of the types""" ;
                sh:resultPath onto:testIntegerSimpleText ;
                sh:resultSeverity sh:Violation ;
                sh:sourceConstraintComponent dash:ClosedByTypesConstraintComponent ;
                sh:sourceShape onto:CardOneResource ;
                sh:value <http://data/value_id_closed_constraint> ] .
    '''
    g = Graph()
    g.parse(data=gstr, format="ttl")
    datastr = f"""{PREFIXES}
    <http://data/id_closed_constraint> a onto:CardOneResource ;
        rdfs:label "Int card does not exist"^^xsd:string ;
        onto:testIntegerSimpleText <http://data/value_id_closed_constraint> .
    <http://data/value_id_closed_constraint> a knora-api:IntValue ;
        knora-api:intValueAsInt 1 .
    """
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/id_closed_constraint"), ONTO.CardOneResource
    )
    return g, data, identifiers


@pytest.fixture
def id_max_card() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
    gstr = f"""{PREFIXES}
    [ a sh:ValidationResult ;
                sh:focusNode <http://data/id_max_card> ;
                sh:resultMessage "1" ;
                sh:resultPath onto:testHasLinkToCardOneResource ;
                sh:resultSeverity sh:Violation ;
                sh:sourceConstraintComponent sh:MaxCountConstraintComponent ;
                sh:sourceShape [ ] ] .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    datastr = f"""{PREFIXES}
    <http://data/id_max_card> a onto:ClassMixedCard ;
        rdfs:label "Decimal Card 0-1"^^xsd:string ;
        onto:testHasLinkToCardOneResource <http://data/value_1> , <http://data/value_2> .
            
    <http://data/value_1> a knora-api:LinkValue ;
        api-shapes:linkValueHasTargetID <http://data/id_card_one> .
    <http://data/value_2> a knora-api:LinkValue ;
        api-shapes:linkValueHasTargetID <http://data/id_closed_constraint> .
    """
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(val_bn, URIRef("http://data/id_max_card"), ONTO.ClassMixedCard)
    return g, data, identifiers


@pytest.fixture
def graph_min_count_violation() -> Graph:
    gstr = f"""{PREFIXES}
    [ a sh:ValidationResult ;
            sh:focusNode <http://data/id_min_card> ;
            sh:resultMessage "1-n" ;
            sh:resultPath onto:testGeoname ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
            sh:sourceShape [ ] ] .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def data_min_count_violation() -> Graph:
    gstr = "<http://data/id_min_card> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassMixedCard> ."
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def graph_closed_constraint() -> Graph:
    gstr = f"""{PREFIXES}
    [ a sh:ValidationResult ;
            sh:focusNode <http://data/id_closed_constraint> ;
            sh:resultMessage "Property onto:testIntegerSimpleText is not among those permitted for any of the types" ;
            sh:resultPath onto:testIntegerSimpleText ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent dash:ClosedByTypesConstraintComponent ;
            sh:sourceShape onto:CardOneResource ;
            sh:value <http://data/val-id_closed_constraint> ] .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def data_closed_constraint() -> Graph:
    gstr = "<http://data/id_closed_constraint> a <http://0.0.0.0:3333/ontology/9999/onto/v2#CardOneResource> ."
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def graph_max_card_violation() -> Graph:
    gstr = f"""{PREFIXES}
    [ a sh:ValidationResult ;
            sh:focusNode <http://data/id_max_card> ;
            sh:resultMessage "1" ;
            sh:resultPath onto:testHasLinkToCardOneResource ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:MaxCountConstraintComponent ;
            sh:sourceShape [ ] ] .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def data_max_card_count_violation() -> Graph:
    gstr = "<http://data/id_max_card> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassMixedCard> ."
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def graph_value_type_mismatch() -> Graph:
    gstr = f'''{PREFIXES}
    [] a sh:ValidationReport ;
    sh:result _:bn_value_type_mismatch .

    [] a sh:ValidationReport ;
    sh:conforms false ;
    sh:result [ 
            a sh:ValidationResult ;
            sh:detail _:bn_value_type_mismatch ;
            sh:focusNode <http://data/value_type_mismatch> ;
            sh:resultMessage """Value does not have shape
                 <http://api.knora.org/ontology/knora-api/shapes/v2#ColorValue_ClassShape>""" ;
            sh:resultPath onto:testColor ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:NodeConstraintComponent ;
            sh:sourceShape onto:testColor_PropShape ;
            sh:value <http://data/value-iri-value_type_mismatch> 
            ] .

    _:bn_value_type_mismatch a sh:ValidationResult ;
    sh:focusNode <http://data/value-iri> ;
    sh:resultMessage "ColorValue" ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:ClassConstraintComponent ;
    sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#ColorValue_ClassShape> ;
    sh:value <http://data/value-iri-value_type_mismatch> .
    '''
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def data_value_type_mismatch() -> Graph:
    gstr = """
    <http://data/value_type_mismatch> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything> .
    <http://data/value-iri-value_type_mismatch> a <http://api.knora.org/ontology/knora-api/v2#TextValue> .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def graph_wrong_regex_content() -> Graph:
    gstr = f'''{PREFIXES}
    [] a sh:ValidationReport ;
    sh:result _:bn_geoname_not_number .

    [] a sh:ValidationReport ;
    sh:conforms false ;
    sh:result [ a sh:ValidationResult ;
            sh:detail _:bn_geoname_not_number ;
            sh:focusNode <http://data/geoname_not_number> ;
            sh:resultMessage """Value does not have shape 
                                        <http://api.knora.org/ontology/knora-api/shapes/v2#GeonameValue_ClassShape>""" ;
            sh:resultPath onto:testGeoname ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:NodeConstraintComponent ;
            sh:sourceShape onto:testGeoname_PropShape ;
            sh:value <http://data/value-iri-geoname_not_number> ] .

    _:bn_geoname_not_number a sh:ValidationResult ;
    sh:focusNode <http://data/value-iri-geoname_not_number> ;
    sh:resultMessage "The value must be a valid geoname code" ;
    sh:resultPath knora-api:geonameValueAsGeonameCode ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:PatternConstraintComponent ;
    sh:sourceShape api-shapes:geonameValueAsGeonameCode_Shape ;
    sh:value "this-is-not-a-valid-code" .
    '''
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def data_wrong_regex_content() -> Graph:
    gstr = """
    <http://data/geoname_not_number> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything> .
    <http://data/value-iri-geoname_not_number> a <http://api.knora.org/ontology/knora-api/v2#GeonameValue> .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    return g


@pytest.fixture
def violation_min_card() -> CardinalityValidationResult:
    return CardinalityValidationResult(
        source_constraint_component=SH.MinCountConstraintComponent,
        res_iri=DATA.id_min_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testGeoname,
        results_message="1-n",
    )


@pytest.fixture
def violation_max_card() -> CardinalityValidationResult:
    return CardinalityValidationResult(
        source_constraint_component=SH.MaxCountConstraintComponent,
        res_iri=DATA.id_max_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testDecimalSimpleText,
        results_message="0-1",
    )


@pytest.fixture
def violation_closed() -> CardinalityValidationResult:
    return CardinalityValidationResult(
        source_constraint_component=DASH.ClosedByTypesConstraintComponent,
        res_iri=DATA.id_closed_constraint,
        res_class=ONTO.CardOneResource,
        property=ONTO.testIntegerSimpleText,
        results_message="Property onto:testIntegerSimpleText is not among those permitted for any of the types",
    )


@pytest.fixture
def violation_value_type() -> ContentValidationResult:
    return ContentValidationResult(
        source_constraint_component=SH.NodeConstraintComponent,
        res_iri=DATA.id_2,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testColor,
        results_message="ColorValue",
        value_type=KNORA_API.TextValue,
        detail_bn_component=SH.ClassConstraintComponent,
        value=None,
    )


@pytest.fixture
def violation_unknown_content() -> ContentValidationResult:
    return ContentValidationResult(
        source_constraint_component=SH.UniqueLangConstraintComponent,
        res_iri=DATA.id,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testIntegerSimpleText,
        results_message="This is a constraint that is not checked in the data and should never appear.",
        detail_bn_component=SH.AndConstraintComponent,
        value=None,
    )


@pytest.fixture
def violation_regex() -> ContentValidationResult:
    return ContentValidationResult(
        source_constraint_component=SH.NodeConstraintComponent,
        res_iri=DATA.geoname_not_number,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testGeoname,
        results_message="The value must be a valid geoname code",
        value_type=KNORA_API.GeonameValue,
        detail_bn_component=SH.PatternConstraintComponent,
        value="this-is-not-a-valid-code",
    )
