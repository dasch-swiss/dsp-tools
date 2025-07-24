import pytest
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import Graph
from rdflib import Literal

from dsp_tools.commands.validate_data.models.validation import DetailBaseInfo
from dsp_tools.commands.validate_data.models.validation import ValidationResult
from dsp_tools.commands.validate_data.models.validation import ValidationResultBaseInfo
from dsp_tools.commands.validate_data.models.validation import ViolationType
from dsp_tools.utils.rdflib_constants import DASH
from dsp_tools.utils.rdflib_constants import DATA
from dsp_tools.utils.rdflib_constants import KNORA_API
from test.unittests.commands.validate_data.constants import IN_BUILT_ONTO
from test.unittests.commands.validate_data.constants import ONTO
from test.unittests.commands.validate_data.constants import PREFIXES


@pytest.fixture(scope="module")
def onto_graph() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/onto.ttl")
    g.parse("testdata/validate-data/knora-api-subset.ttl")
    return g


@pytest.fixture
def report_target_resource_wrong_type(onto_graph: Graph) -> tuple[Graph, Graph]:
    validation_str = f"""{PREFIXES}
    [ 
        a sh:ValidationResult ;
        sh:detail _:detail_bn ;
        sh:focusNode <http://data/region_isRegionOf_resource_not_a_representation> ;
        sh:resultMessage "Value does not have shape api-shapes:isRegionOf_NodeShape" ;
        sh:resultPath <http://api.knora.org/ontology/knora-api/v2#isRegionOf> ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:NodeConstraintComponent ;
        sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#isRegionOf_PropertyShape> ;
        sh:value <http://data/value_isRegionOf> 
    ] .
    
    _:detail_bn a sh:ValidationResult ;
        sh:focusNode <http://data/value_isRegionOf> ;
        sh:resultMessage "http://api.knora.org/ontology/knora-api/v2#Representation" ;
        sh:resultPath <http://api.knora.org/ontology/knora-api/shapes/v2#linkValueHasTargetID> ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:ClassConstraintComponent ;
        sh:sourceShape _:source_shape ;
        sh:value <http://data/target_res_without_representation_1> .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/region_isRegionOf_resource_not_a_representation> 
        a knora-api:Region ;
        rdfs:label "Region"^^xsd:string ;
        knora-api:hasColor <http://data/value_hasColor> ;
        knora-api:hasGeometry <http://data/value_hasGeometry> ;
        knora-api:isRegionOf <http://data/value_isRegionOf> .
    
    <http://data/value_isRegionOf> a knora-api:LinkValue ;
        api-shapes:linkValueHasTargetID <http://data/target_res_without_representation_1> .
    
    <http://data/target_res_without_representation_1> a in-built:TestNormalResource ;
        rdfs:label "Resource without Representation"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    return validation_g, onto_data_g


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
        focus_node_iri=DATA.id_card_one,
        focus_node_type=ONTO.ClassInheritedCardinalityOverwriting,
        result_path=ONTO.testBoolean,
        severity=SH.Violation,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def report_file_closed_constraint(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
[   a sh:ValidationResult ;
    sh:focusNode <http://data/id_wrong_file_type> ;
    sh:resultMessage "Property knora-api:hasMovingImageFileValue is not among those permitted for any of the types" ;
    sh:resultPath <http://api.knora.org/ontology/knora-api/v2#hasMovingImageFileValue> ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent <http://datashapes.org/dash#ClosedByTypesConstraintComponent> ;
    sh:sourceShape <http://0.0.0.0:3333/ontology/9999/onto/v2#TestStillImageRepresentation> ;
    sh:value <http://data/fileValueBn> ] .
    """
    data_str = f"""{PREFIXES}
    <http://data/id_wrong_file_type> a onto:TestStillImageRepresentation ;
        rdfs:label "TestStillImageRepresentation File mp4"^^xsd:string ;
        knora-api:hasMovingImageFileValue <http://data/fileValueBn> .
        
    <http://data/fileValueBn> a knora-api:MovingImageFileValue ;
        knora-api:fileValueHasFilename "file.mp4"^^xsd:string .
    """
    result_g = Graph()
    result_g.parse(data=validation_str, format="ttl")
    data_g = Graph()
    data_g.parse(data=data_str, format="ttl")
    result_g += onto_graph
    val_bn = next(result_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=DASH.ClosedByTypesConstraintComponent,
        focus_node_iri=DATA.id_wrong_file_type,
        focus_node_type=ONTO.TestStillImageRepresentation,
        result_path=KNORA_API.hasMovingImageFileValue,
        severity=SH.Violation,
    )
    return result_g, data_g, base_info


@pytest.fixture
def file_value_for_resource_without_representation(onto_graph: Graph) -> tuple[Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
[ a sh:ValidationResult ;
    sh:focusNode <http://data/id_resource_without_representation> ;
    sh:resultMessage "Property knora-api:hasMovingImageFileValue is not among those permitted for any of the types" ;
    sh:resultPath <http://api.knora.org/ontology/knora-api/v2#hasMovingImageFileValue> ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent <http://datashapes.org/dash#ClosedByTypesConstraintComponent> ;
    sh:sourceShape <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything> ;
    sh:value <http://data/fileBn> ] .
    """
    data_str = f"""{PREFIXES}
    <http://data/id_resource_without_representation> a <http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything> ;
        rdfs:label "Resource Without Representation"^^xsd:string ;
        knora-api:hasMovingImageFileValue <http://data/fileBn> .
    """
    graphs = Graph()
    graphs.parse(data=validation_str, format="ttl")
    graphs.parse(data=data_str, format="ttl")
    graphs += onto_graph
    val_bn = next(graphs.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=DASH.ClosedByTypesConstraintComponent,
        focus_node_iri=DATA.id_resource_without_representation,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=KNORA_API.hasMovingImageFileValue,
        severity=SH.Violation,
    )
    return graphs, base_info


@pytest.fixture
def extracted_file_value_for_resource_without_representation() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.FILE_VALUE_PROHIBITED,
        res_iri=DATA.id_resource_without_representation,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.hasMovingImageFileValue,
        severity=SH.Violation,
    )


@pytest.fixture
def extracted_min_card() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.MIN_CARD,
        res_iri=DATA.id_card_one,
        res_class=ONTO.ClassInheritedCardinalityOverwriting,
        property=ONTO.testBoolean,
        expected=Literal("1"),
        severity=SH.Violation,
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
        focus_node_iri=DATA.id_simpletext,
        focus_node_type=ONTO.ClassWithEverything,
        severity=SH.Violation,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_value_type_simpletext() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.VALUE_TYPE,
        res_iri=DATA.id_simpletext,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testTextarea,
        expected=Literal("TextValue without formatting"),
        input_type=KNORA_API.TextValue,
        severity=SH.Violation,
    )


@pytest.fixture
def report_min_inclusive(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/value_iri> ;
        sh:resultMessage "The interval start must be a non-negative integer or decimal." ;
        sh:resultPath <http://api.knora.org/ontology/knora-api/v2#intervalValueHasStart> ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:MinInclusiveConstraintComponent ;
        sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#intervalValueHasStart_PropShape> ;
        sh:value -2.0 ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}

    <http://data/video_segment_negative_bounds> a knora-api:VideoSegment ;
        rdfs:label "Video Segment"^^xsd:string ;
        knora-api:hasSegmentBounds <http://data/value_iri> .
    
    <http://data/value_iri> a knora-api:IntervalValue ;
        knora-api:intervalValueHasEnd -1.0 ;
        knora-api:intervalValueHasStart -2.0 .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        result_path=KNORA_API.hasSegmentBounds,
        source_constraint_component=SH.NodeConstraintComponent,
        focus_node_iri=DATA.video_segment_negative_bounds,
        focus_node_type=KNORA_API.VideoSegment,
        severity=SH.Violation,
        detail=None,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_min_inclusive() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.GENERIC,
        res_iri=DATA.video_segment_negative_bounds,
        res_class=KNORA_API.VideoSegment,
        property=KNORA_API.hasSegmentBounds,
        message=Literal("The interval start must be a non-negative integer or decimal."),
        input_value=Literal("-2.0"),
        severity=SH.Violation,
    )


@pytest.fixture
def report_value_type(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/id_uri> ;
        sh:resultMessage "This property requires a UriValue" ;
        sh:resultPath <http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue> ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:ClassConstraintComponent ;
        sh:sourceShape [ ] ;
        sh:value <http://data/value_id_uri> ] .
    """
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
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.ClassConstraintComponent,
        focus_node_iri=DATA.id_uri,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testUriValue,
        severity=SH.Violation,
        detail=None,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_value_type() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.VALUE_TYPE,
        res_iri=DATA.id_uri,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testUriValue,
        expected=Literal("This property requires a UriValue"),
        input_type=KNORA_API.TextValue,
        severity=SH.Violation,
    )


@pytest.fixture
def report_regex(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/value_geoname_not_number> ;
        sh:resultMessage "The value must be a valid geoname code" ;
        sh:resultPath <http://api.knora.org/ontology/knora-api/v2#geonameValueAsGeonameCode> ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:PatternConstraintComponent ;
        sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#geonameValueAsGeonameCode_Shape> ;
        sh:value "this-is-not-a-valid-code" ].
    """
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
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.NodeConstraintComponent,
        focus_node_iri=DATA.geoname_not_number,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testGeoname,
        severity=SH.Violation,
        detail=None,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_regex() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.PATTERN,
        res_iri=DATA.geoname_not_number,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testGeoname,
        expected=Literal("The value must be a valid geoname code"),
        input_value=Literal("this-is-not-a-valid-code"),
        severity=SH.Violation,
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
        focus_node_iri=DATA.link_target_non_existent,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testHasLinkTo,
        severity=SH.Violation,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_link_target_non_existent() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.LINK_TARGET,
        res_iri=DATA.link_target_non_existent,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testHasLinkTo,
        expected=KNORA_API.Resource,
        input_value=DATA.other,
        severity=SH.Violation,
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
        focus_node_iri=DATA.link_target_wrong_class,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testHasLinkToCardOneResource,
        severity=SH.Violation,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_link_target_wrong_class() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.LINK_TARGET,
        res_iri=DATA.link_target_wrong_class,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testHasLinkToCardOneResource,
        expected=ONTO.CardOneResource,
        input_value=DATA.id_9_target,
        input_type=ONTO.ClassWithEverything,
        severity=SH.Violation,
    )


@pytest.fixture
def report_image_missing_legal_info(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/value_image_no_legal_info> ;
        sh:resultMessage "Files and IIIF-URIs require a reference to a license." ;
        sh:resultPath <http://api.knora.org/ontology/knora-api/v2#hasLicense> ;
        sh:resultSeverity sh:Warning ;
        sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
        sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#hasLicense_PropShape> ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/image_no_legal_info> a <http://0.0.0.0:3333/ontology/9999/onto/v2#TestStillImageRepresentation> ;
    rdfs:label "TestStillImageRepresentation Bitstream"^^xsd:string ;
    knora-api:hasStillImageFileValue <http://data/value_image_no_legal_info> .

    <http://data/value_image_no_legal_info> a knora-api:StillImageFileValue ;
        knora-api:fileValueHasFilename "this/is/filepath/file.jp2"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.MinCountConstraintComponent,
        focus_node_iri=DATA.image_no_legal_info,
        focus_node_type=ONTO.TestStillImageRepresentation,
        result_path=KNORA_API.hasLicense,
        severity=SH.Warning,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_image_missing_legal_info() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.GENERIC,
        res_iri=DATA.image_no_legal_info,
        res_class=ONTO.TestStillImageRepresentation,
        severity=SH.Warning,
        property=KNORA_API.hasLicense,
        expected=Literal("Files and IIIF-URIs require a reference to a license."),
    )


@pytest.fixture
def report_archive_missing_legal_info(onto_graph: Graph) -> tuple[Graph, Graph]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/value_bitstream_no_legal_info> ;
        sh:resultMessage "Files and IIIF-URIs require a reference to a license." ;
        sh:resultPath <http://api.knora.org/ontology/knora-api/v2#hasLicense> ;
        sh:resultSeverity sh:Warning ;
        sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
        sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#hasLicense_PropShape> ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/bitstream_no_legal_info> a <http://0.0.0.0:3333/ontology/9999/onto/v2#TestArchiveRepresentation> ;
        rdfs:label "TestArchiveRepresentation tar"^^xsd:string ;
        knora-api:hasArchiveFileValue <http://data/value_bitstream_no_legal_info> .
    
    <http://data/value_bitstream_no_legal_info> a knora-api:ArchiveFileValue ;
        knora-api:fileValueHasFilename "this/is/filepath/file.tar"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    return validation_g, onto_data_g


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
        focus_node_iri=DATA.id_closed_constraint,
        focus_node_type=ONTO.CardOneResource,
        result_path=ONTO.testIntegerSimpleText,
        severity=SH.Violation,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_closed_constraint() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.NON_EXISTING_CARD,
        res_iri=DATA.id_closed_constraint,
        res_class=ONTO.CardOneResource,
        property=ONTO.testIntegerSimpleText,
        severity=SH.Violation,
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
        focus_node_iri=DATA.id_max_card,
        focus_node_type=ONTO.ClassMixedCard,
        result_path=ONTO.testHasLinkToCardOneResource,
        severity=SH.Violation,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_max_card() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.MAX_CARD,
        res_iri=DATA.id_max_card,
        res_class=ONTO.ClassMixedCard,
        property=ONTO.testDecimalSimpleText,
        expected=Literal("0-1"),
        severity=SH.Violation,
    )


@pytest.fixture
def report_empty_label(onto_graph: Graph) -> tuple[Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/empty_label> ;
        sh:resultMessage "The label must be a non-empty string" ;
        sh:resultPath rdfs:label ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent sh:PatternConstraintComponent ;
        sh:sourceShape [ ] ;
        sh:value " " ] .
    """
    data_str = f"""{PREFIXES}
        <http://data/empty_label> a onto:ClassWithEverything ;
            rdfs:label " "^^xsd:string .
    """
    graphs = Graph()
    graphs.parse(data=validation_str, format="ttl")
    graphs.parse(data=data_str, format="ttl")
    graphs += onto_graph
    val_bn = next(graphs.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.PatternConstraintComponent,
        focus_node_iri=DATA.empty_label,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=RDFS.label,
        severity=SH.Violation,
    )
    return graphs, base_info


@pytest.fixture
def extracted_empty_label() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.PATTERN,
        res_iri=DATA.empty_label,
        res_class=ONTO.ClassWithEverything,
        property=RDFS.label,
        expected=Literal("The label must be a non-empty string"),
        input_value=Literal(" "),
        severity=SH.Violation,
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
        focus_node_iri=DATA.identical_values_valueHas,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testGeoname,
        severity=SH.Violation,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_unique_value_literal() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.UNIQUE_VALUE,
        res_iri=DATA.identical_values_valueHas,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testGeoname,
        input_value=Literal("00111111"),
        severity=SH.Violation,
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
        focus_node_iri=DATA.identical_values_LinkValue,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testHasLinkTo,
        severity=SH.Violation,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_unique_value_iri() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.UNIQUE_VALUE,
        res_iri=DATA.identical_values_LinkValue,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testHasLinkTo,
        input_value=DATA.link_valueTarget_id,
        severity=SH.Violation,
    )


@pytest.fixture
def report_coexist_with(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
        sh:focusNode <http://data/missing_seqnum> ;
        sh:resultMessage "The property seqnum must be used together with isPartOf" ;
        sh:resultPath <http://api.knora.org/ontology/knora-api/v2#seqnum> ;
        sh:resultSeverity sh:Violation ;
        sh:sourceConstraintComponent <http://datashapes.org/dash#CoExistsWithConstraintComponent> ;
        sh:sourceShape <http://api.knora.org/ontology/knora-api/shapes/v2#seqnum_PropShape> ] .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/missing_seqnum> a in-built:TestStillImageRepresentationWithSeqnum ;
        rdfs:label "Image with sequence"^^xsd:string ;
        knora-api:hasStillImageFileValue <http://data/file_value> ;
        knora-api:isPartOf <http://data/is_part_of_value> .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=DASH.CoExistsWithConstraintComponent,
        focus_node_iri=DATA.missing_seqnum,
        focus_node_type=IN_BUILT_ONTO.TestStillImageRepresentationWithSeqnum,
        result_path=KNORA_API.seqnum,
        severity=SH.Violation,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def report_coexist_with_date(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a                            sh:ValidationResult;
     sh:focusNode                  <http://data/value_date_range_first_is_ce_second_bce>;
     sh:resultMessage              "date message";
     sh:resultPath                 api-shapes:dateHasStart;
     sh:resultSeverity             sh:Violation;
     sh:sourceConstraintComponent  dash:CoExistsWithConstraintComponent;
     sh:sourceShape                [] 
               ].
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    data_str = f"""{PREFIXES}
    <http://data/date_range_first_is_ce_second_bce> a onto:ClassWithEverything ;
        rdfs:label "date_range_first_is_ce_second_bce"^^xsd:string ;
        onto:testSubDate1 <http://data/value_date_range_first_is_ce_second_bce> .
    
    <http://data/value_date_range_first_is_ce_second_bce> a knora-api:DateValue ;
        api-shapes:dateHasStart "2000-01-01"^^xsd:date ;
        knora-api:valueAsString "GREGORIAN:CE:2000:BCE:1900"^^xsd:string .
    """
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=DASH.CoExistsWithConstraintComponent,
        focus_node_iri=DATA.date_range_first_is_ce_second_bce,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testSubDate1,
        severity=SH.Violation,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_coexist_with() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.SEQNUM_IS_PART_OF,
        res_iri=DATA.missing_seqnum,
        res_class=IN_BUILT_ONTO.TestStillImageRepresentationWithSeqnum,
        message=Literal("Coexist message from knora-api turtle"),
        severity=SH.Violation,
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
    sh:resultMessage "A valid node from the list 'firstList' must be used with this property." ;
    sh:resultPath knora-api:listValueAsListNode ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:InConstraintComponent ;
    sh:sourceShape [ ] ;
    sh:value "firstList / other" .
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
        focus_node_iri=DATA.list_node_non_existent,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testListProp,
        severity=SH.Violation,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_unknown_list_node() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.GENERIC,
        res_iri=DATA.list_node_non_existent,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testListProp,
        message=Literal("A valid node from the list 'firstList' must be used with this property."),
        input_value=Literal("firstList / other"),
        severity=SH.Violation,
    )


@pytest.fixture
def report_unknown_list_name(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
[
    a sh:ValidationResult ;
    sh:detail _:bn_list_name_non_existent ;
    sh:focusNode <http://data/list_name_non_existent> ;
    sh:resultMessage "Value does not have shape <http://rdfh.ch/lists/9999/b7p3ucDWQ5CZuKpVo-im7Q>" ;
    sh:resultPath <http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp> ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:NodeConstraintComponent ;
    sh:sourceShape <http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp_PropShape> ;
    sh:value <http://data/value_list_name_non_existent> ] .

_:bn_list_name_non_existent a sh:ValidationResult ;
    sh:focusNode <http://data/value_list_name_non_existent> ;
    sh:resultMessage "A valid node from the list 'firstList' must be used with this property." ;
    sh:resultPath <http://api.knora.org/ontology/knora-api/v2#listValueAsListNode> ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent sh:InConstraintComponent ;
    sh:sourceShape _:bn_source ;
    sh:value "other / n1" .
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
        focus_node_iri=DATA.list_name_non_existent,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testListProp,
        severity=SH.Violation,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_unknown_list_name() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.GENERIC,
        res_iri=DATA.list_name_non_existent,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testListProp,
        message=Literal("A valid node from the list 'firstList' must be used with this property."),
        input_value=Literal("other / n1"),
        severity=SH.Violation,
    )


@pytest.fixture
def report_missing_file_value(onto_graph: Graph) -> tuple[Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ a sh:ValidationResult ;
            sh:focusNode <http://data/id_video_missing> ;
            sh:resultMessage "Cardinality 1" ;
            sh:resultPath <http://api.knora.org/ontology/knora-api/v2#hasMovingImageFileValue> ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
            sh:sourceShape _:n9f446ddf698b43ee9bc70be5f606ec25b13 ] .
    """
    data_str = f"""{PREFIXES}
    <http://data/id_video_missing> a <http://0.0.0.0:3333/ontology/9999/onto/v2#TestMovingImageRepresentation> ;
        rdfs:label "TestMovingImageRepresentation"^^xsd:string .
    """
    graphs = Graph()
    graphs.parse(data=validation_str, format="ttl")
    graphs.parse(data=data_str, format="ttl")
    graphs += onto_graph
    val_bn = next(graphs.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.MinCountConstraintComponent,
        focus_node_iri=DATA.id_video_missing,
        focus_node_type=ONTO.TestMovingImageRepresentation,
        result_path=KNORA_API.hasMovingImageFileValue,
        severity=SH.Violation,
    )
    return graphs, base_info


@pytest.fixture
def extracted_missing_file_value() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.MIN_CARD,
        res_iri=DATA.id_video_missing,
        res_class=ONTO.TestMovingImageRepresentation,
        property=KNORA_API.hasMovingImageFileValue,
        expected=Literal("Cardinality 1"),
        severity=SH.Violation,
    )


@pytest.fixture
def report_single_line_constraint_component(onto_graph: Graph) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f'''{PREFIXES}
        [ a sh:ValidationResult ;
            sh:focusNode <http://data/value_copyright_holder_with_newline> ;
            sh:resultMessage "The copyright holder must be a string without newlines." ;
            sh:resultPath <http://api.knora.org/ontology/knora-api/v2#hasCopyrightHolder> ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent <http://datashapes.org/dash#SingleLineConstraintComponent> ;
            sh:sourceShape [ ] ;
            sh:value """FirstLine
Second Line""" ] .
    '''
    data_str = f'''{PREFIXES}
<http://data/copyright_holder_with_newline> a <http://0.0.0.0:3333/ontology/9999/onto/v2#TestArchiveRepresentation> ;
rdfs:label "TestArchiveRepresentation zip"^^xsd:string ;
knora-api:hasArchiveFileValue <http://data/value_copyright_holder_with_newline> .

<http://data/value_copyright_holder_with_newline> a knora-api:ArchiveFileValue ;
    knora-api:fileValueHasFilename "this/is/filepath/file.zip"^^xsd:string ;
    knora-api:hasAuthorship "authorship_1"^^xsd:string ;
    knora-api:hasCopyrightHolder """FirstLine
Second Line"""^^xsd:string ;
    knora-api:hasLicense <http://rdfh.ch/licenses/cc-by-4.0> .
    '''
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=DASH.SingleLineConstraintComponent,
        focus_node_iri=DATA.copyright_holder_with_newline,
        focus_node_type=ONTO.TestArchiveRepresentation,
        result_path=KNORA_API.hasCopyrightHolder,
        severity=SH.Violation,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def report_single_line_constraint_component_content_is_value(
    onto_graph: Graph,
) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f'''{PREFIXES}
[ a sh:ValidationResult ;
            sh:detail _:detail_bn ;
            sh:focusNode <http://data/simple_text_with_newlines> ;
            sh:resultMessage "This property requires a TextValue" ;
            sh:resultPath <http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText> ;
            sh:resultSeverity sh:Violation ;
            sh:sourceConstraintComponent sh:NodeConstraintComponent ;
            sh:sourceShape <http://0.0.0.0:3333/ontology/9999/onto/v2#testSimpleText_PropShape> ;
            sh:value <http://data/value_simple_text_with_newlines> ].

    _:detail_bn a sh:ValidationResult ;
    sh:focusNode <http://data/value_simple_text_with_newlines> ;
    sh:resultMessage "The value must be a non-empty string without newlines." ;
    sh:resultPath <http://api.knora.org/ontology/knora-api/v2#valueAsString> ;
    sh:resultSeverity sh:Violation ;
    sh:sourceConstraintComponent <http://datashapes.org/dash#SingleLineConstraintComponent> ;
    sh:sourceShape [ ] ;
    sh:value """This may not

have newlines""" .
    '''
    data_str = f'''{PREFIXES}
<http://data/simple_text_with_newlines> a onto:ClassWithEverything ;
    rdfs:label "With linebreaks"^^xsd:string ;
    onto:testSimpleText <http://data/value_simple_text_with_newlines> .

<http://data/value_simple_text_with_newlines> a knora-api:TextValue ;
    knora-api:valueAsString """This may not

have newlines"""^^xsd:string .
    '''
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    detail_bn = next(validation_g.objects(val_bn, SH.detail))
    detail = DetailBaseInfo(
        detail_bn=detail_bn,
        source_constraint_component=DASH.SingleLineConstraintComponent,
    )
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.NodeConstraintComponent,
        focus_node_iri=DATA.simple_text_with_newlines,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testSimpleText,
        severity=SH.Violation,
        detail=detail,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_single_line_constraint_component() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.GENERIC,
        res_iri=DATA.copyright_holder_with_newline,
        res_class=ONTO.TestArchiveRepresentation,
        property=KNORA_API.hasCopyrightHolder,
        message=Literal("The copyright holder must be a string without newlines."),
        input_value=Literal("with newline"),
        severity=SH.Violation,
    )


@pytest.fixture
def report_date_single_month_does_not_exist(
    onto_graph: Graph,
) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [    a                             sh:ValidationResult;
         sh:focusNode                  <http://data/value_date_month_does_not_exist>;
         sh:resultMessage              "date message";
         sh:resultPath                 api-shapes:dateHasStart;
         sh:resultSeverity             sh:Violation;
         sh:sourceConstraintComponent  sh:OrConstraintComponent;
         sh:sourceShape                [] ;
         sh:value                      "1800-22-01"
       ] .
    """
    data_str = f"""{PREFIXES}
    <http://data/date_month_does_not_exist> a onto:ClassWithEverything ;
        rdfs:label "date_month_does_not_exist"^^xsd:string ;
        onto:testSubDate1 <http://data/value_date_month_does_not_exist> .
        
    <http://data/value_date_month_does_not_exist> a knora-api:DateValue ;
        api-shapes:dateHasEnd "1800-22-01"^^xsd:string ;
        api-shapes:dateHasStart "1800-22-01"^^xsd:string ;
        knora-api:valueAsString "GREGORIAN:CE:1800-22"^^xsd:string .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.OrConstraintComponent,
        focus_node_iri=DATA.date_month_does_not_exist,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testSubDate1,
        severity=SH.Violation,
        detail=None,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def extracted_date_single_month_does_not_exist() -> ValidationResult:
    return ValidationResult(
        violation_type=ViolationType.GENERIC,
        res_iri=DATA.date_month_does_not_exist,
        res_class=ONTO.ClassWithEverything,
        property=ONTO.testSubDate1,
        message=Literal("date message"),
        input_value=Literal("1800-22"),
        severity=SH.Violation,
    )


@pytest.fixture
def report_date_range_wrong_yyyy(
    onto_graph: Graph,
) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ rdf:type                      sh:ValidationResult;
     sh:focusNode                  <http://data/value_date_range_wrong_yyyy>;
     sh:resultMessage              "date message";
     sh:resultPath                 api-shapes:dateHasStart;
     sh:resultSeverity             sh:Violation;
     sh:sourceConstraintComponent  sh:LessThanOrEqualsConstraintComponent;
     sh:sourceShape                [] ;
     sh:value                      "2000"^^xsd:gYear
   ] .
    """
    data_str = f"""{PREFIXES}
    <http://data/date_range_wrong_yyyy> a onto:ClassWithEverything ;
        rdfs:label "date_range_wrong_yyyy"^^xsd:string ;
        onto:testSubDate1 <http://data/value_date_range_wrong_yyyy> .

    <http://data/value_date_range_wrong_yyyy> a knora-api:DateValue ;
        api-shapes:dateHasEnd "1900"^^xsd:gYear ;
        api-shapes:dateHasStart "2000"^^xsd:gYear ;
        knora-api:valueAsString "GREGORIAN:CE:2000:CE:1900"^^xsd:string .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.LessThanOrEqualsConstraintComponent,
        focus_node_iri=DATA.date_range_wrong_yyyy,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testSubDate1,
        severity=SH.Violation,
        detail=None,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def report_date_range_wrong_to_ignore(
    onto_graph: Graph,
) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ rdf:type                      sh:ValidationResult;
     sh:focusNode                  <http://data/value_date_end_day_does_not_exist>;
     sh:resultMessage              "The end date must be equal or later than the start date.";
     sh:resultPath                 api-shapes:dateHasStart;
     sh:resultSeverity             sh:Violation;
     sh:sourceConstraintComponent  sh:LessThanOrEqualsConstraintComponent;
     sh:sourceShape                _:b13;
     sh:value                      "1800-01-01"^^xsd:date
   ] .
    """
    data_str = f"""{PREFIXES}
    <http://data/date_end_day_does_not_exist> a onto:ClassWithEverything ;
        rdfs:label "date_end_day_does_not_exist"^^xsd:string ;
        onto:testSubDate1 <http://data/value_date_end_day_does_not_exist> .
    
    <http://data/value_date_end_day_does_not_exist> a knora-api:DateValue ;
        api-shapes:dateHasEnd "1900-01-50"^^xsd:string ;
        api-shapes:dateHasStart "1800-01-01"^^xsd:date ;
        knora-api:valueAsString "GREGORIAN:CE:1800-01-01:CE:1900-01-50"^^xsd:string .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.LessThanOrEqualsConstraintComponent,
        focus_node_iri=DATA.date_end_day_does_not_exist,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=ONTO.testSubDate1,
        severity=SH.Violation,
        detail=None,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def report_standoff_link_target_is_iri(
    onto_graph: Graph,
) -> tuple[Graph, Graph, ValidationResultBaseInfo]:
    validation_str = f"""{PREFIXES}
    [ rdf:type                      sh:ValidationResult;
     sh:focusNode                  <http://data/richtext_with_standoff_to_resource_in_db>;
     sh:resultMessage              "A stand-off link must target an existing resource.";
     sh:resultPath                 knora-api:hasStandoffLinkTo;
     sh:resultSeverity             sh:Violation;
     sh:sourceConstraintComponent  sh:ClassConstraintComponent;
     sh:sourceShape                [] ;
     sh:value                      <http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA>
   ] .
    """
    data_str = f"""{PREFIXES}
<http://data/richtext_with_standoff_to_resource_in_db> a onto:ClassWithEverything ;
    rdfs:label "Richtext"^^xsd:string ;
    onto:testRichtext <http://data/value_richtext_with_standoff_to_resource_in_db> ;
    knora-api:hasStandoffLinkTo <http://rdfh.ch/4123/DiAmYQzQSzC7cdTo6OJMYA> .

<http://data/value_richtext_with_standoff_to_resource_in_db> a knora-api:TextValue ;
    knora-api:textValueAsXml "Text"^^xsd:string .
    """
    validation_g = Graph()
    validation_g.parse(data=validation_str, format="ttl")
    onto_data_g = Graph()
    onto_data_g += onto_graph
    onto_data_g.parse(data=data_str, format="ttl")
    val_bn = next(validation_g.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.ClassConstraintComponent,
        focus_node_iri=DATA.richtext_with_standoff_to_resource_in_db,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=KNORA_API.hasStandoffLinkTo,
        severity=SH.Violation,
        detail=None,
    )
    return validation_g, onto_data_g, base_info


@pytest.fixture
def result_unknown_component(onto_graph: Graph) -> tuple[Graph, ValidationResultBaseInfo]:
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
    data_str = f"""{PREFIXES}
        <http://data/empty_label> a onto:ClassWithEverything ;
            rdfs:label " "^^xsd:string .
    """
    graphs = Graph()
    graphs.parse(data=validation_str, format="ttl")
    graphs.parse(data=data_str, format="ttl")
    graphs += onto_graph
    val_bn = next(graphs.subjects(RDF.type, SH.ValidationResult))
    base_info = ValidationResultBaseInfo(
        result_bn=val_bn,
        source_constraint_component=SH.PatternConstraintComponent,
        focus_node_iri=DATA.empty_label,
        focus_node_type=ONTO.ClassWithEverything,
        result_path=RDFS.label,
        severity=SH.Violation,
    )
    return graphs, base_info
