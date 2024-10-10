import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.validation import ResourceValidationReportIdentifiers
from dsp_tools.commands.validate_data.models.validation import ResultWithDetail
from dsp_tools.commands.validate_data.models.validation import ResultWithoutDetail
from test.unittests.commands.validate_data.constants import DASH
from test.unittests.commands.validate_data.constants import DATA
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO
from test.unittests.commands.validate_data.constants import PREFIXES

MINIMAL_ONTO = """
        onto:CardOneResource
          a               owl:Class ;
          rdfs:subClassOf knora-api:Resource .
        
        onto:ClassInheritedCardinality
          a               owl:Class ;
          rdfs:subClassOf onto:CardOneResource .
        
        onto:ClassInheritedCardinalityOverwriting
          a               owl:Class ;
          rdfs:subClassOf onto:CardOneResource .
        
        onto:ClassMixedCard
          a               owl:Class ;
          rdfs:subClassOf knora-api:Resource .
        
        onto:ClassWithEverything
          a               owl:Class ;
          rdfs:subClassOf knora-api:Resource .
        
        onto:TestStillImageRepresentation
          a               owl:Class ;
          rdfs:subClassOf knora-api:StillImageRepresentation .
          
        knora-api:StillImageRepresentation
          a               owl:Class ;
          rdfs:subClassOf knora-api:Representation  .
        
        knora-api:Representation 
          a               owl:Class ;
          rdfs:subClassOf knora-api:Resource .
    """


@pytest.fixture
def result_id_card_one() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
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
    datastr = (
        f"""{PREFIXES}
    <http://data/id_card_one> a onto:ClassInheritedCardinalityOverwriting ;
        rdfs:label "Bool Card 1"^^xsd:string .
    """
        + MINIMAL_ONTO
    )
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(result.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/id_card_one"), ONTO.ClassInheritedCardinalityOverwriting
    )
    return result, data, identifiers


@pytest.fixture
def result_id_simpletext() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
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
    datastr = (
        f"""{PREFIXES}
    <http://data/id_simpletext> a onto:ClassWithEverything ;
        rdfs:label "Simpletext"^^xsd:string ;
        onto:testTextarea <http://data/value_id_simpletext> .

    <http://data/value_id_simpletext> a knora-api:TextValue ;
        knora-api:textValueAsXml "Text"^^xsd:string .
    """
        + MINIMAL_ONTO
    )
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(g.objects(predicate=SH.detail))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/id_simpletext"), ONTO.ClassWithEverything, detail_bn
    )
    return g, data, identifiers


@pytest.fixture
def result_id_uri() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
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
    datastr = (
        f"""{PREFIXES}
    <http://data/id_uri> a onto:ClassWithEverything ;
        rdfs:label "Uri"^^xsd:string ;
        onto:testUriValue <http://data/value_id_uri> .

    <http://data/value_id_uri> a knora-api:TextValue ;
        knora-api:valueAsString "https://dasch.swiss"^^xsd:string .
    """
        + MINIMAL_ONTO
    )
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(g.objects(predicate=SH.detail))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/id_uri"), ONTO.ClassWithEverything, detail_bn
    )
    return g, data, identifiers


@pytest.fixture
def result_geoname_not_number() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
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
    datastr = (
        f"""{PREFIXES}
    <http://data/geoname_not_number> a onto:ClassWithEverything ;
        rdfs:label "Geoname is not a number"^^xsd:string ;
        onto:testGeoname <http://data/value_geoname_not_number> .

    <http://data/value_geoname_not_number> a knora-api:GeonameValue ;
        knora-api:geonameValueAsGeonameCode "this-is-not-a-valid-code"^^xsd:string .
    """
        + MINIMAL_ONTO
    )
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(g.objects(predicate=SH.detail))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/geoname_not_number"), ONTO.ClassWithEverything, detail_bn
    )
    return g, data, identifiers


@pytest.fixture
def result_id_closed_constraint() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
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
    datastr = (
        f"""{PREFIXES}
    <http://data/id_closed_constraint> a onto:CardOneResource ;
        rdfs:label "Int card does not exist"^^xsd:string ;
        onto:testIntegerSimpleText <http://data/value_id_closed_constraint> .
    <http://data/value_id_closed_constraint> a knora-api:IntValue ;
        knora-api:intValueAsInt 1 .
    """
        + MINIMAL_ONTO
    )
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/id_closed_constraint"), ONTO.CardOneResource
    )
    return g, data, identifiers


@pytest.fixture
def result_id_max_card() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
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
    datastr = (
        f"""{PREFIXES}
    <http://data/id_max_card> a onto:ClassMixedCard ;
        rdfs:label "Decimal Card 0-1"^^xsd:string ;
        onto:testHasLinkToCardOneResource <http://data/value_1> , <http://data/value_2> .

    <http://data/value_1> a knora-api:LinkValue ;
        api-shapes:linkValueHasTargetID <http://data/id_card_one> .
    <http://data/value_2> a knora-api:LinkValue ;
        api-shapes:linkValueHasTargetID <http://data/id_closed_constraint> .
    """
        + MINIMAL_ONTO
    )
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(val_bn, URIRef("http://data/id_max_card"), ONTO.ClassMixedCard)
    return g, data, identifiers


@pytest.fixture
def result_empty_label() -> tuple[Graph, Graph, ResourceValidationReportIdentifiers]:
    gstr = f"""{PREFIXES}
    [ a sh:ValidationResult ;
            sh:focusNode <http://data/empty_label> ;
            sh:resultMessage "The label must be a non-empty string" ;
            sh:resultPath rdfs:label ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:PatternConstraintComponent ;
            sh:sourceShape api-shapes:rdfsLabel_Shape ;
            sh:value " " ] .
    """
    g = Graph()
    g.parse(data=gstr, format="ttl")
    datastr = (
        f"""{PREFIXES}
        <http://data/empty_label> a onto:ClassWithEverything ;
            rdfs:label " "^^xsd:string .
    """
        + MINIMAL_ONTO
    )
    data = Graph()
    data.parse(data=datastr, format="ttl")
    val_bn = next(g.subjects(RDF.type, SH.ValidationResult))
    identifiers = ResourceValidationReportIdentifiers(
        val_bn, URIRef("http://data/empty_label"), ONTO.ClassWithEverything
    )
    return g, data, identifiers


@pytest.fixture
def violation_empty_label() -> ResultWithoutDetail:
    return ResultWithoutDetail(
        source_constraint_component=SH.PatternConstraintComponent,
        res_iri=DATA.empty_label,
        res_class=ONTO.ClassWithEverything,
        property=RDFS.label,
        results_message="The label must be a non-empty string",
    )


@pytest.fixture
def violation_min_card() -> ResultWithoutDetail:
    return ResultWithoutDetail(
        source_constraint_component=SH.MinCountConstraintComponent,
        res_iri=DATA.id_min_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testGeoname,
        results_message="1-n",
    )


@pytest.fixture
def violation_max_card() -> ResultWithoutDetail:
    return ResultWithoutDetail(
        source_constraint_component=SH.MaxCountConstraintComponent,
        res_iri=DATA.id_max_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testDecimalSimpleText,
        results_message="0-1",
    )


@pytest.fixture
def violation_closed() -> ResultWithoutDetail:
    return ResultWithoutDetail(
        source_constraint_component=DASH.ClosedByTypesConstraintComponent,
        res_iri=DATA.id_closed_constraint,
        res_class=ONTO.CardOneResource,
        property=ONTO.testIntegerSimpleText,
        results_message="Property onto:testIntegerSimpleText is not among those permitted for any of the types",
    )


@pytest.fixture
def violation_value_type() -> ResultWithDetail:
    return ResultWithDetail(
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
def violation_unknown_content() -> ResultWithDetail:
    return ResultWithDetail(
        source_constraint_component=SH.UniqueLangConstraintComponent,
        res_iri=DATA.id,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testIntegerSimpleText,
        results_message="This is a constraint that is not checked in the data and should never appear.",
        detail_bn_component=SH.AndConstraintComponent,
        value=None,
    )


@pytest.fixture
def violation_regex() -> ResultWithDetail:
    return ResultWithDetail(
        source_constraint_component=SH.NodeConstraintComponent,
        res_iri=DATA.geoname_not_number,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testGeoname,
        results_message="The value must be a valid geoname code",
        value_type=KNORA_API.GeonameValue,
        detail_bn_component=SH.PatternConstraintComponent,
        value="this-is-not-a-valid-code",
    )
