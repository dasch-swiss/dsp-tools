from functools import lru_cache

import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import Literal

from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import ResultGenericViolation
from dsp_tools.commands.validate_data.models.validation import ResultLinkTargetViolation
from dsp_tools.commands.validate_data.models.validation import ResultMaxCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultMinCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultNonExistentCardinalityViolation
from dsp_tools.commands.validate_data.models.validation import ResultPatternViolation
from dsp_tools.commands.validate_data.models.validation import ResultUniqueValueViolation
from dsp_tools.commands.validate_data.models.validation import ResultValueTypeViolation
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from test.unittests.commands.validate_data.constants import DASH
from test.unittests.commands.validate_data.constants import DATA
from test.unittests.commands.validate_data.constants import KNORA_API
from test.unittests.commands.validate_data.constants import ONTO
from test.unittests.commands.validate_data.constants import PREFIXES


@lru_cache(maxsize=None)
@pytest.fixture
def onto_graph() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/onto.ttl")
    return g


@pytest.fixture
def report_not_resource(onto_graph: Graph) -> tuple[Graph, Graph]:
    validation_str = f"""{PREFIXES}
    _:bn_id_simpletext a sh:ValidationResult ;
        sh:focusNode <http://data/value_id_simpletext> ;
        sh:resultMessage "TextValue without formatting" ;
        sh:resultPath knora-api:valueAsString ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
        sh:sourceShape api-shapes:SimpleTextValue_PropShape .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/id_simpletext> a onto:ClassWithEverything ;
        rdfs:label "Simpletext"^^xsd:string ;
        onto:testTextarea <http://data/value_id_simpletext> .
    <http://data/value_id_simpletext> a knora-api:TextValue ;
        knora-api:textValueAsXml "Text"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    return validation_g, onto_data_g


@pytest.fixture
def report_min_card(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/id_card_one> ;
        sh:resultMessage "1" ;
        sh:resultPath onto:testBoolean ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
        sh:sourceShape [ ] ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/id_card_one> a onto:ClassInheritedCardinalityOverwriting ;
        rdfs:label "Bool Card 1"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.MinCountConstraintComponent,
        resource_iri=DATA.id_card_one,
        res_class_type=ONTO.ClassInheritedCardinalityOverwriting,
        result_path=ONTO.testBoolean,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_min_card() -> ResultMinCardinalityViolation:
    return ResultMinCardinalityViolation(
        res_iri=DATA.id_card_one,
        res_class=ONTO.ClassInheritedCardinalityOverwriting,
        property=ONTO.testBoolean,
        results_message="1",
    )


@pytest.fixture
def report_value_type_simpletext(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:detail _:bn_id_simpletext ;
        sh:focusNode <http://data/id_simpletext> ;
        sh:resultMessage "Value does not have shape <http://api.knora.org/ontology/knora-api/shapes/v2#SimpleTextValue_ClassShape>" ;
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
    """  # noqa: E501 (Line too long)
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/id_simpletext> a onto:ClassWithEverything ;
        rdfs:label "Simpletext"^^xsd:string ;
        onto:testTextarea <http://data/value_id_simpletext> .

    <http://data/value_id_simpletext> a knora-api:TextValue ;
        knora-api:textValueAsXml "Text"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(validation_g.objects(val_bn, SH.detail))
    detail = DetailBaseInfo(
        detail_bn=detail_bn,
        source_constraint_component=SH.MinCountConstraintComponent,
    )
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        result_path=ONTO.testTextarea,
        source_constraint_component=SH.NodeConstraintComponent,
        resource_iri=DATA.id_simpletext,
        res_class_type=ONTO.ClassWithEverything,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_value_type_simpletext() -> ResultValueTypeViolation:
    return ResultValueTypeViolation(
        res_iri=DATA.id_simpletext,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testTextarea,
        results_message="TextValue without formatting",
        actual_value_type=KNORA_API.TextValue,
    )


@pytest.fixture
def report_value_type(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:detail _:bn_id_uri ;
        sh:focusNode <http://data/id_uri> ;
        sh:resultMessage "Value does not have shape <http://api.knora.org/ontology/knora-api/shapes/v2#UriValue_ClassShape>" ;
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
    """  # noqa: E501 (Line too long)
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/id_uri> a onto:ClassWithEverything ;
        rdfs:label "Uri"^^xsd:string ;
        onto:testUriValue <http://data/value_id_uri> .

    <http://data/value_id_uri> a knora-api:TextValue ;
        knora-api:valueAsString "https://dasch.swiss"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(validation_g.objects(predicate=SH.detail))
    detail_component = next(validation_g.objects(detail_bn, SH.sourceConstraintComponent))
    detail = DetailBaseInfo(
        detail_bn=detail_bn,
        source_constraint_component=detail_component,
    )
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.NodeConstraintComponent,
        resource_iri=DATA.id_uri,
        res_class_type=ONTO.ClassWithEverything,
        result_path=ONTO.testUriValue,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_value_type() -> ResultValueTypeViolation:
    return ResultValueTypeViolation(
        res_iri=DATA.id_uri,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testUriValue,
        results_message="UriValue",
        actual_value_type=KNORA_API.TextValue,
    )


@pytest.fixture
def report_regex(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:detail _:bn_geoname_not_number ;
        sh:focusNode <http://data/geoname_not_number> ;
        sh:resultMessage "Value does not have shape <http://api.knora.org/ontology/knora-api/shapes/v2#GeonameValue_ClassShape>" ;
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
    """  # noqa: E501 (Line too long)
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/geoname_not_number> a onto:ClassWithEverything ;
        rdfs:label "Geoname is not a number"^^xsd:string ;
        onto:testGeoname <http://data/value_geoname_not_number> .

    <http://data/value_geoname_not_number> a knora-api:GeonameValue ;
        knora-api:geonameValueAsGeonameCode "this-is-not-a-valid-code"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(validation_g.objects(val_bn, SH.detail))
    detail_component = next(validation_g.objects(detail_bn, SH.sourceConstraintComponent))
    detail = DetailBaseInfo(
        detail_bn=detail_bn,
        source_constraint_component=detail_component,
    )
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.NodeConstraintComponent,
        resource_iri=DATA.geoname_not_number,
        res_class_type=ONTO.ClassWithEverything,
        result_path=ONTO.testGeoname,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_regex() -> ResultPatternViolation:
    return ResultPatternViolation(
        res_iri=DATA.geoname_not_number,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testGeoname,
        results_message="The value must be a valid geoname code",
        actual_value="this-is-not-a-valid-code",
    )


@pytest.fixture
def report_link_target_non_existent(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:detail _:bn_link_target_non_existent ;
        sh:focusNode <http://data/link_target_non_existent> ;
        sh:resultMessage "Value does not have shape <http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo_NodeShape>" ;
        sh:resultPath onto:testHasLinkTo ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:NodeConstraintComponent ;
        sh:sourceShape onto:testHasLinkTo_PropShape ;
        sh:value <http://data/value_link_target_non_existent> ] .
    
    _:bn_link_target_non_existent a sh:ValidationResult ;
        sh:focusNode <http://data/value_link_target_non_existent> ;
        sh:resultMessage <http://api.knora.org/ontology/knora-api/v2#Resource> ;
        sh:resultPath api-shapes:linkValueHasTargetID ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:ClassConstraintComponent ;
        sh:sourceShape [ ] ;
        sh:value <http://data/other> .
    """  # noqa: E501 (Line too long)
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/link_target_non_existent> a onto:ClassWithEverything ;
        rdfs:label "Target does not exist"^^xsd:string ;
        onto:testHasLinkTo <http://data/value_link_target_non_existent> .
    
    <http://data/value_link_target_non_existent> a knora-api:LinkValue ;
    api-shapes:linkValueHasTargetID <http://data/other> .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(validation_g.objects(val_bn, SH.detail))
    detail_component = next(validation_g.objects(detail_bn, SH.sourceConstraintComponent))
    detail = DetailBaseInfo(
        detail_bn=detail_bn,
        source_constraint_component=detail_component,
    )
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.NodeConstraintComponent,
        resource_iri=DATA.link_target_non_existent,
        res_class_type=ONTO.ClassWithEverything,
        result_path=ONTO.testHasLinkTo,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_link_target_non_existent() -> ResultLinkTargetViolation:
    return ResultLinkTargetViolation(
        res_iri=DATA.link_target_non_existent,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testHasLinkTo,
        expected_type=KNORA_API.Resource,
        target_iri=DATA.other,
        target_resource_type=None,
    )


@pytest.fixture
def report_link_target_wrong_class(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:detail _:bn_link_target_wrong_class ;
        sh:focusNode <http://data/link_target_wrong_class> ;
        sh:resultMessage "Value does not have shape <http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkToCardOneResource_NodeShape>" ;
        sh:resultPath onto:testHasLinkToCardOneResource ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:NodeConstraintComponent ;
        sh:sourceShape onto:testHasLinkToCardOneResource_PropShape ;
        sh:value <http://data/value_link_target_wrong_class> ] .
        
    _:bn_link_target_wrong_class a sh:ValidationResult ;
        sh:focusNode <http://data/value_link_target_wrong_class> ;
        sh:resultMessage <http://0.0.0.0:3333/ontology/9999/onto/v2#CardOneResource> ;
        sh:resultPath api-shapes:linkValueHasTargetID ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:ClassConstraintComponent ;
        sh:sourceShape [ ] ;
        sh:value <http://data/id_9_target> .
    """  # noqa: E501 (Line too long)
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/link_target_wrong_class> a onto:ClassWithEverything ;
        rdfs:label "Target not the right class"^^xsd:string ;
        onto:testHasLinkToCardOneResource <http://data/value_link_target_wrong_class> .
    
    <http://data/id_9_target> a onto:ClassWithEverything ;
        rdfs:label "Link Prop"^^xsd:string .

    <http://data/value_link_target_wrong_class> a knora-api:LinkValue ;
        api-shapes:linkValueHasTargetID <http://data/id_9_target> .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(validation_g.objects(val_bn, SH.detail))
    detail_component = next(validation_g.objects(detail_bn, SH.sourceConstraintComponent))
    detail = DetailBaseInfo(
        detail_bn=detail_bn,
        source_constraint_component=detail_component,
    )
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.NodeConstraintComponent,
        resource_iri=DATA.link_target_wrong_class,
        res_class_type=ONTO.ClassWithEverything,
        result_path=ONTO.testHasLinkToCardOneResource,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_link_target_wrong_class() -> ResultLinkTargetViolation:
    return ResultLinkTargetViolation(
        res_iri=DATA.link_target_wrong_class,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testHasLinkToCardOneResource,
        expected_type=ONTO.CardOneResource,
        target_iri=DATA.id_9_target,
        target_resource_type=ONTO.ClassWithEverything,
    )


@pytest.fixture
def report_closed_constraint(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/id_closed_constraint> ;
        sh:resultMessage "Property onto:testIntegerSimpleText is not among those permitted for any of the types" ;
        sh:resultPath onto:testIntegerSimpleText ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent dash:ClosedByTypesConstraintComponent ;
        sh:sourceShape onto:CardOneResource ;
        sh:value <http://data/value_id_closed_constraint> ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/id_closed_constraint> a onto:CardOneResource ;
        rdfs:label "Int card does not exist"^^xsd:string ;
        onto:testIntegerSimpleText <http://data/value_id_closed_constraint> .
    <http://data/value_id_closed_constraint> a knora-api:IntValue ;
        knora-api:intValueAsInt 1 .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=DASH.ClosedByTypesConstraintComponent,
        resource_iri=DATA.id_closed_constraint,
        res_class_type=ONTO.CardOneResource,
        result_path=ONTO.testIntegerSimpleText,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_closed_constraint() -> ResultNonExistentCardinalityViolation:
    return ResultNonExistentCardinalityViolation(
        res_iri=DATA.id_closed_constraint,
        res_class=ONTO.CardOneResource,
        property=ONTO.testIntegerSimpleText,
    )


@pytest.fixture
def report_max_card(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/id_max_card> ;
        sh:resultMessage "1" ;
        sh:resultPath onto:testHasLinkToCardOneResource ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:MaxCountConstraintComponent ;
        sh:sourceShape [ ] ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/id_max_card> a onto:ClassMixedCard ;
        rdfs:label "Decimal Card 0-1"^^xsd:string ;
        onto:testHasLinkToCardOneResource <http://data/value_1> , <http://data/value_2> .

    <http://data/value_1> a knora-api:LinkValue ;
        api-shapes:linkValueHasTargetID <http://data/id_card_one> .
    <http://data/value_2> a knora-api:LinkValue ;
        api-shapes:linkValueHasTargetID <http://data/id_closed_constraint> .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.MaxCountConstraintComponent,
        resource_iri=DATA.id_max_card,
        res_class_type=ONTO.ClassMixedCard,
        result_path=ONTO.testHasLinkToCardOneResource,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_max_card() -> ResultMaxCardinalityViolation:
    return ResultMaxCardinalityViolation(
        res_iri=DATA.id_max_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testDecimalSimpleText,
        results_message="0-1",
    )


@pytest.fixture
def report_empty_label(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/empty_label> ;
        sh:resultMessage "The label must be a non-empty string" ;
        sh:resultPath rdfs:label ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:PatternConstraintComponent ;
        sh:sourceShape api-shapes:rdfsLabel_Shape ;
        sh:value " " ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
        <http://data/empty_label> a onto:ClassWithEverything ;
            rdfs:label " "^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.PatternConstraintComponent,
        resource_iri=DATA.empty_label,
        res_class_type=ONTO.ClassWithEverything,
        result_path=RDFS.label,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_empty_label() -> ResultPatternViolation:
    return ResultPatternViolation(
        res_iri=DATA.empty_label,
        res_class=ONTO.ClassWithEverything,
        property=RDFS.label,
        results_message="The label must be a non-empty string",
        actual_value=" ",
    )


@pytest.fixture
def report_unique_value_literal(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/identical_values_valueHas> ;
        sh:resultMessage "A resource may not have the same property and value more than one time." ;
        sh:resultPath onto:testGeoname ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraint _:1 ;
        sh:sourceConstraintComponent sh:SPARQLConstraintComponent ;
        sh:sourceShape onto:ClassWithEverything_Unique ;
        sh:value "00111111" ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
        <http://data/identical_values_valueHas> a onto:ClassWithEverything .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.SPARQLConstraintComponent,
        resource_iri=DATA.identical_values_valueHas,
        res_class_type=ONTO.ClassWithEverything,
        result_path=ONTO.testGeoname,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_unique_value_literal() -> ResultUniqueValueViolation:
    return ResultUniqueValueViolation(
        res_iri=DATA.identical_values_valueHas,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testGeoname,
        actual_value=Literal("00111111"),
    )


@pytest.fixture
def report_unique_value_iri(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/identical_values_LinkValue> ;
        sh:resultMessage "A resource may not have the same property and value more than one time." ;
        sh:resultPath onto:testHasLinkTo ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraint _:1 ;
        sh:sourceConstraintComponent sh:SPARQLConstraintComponent ;
        sh:sourceShape onto:ClassWithEverything_Unique ;
        sh:value <http://data/link_valueTarget_id> ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
        <http://data/identical_values_LinkValue> a onto:ClassWithEverything .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.SPARQLConstraintComponent,
        resource_iri=DATA.identical_values_LinkValue,
        res_class_type=ONTO.ClassWithEverything,
        result_path=ONTO.testHasLinkTo,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_unique_value_iri() -> ResultUniqueValueViolation:
    return ResultUniqueValueViolation(
        res_iri=DATA.identical_values_LinkValue,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testHasLinkTo,
        actual_value=DATA.link_valueTarget_id,
    )


@pytest.fixture
def report_unknown_list_node(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ 
    a sh:ValidationResult ;
sh:detail _:bn_list_node_non_existent ;
sh:focusNode <http://data/list_node_non_existent> ;
sh:resultMessage "Value does not have shape <http://api.knora.org/ontology/knora-api/shapes/v2#firstList_NodeShape>" ;
sh:resultPath onto:testListProp ;
sh:resultSeverity sh:Violation ;
sh:sourceConstraintComponent sh:NodeConstraintComponent ;
sh:sourceShape onto:testListProp_PropShape ;
sh:value <http://data/value_list_node_non_existent> ] .
    
    _:bn_list_node_non_existent a sh:ValidationResult ;
    sh:focusNode <http://data/value_list_node_non_existent> ;
    sh:resultMessage "Unknown list node for list 'firstList'." ;
    sh:resultPath api-shapes:listNodeAsString ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:InConstraintComponent ;
    sh:sourceShape [ ] ;
    sh:value "other" .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/list_node_non_existent> a onto:ClassWithEverything .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(validation_g.objects(val_bn, SH.detail))
    detail = DetailBaseInfo(
        detail_bn=detail_bn,
        source_constraint_component=SH.InConstraintComponent,
    )
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.NodeConstraintComponent,
        resource_iri=DATA.list_node_non_existent,
        res_class_type=ONTO.ClassWithEverything,
        result_path=ONTO.testListProp,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_unknown_list_node() -> ResultGenericViolation:
    return ResultGenericViolation(
        res_iri=DATA.list_node_non_existent,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testListProp,
        results_message="Unknown list node for list 'firstList'.",
        actual_value="other",
    )


@pytest.fixture
def report_unknown_list_name(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
[ a sh:ValidationResult ;
sh:detail _:bn_list_name_non_existent ;
sh:focusNode <http://data/list_name_non_existent> ;
sh:resultMessage "Value does not have shape <http://api.knora.org/ontology/knora-api/shapes/v2#firstList_NodeShape>" ;
sh:resultPath onto:testListProp ;
sh:resultSeverity sh:Violation ;
sh:sourceConstraintComponent sh:NodeConstraintComponent ;
sh:sourceShape onto:testListProp_PropShape ;
sh:value <http://data/value_list_name_non_existent> ] .

_:bn_list_name_non_existent a sh:ValidationResult ;
    sh:focusNode <http://data/value_list_name_non_existent> ;
    sh:resultMessage "The list that should be used with this property is 'firstList'." ;
    sh:resultPath api-shapes:listNameAsString ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:InConstraintComponent ;
    sh:sourceShape _:bn_source ;
    sh:value "other" .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/list_name_non_existent> a onto:ClassWithEverything .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(validation_g.objects(val_bn, SH.detail))
    detail = DetailBaseInfo(
        detail_bn=detail_bn,
        source_constraint_component=SH.InConstraintComponent,
    )
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.NodeConstraintComponent,
        resource_iri=DATA.list_name_non_existent,
        res_class_type=ONTO.ClassWithEverything,
        result_path=ONTO.testListProp,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_unknown_list_name() -> ResultGenericViolation:
    return ResultGenericViolation(
        res_iri=DATA.list_name_non_existent,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testListProp,
        results_message="The list that should be used with this property is 'firstList'.",
        actual_value="other",
    )


@pytest.fixture
def report_missing_file_value(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
            sh:focusNode <http://data/id_video_missing> ;
            sh:resultMessage "A MovingImageRepresentation requires a file with the extension 'mp4'." ;
            sh:resultPath <http://api.knora.org/ontology/knora-api/v2#hasMovingImageFileValue> ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
            sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#hasMovingImageFileValue_PropShape> 
    ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/id_video_missing> a <http://0.0.0.0:3333/ontology/9999/onto/v2#TestMovingImageRepresentation> ;
        rdfs:label "TestMovingImageRepresentation"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.MinCountConstraintComponent,
        resource_iri=DATA.id_video_missing,
        res_class_type=ONTO.TestMovingImageRepresentation,
        result_path=KNORA_API.hasMovingImageFileValue,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_missing_file_value() -> ResultMinCardinalityViolation:
    return ResultMinCardinalityViolation(
        res_iri=DATA.id_video_missing,
        res_class=ONTO.TestMovingImageRepresentation,
        property=KNORA_API.hasMovingImageFileValue,
        results_message="A MovingImageRepresentation requires a file with the extension 'mp4'.",
    )


@pytest.fixture
def result_unknown_component(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/empty_label> ;
        sh:resultMessage "The label must be a non-empty string" ;
        sh:resultPath rdfs:label ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:UniqueLangConstraintComponent ;
        sh:sourceShape api-shapes:rdfsLabel_Shape ;
        sh:value " " ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
        <http://data/empty_label> a onto:ClassWithEverything ;
            rdfs:label " "^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.PatternConstraintComponent,
        resource_iri=DATA.empty_label,
        res_class_type=ONTO.ClassWithEverything,
        result_path=RDFS.label,
    )
    return validation_g, onto_data_g, base_info
