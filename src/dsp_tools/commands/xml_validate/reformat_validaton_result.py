import regex
from rdflib import RDF
from rdflib import SH
from rdflib import BNode
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xml_validate.models.input_error import AllErrors
from dsp_tools.commands.xml_validate.models.input_error import DuplicateContent
from dsp_tools.commands.xml_validate.models.input_error import GenericContentViolation
from dsp_tools.commands.xml_validate.models.input_error import InputProblem
from dsp_tools.commands.xml_validate.models.input_error import ListViolation
from dsp_tools.commands.xml_validate.models.input_error import MaxCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_error import ValidationProblem
from dsp_tools.commands.xml_validate.models.input_error import ValidationProblemValue
from dsp_tools.models.exceptions import InputError

VAL_ONTO = Namespace("http://api.knora.org/validation-onto#")


def parse_ttl_file(ttl_path: str) -> Graph:
    onto = Graph()
    onto.parse(ttl_path)
    return onto


def reformat_validation_graph(
    #     validation_graph: Graph
) -> AllErrors:
    problems = _reformat_property_violations()
    problems.extend(_reformat_cardinality_violations())
    if problems:
        er = AllErrors(errors=problems)
        msg = er.get_msg()
        raise InputError(msg)


def _separate_nodes_with_details_and_without(g: Graph) -> tuple[list[BNode], list[BNode]]:
    individual_validation_results = list(g.subjects(RDF.type, SH.ValidationResult))

    def check(bn: BNode) -> list[BNode]:
        return list(g.objects(bn, SH.detail))

    details = [x for x in individual_validation_results if check(x)]
    no_details = [x for x in individual_validation_results if not check(x)]
    return details, no_details


def _reformat_res_id(res: URIRef) -> str:
    return regex.search(r"/data/(.+)$", str(res)).group(1)


def _reformat_prop_iri(prop: URIRef) -> str:
    onto = str(prop).split("/")[-2]
    return f'{onto}:{str(prop).split("#")[-1]}'


def _reformat_cardinality_violations(
    # validation_graph: Graph
) -> list[InputProblem]:
    validation_graph = parse_ttl_file("testdata/xml-validate/validation-results/card-violations.ttl")
    sparql_violation_bns, card_violation_bns = _separate_cardinality_violation_types(validation_graph)
    problems: list[InputProblem] = _reformat_sparql_violations(validation_graph, sparql_violation_bns)
    problems.extend(_reformat_card_violations(validation_graph, card_violation_bns))
    return problems


def _separate_cardinality_violation_types(validation_graph: Graph) -> tuple[list[BNode], list[BNode]]:
    sparql_violation, no_detail = _separate_nodes_with_details_and_without(validation_graph)
    sparql_bn = list(validation_graph.subjects(SH.sourceConstraintComponent, SH.SPARQLConstraintComponent))
    card_violations = [x for x in no_detail if x not in sparql_bn]
    return sparql_violation, card_violations


def _reformat_sparql_violations(g: Graph, nodes: list[BNode]) -> list[DuplicateContent]:
    return [_reformat_one_sparql_violation(g, x) for x in nodes]


def _reformat_one_sparql_violation(g: Graph, bn: BNode) -> DuplicateContent:
    detail_bn = next(g.objects(bn, SH.detail))
    problem_iri = next(g.objects(bn, SH.focusNode))
    problem_resource = _reformat_res_id(problem_iri)
    prop_iri = str(next(g.objects(detail_bn, SH.resultPath)))
    prop = _reformat_prop_iri(prop_iri)
    content = str(next(g.objects(detail_bn, SH.value)))
    return DuplicateContent(res_id=problem_resource, prop_name=prop, content=content)


def _reformat_card_violations(g: Graph, nodes: list[BNode]) -> list[InputProblem]:
    return [_reformat_one_card_violation(g, x) for x in nodes]


def _reformat_one_card_violation(g: Graph, bn: BNode) -> InputProblem:
    res_iri = next(g.objects(bn, SH.focusNode))
    res_id = _reformat_res_id(res_iri)
    prop_iri = next(g.objects(bn, SH.resultPath))
    prop = _reformat_prop_iri(prop_iri)
    violation_type = str(next(g.objects(bn, SH.sourceConstraintComponent)))
    match violation_type:
        case "http://www.w3.org/ns/shacl#MaxCountConstraintComponent":
            return MaxCardinalityViolation(res_id=res_id, prop_name=prop)
        case _:
            raise NotImplementedError


def _reformat_property_violations(
    # validaton_graph: Graph
) -> list[InputProblem]:
    validation_graph = parse_ttl_file("testdata/xml-validate/validation-results/prop-violations.ttl")
    validation_nodes, _ = _separate_nodes_with_details_and_without(validation_graph)
    extracted = [_extract_one_validation_result(x, validation_graph) for x in validation_nodes]
    return _reformat_property_validation_results(extracted)


def _extract_one_validation_result(validation_bn: BNode, validation_graph: Graph) -> ValidationProblem:
    res_iri = next(validation_graph.objects(validation_bn, SH.focusNode))
    prop_iri = next(validation_graph.objects(validation_bn, SH.resultPath))
    detail_bn = next(validation_graph.objects(validation_bn, SH.detail))
    violation_message = str(next(validation_graph.objects(detail_bn, SH.resultMessage)))
    value_bn = next(validation_graph.objects(validation_bn, SH.value))
    has_values = next(validation_graph.objects(value_bn, VAL_ONTO.hasValue))
    list_name = list(validation_graph.objects(value_bn, VAL_ONTO.hasListName))
    val_types = list(validation_graph.objects(value_bn, RDF.type))
    problem_value = ValidationProblemValue(rdf_types=val_types, hasValue=has_values, hasListName=list_name)
    return ValidationProblem(
        resource_iri=res_iri,
        property_iri=prop_iri,
        violation_value=problem_value,
        message=str(violation_message),
    )


def _reformat_property_validation_results(violations: list[ValidationProblem]) -> list[InputProblem]:
    return [_reformat_one_property_violation(x) for x in violations]


def _reformat_one_property_violation(violation: ValidationProblem) -> InputProblem:
    val_types = [str(x) for x in violation.violation_value.rdf_types]
    if "http://api.knora.org/validation-onto#ListValue" in val_types:
        return _reformat_list_violation(violation)
    elif "http://api.knora.org/validation-onto#LinkValue" in val_types:
        return _reformat_link_violation(violation)
    else:
        return _reformat_other_violation(violation)


def _reformat_list_violation(violation: ValidationProblem) -> InputProblem:
    res_id = _reformat_res_id(violation.resource_iri)
    prop = _reformat_prop_iri(violation.property_iri)
    return ListViolation(
        res_id=res_id,
        prop_name=prop,
        msg=violation.message,
        list_name=str(violation.violation_value.hasListName[0]),
        node_name=str(violation.violation_value.hasValue),
    )


def _reformat_link_violation(violation: ValidationProblem) -> InputProblem:
    res_id = _reformat_res_id(violation.resource_iri)
    prop = _reformat_prop_iri(violation.property_iri)
    val = _reformat_res_id(violation.violation_value.hasValue)
    return GenericContentViolation(res_id=res_id, prop_name=prop, content=val, msg=violation.message)


def _reformat_other_violation(violation: ValidationProblem) -> InputProblem:
    res_id = _reformat_res_id(violation.resource_iri)
    prop = _reformat_prop_iri(violation.property_iri)
    return GenericContentViolation(
        res_id=res_id, prop_name=prop, content=str(violation.violation_value.hasValue), msg=violation.message
    )
