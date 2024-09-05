
from rdflib import RDF
from rdflib import RDFS
from rdflib import SH
from rdflib import BNode
from rdflib import Graph
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xml_validate.models.input_problems import DuplicateContent
from dsp_tools.commands.xml_validate.models.input_problems import GenericContentViolation
from dsp_tools.commands.xml_validate.models.input_problems import InputProblem
from dsp_tools.commands.xml_validate.models.input_problems import ListViolation
from dsp_tools.commands.xml_validate.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import NodeInfo
from dsp_tools.commands.xml_validate.models.input_problems import ValidationGraphs
from dsp_tools.commands.xml_validate.models.input_problems import ValueInfo
from dsp_tools.models.exceptions import BaseError

VAL_ONTO = Namespace("http://api.knora.org/validation-onto#")


def reformat_validation_graph(validation_graph: ValidationGraphs) -> list[InputProblem]:
    """
    Reformats the validation result from a RDF graph into class instances
    that are used to communicate the problems with the user.

    Args:
        validation_graph: Contains the possible two validation errors

    Returns:
        List of individual problems
    """
    problems: list[InputProblem] = []
    g = Graph()
    if validation_graph.node_violations:
        g = validation_graph.node_violations
        problems.extend(_reformat_node_constraint_component(validation_graph.node_violations))
    if validation_graph.cardinality_violations:
        g += validation_graph.cardinality_violations
        problems.extend(_reformat_cardinality_constraint_component(validation_graph.cardinality_violations))
    _check_expected_constraint_components(g)
    return problems


def _check_expected_constraint_components(g: Graph) -> None:
    # In the future this would not raise an error but be part of the error message
    # with the instruction to contact support.
    # The validation graph would be saved for further analysis.
    known_components = {
        SH.MaxCountConstraintComponent,
        SH.ClassConstraintComponent,
        SH.InConstraintComponent,
        SH.NodeConstraintComponent,
        SH.SPARQLConstraintComponent,
    }
    unknown_components = set()
    for _, _, component in g.triples((None, SH.sourceConstraintComponent, None)):
        if component not in known_components:
            unknown_components.add(str(component))
    if unknown_components:
        raise BaseError(f"Unknown constraint component: {', '.join(unknown_components)}")


def _reformat_cardinality_constraint_component(g: Graph) -> list[InputProblem]:
    count_violation: list[InputProblem] = _reformat_cardinality_violations(g)
    count_violation.extend(_reformat_sparql_constraint_component(g))
    return count_violation


def _reformat_cardinality_violations(g: Graph) -> list[InputProblem]:
    # Not implemented:
    # - sh:MinCountConstraintComponent
    # - sh:ClosedConstraintComponent (no cardinality listed for resource)
    max_counts = g.subjects(SH.sourceConstraintComponent, SH.MaxCountConstraintComponent)
    return [_reformat_one_max_count(g, x) for x in max_counts]


def _reformat_one_max_count(g: Graph, bn: BNode) -> MaxCardinalityViolation:
    res_id = str(next(g.objects(bn, SH.focusNode)))
    prop_iri = next(g.objects(bn, SH.resultPath))
    prop = _reformat_prop_iri(str(prop_iri))
    return MaxCardinalityViolation(res_id=res_id, prop_name=prop)


def _reformat_sparql_constraint_component(g: Graph) -> list[DuplicateContent]:
    sparql_nodes = g.subjects(SH.sourceConstraintComponent, SH.SPARQLConstraintComponent)
    return [_reformat_one_sparql_constraint_component(g, x) for x in sparql_nodes]


def _reformat_one_sparql_constraint_component(g: Graph, bn: BNode) -> DuplicateContent:
    detail_bn = list(g.triples((bn, None, None)))
    problem_resource = str(next(g.objects(bn, SH.focusNode)))
    prop_iri = str(next(g.objects(detail_bn, SH.resultPath)))
    prop = _reformat_prop_iri(prop_iri)
    content = str(next(g.objects(detail_bn, SH.value)))
    return DuplicateContent(res_id=problem_resource, prop_name=prop, content=content)


def _reformat_node_constraint_component(g: Graph):
    nodes_bns = g.subjects(SH.sourceConstraintComponent, SH.NodeConstraintComponent)
    return [_reformat_one_node_constraint_component(g, bn) for bn in nodes_bns]


def _reformat_one_node_constraint_component(g: Graph, bn: BNode) -> InputProblem:
    # To be expected in future:
    # - sh:MaxLengthConstraintComponent (for GUI attribute of string)
    # - sh:MinLengthConstraintComponent all strings at least 1 length
    # - sh:PatternConstraintComponent (regex)
    detail_bn = next(g.objects(bn, SH.detail))
    component_type = next(g.objects(detail_bn, SH.sourceConstraintComponent))
    match component_type:
        case SH.ClassConstraintComponent:
            return _reformat_class_constraint_component(g, bn, detail_bn)
        case SH.InConstraintComponent:
            return _reformat_in_constraint_component(g, bn, detail_bn)
        case _:
            raise NotImplementedError


def _reformat_class_constraint_component(g: Graph, node_bn: BNode, detail_bn: BNode) -> GenericContentViolation:
    generic_info = _get_node_constraint_info(g, node_bn, detail_bn)
    property_values = _get_value_info(g, node_bn)
    return GenericContentViolation(
        res_id=generic_info.res_id,
        prop_name=generic_info.prop_name,
        content=property_values.hasValue,
        value_type=property_values.rdf_type,
        msg=generic_info.message,
    )


def _reformat_in_constraint_component(g: Graph, node_bn: BNode, detail_bn: BNode) -> ListViolation:
    generic_info = _get_node_constraint_info(g, node_bn, detail_bn)
    value_info = _get_value_info(g, node_bn)
    return ListViolation(
        res_id=generic_info.res_id,
        prop_name=generic_info.prop_name,
        msg=generic_info.message,
        list_name=str(value_info.hasListName),
        node_name=value_info.hasValue,
    )


def _get_node_constraint_info(g: Graph, node_bn: BNode, detail_bn: BNode) -> NodeInfo:
    res_id = str(next(g.objects(node_bn, SH.focusNode)))
    prop_iri = next(g.objects(node_bn, SH.resultPath))
    prop_name = _reformat_prop_iri(str(prop_iri))
    msg = str(next(g.objects(detail_bn, SH.resultMessage)))
    return NodeInfo(res_id=res_id, prop_name=prop_name, message=msg)


def _get_value_info(g: Graph, node_bn: BNode) -> ValueInfo:
    val_bn = next(g.objects(node_bn, SH.value))
    val = next(g.objects(val_bn, VAL_ONTO.hasValue))
    list_val = list(g.objects(val_bn, VAL_ONTO.hasListName))
    rdf_types = list(g.objects(val_bn, RDF.type))
    onto_type = _get_specific_type(rdf_types)
    return ValueInfo(rdf_type=str(onto_type), hasValue=str(val), hasListName=list_val)


def _reformat_prop_iri(prop: str) -> str:
    onto = str(prop).split("/")[-2]
    return f'{onto}:{str(prop).split("#")[-1]}'


def _get_specific_type(rdf_types: list[URIRef]) -> str:
    for ele in rdf_types:
        if ele == RDFS.Resource:
            pass
        elif ele == VAL_ONTO.Value:
            pass
        else:
            return str(ele).split("#")[-1]
