import regex
from rdflib import RDF
from rdflib import SH
from rdflib import BNode
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xml_validate.models.data_rdf import ValidationProblem
from dsp_tools.commands.xml_validate.models.data_rdf import ValidationProblemValue
from dsp_tools.commands.xml_validate.models.input_error import AllErrors
from dsp_tools.commands.xml_validate.models.input_error import DuplicateContent
from dsp_tools.commands.xml_validate.models.input_error import InputProblem
from dsp_tools.models.exceptions import InputError

VAL_ONTO = Namespace("http://api.knora.org/validation-onto#")


def parse_ttl_file(ttl_path: str) -> Graph:
    onto = Graph()
    onto.parse(ttl_path)
    return onto


def reformat_validation_graph(validation_graph: Graph) -> AllErrors:
    problems = _reformat_property_violations(validation_graph)
    problems.extend(_reformat_cardinality_violations(validation_graph))
    if problems:
        er = AllErrors(errors=problems)
        msg = er.get_msg()
        raise InputError(msg)


def _separate_nodes_with_details_and_without(g: Graph) -> list[BNode]:
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
    pass


def _reformat_one_card_violation(g: Graph, bn: BNode) -> InputProblem:
    pass


def _reformat_property_violations(validaton_graph: Graph) -> list[InputProblem]:
    validaton_graph = parse_ttl_file("testdata/xml-validate/validation-results/prop-violations.ttl")


def reformat_one_validation_result(validation_bn: BNode, validation_graph: Graph) -> ValidationProblem:
    problem_resource = next(validation_graph.objects(validation_bn, SH.focusNode))
    problem_prop = next(validation_graph.objects(validation_bn, SH.resultPath))
    detail_bn = next(validation_graph.objects(validation_bn, SH.detail))
    violation_message = str(next(validation_graph.objects(detail_bn, SH.resultMessage)))
    value_bn = next(validation_graph.objects(validation_bn, SH.value))
    val_types = list(validation_graph.objects(value_bn, RDF.type))
    has_values = list(validation_graph.objects(value_bn, VAL_ONTO.hasValue))
    list_name = list(validation_graph.objects(value_bn, VAL_ONTO.hasListName))
    problem_value = ValidationProblemValue(rdf_types=val_types, hasValue=has_values, hasListName=list_name)
    return ValidationProblem(
        resource_iri=problem_resource,
        property_iri=problem_prop,
        violation_value=problem_value,
        message=str(violation_message),
    )


_reformat_cardinality_violations()
