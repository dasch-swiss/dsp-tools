from rdflib import RDF
from rdflib import SH
from rdflib import BNode
from rdflib import Graph
from rdflib import Namespace

from dsp_tools.commands.xml_validate.models.data_rdf import ValidationProblem
from dsp_tools.commands.xml_validate.models.data_rdf import ValidationProblemValue
from dsp_tools.commands.xml_validate.models.input_error import AllErrors

VAL_ONTO = Namespace("http://api.knora.org/validation-onto#")


def reformat_validation_graph(validation_graph: Graph) -> AllErrors:
    individual_validation_results = list(validation_graph.subjects(RDF.type, SH.ValidationResult))

    def check(bn: BNode) -> list[BNode]:
        return list(validation_graph.objects(bn, SH.detail))

    main_res = [x for x in individual_validation_results if check(x)]
    reformatted = [reformat_one_validation_result(x, validation_graph) for x in main_res]
    print()


# TODO: card violations don't have detail
# TODO: the value detail is not universally correct need to parse sparql differently


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


def parse_ttl_file(ttl_path: str) -> Graph:
    onto = Graph()
    onto.parse(ttl_path)
    return onto


p_graph = parse_ttl_file("testdata/xml-validate/validation-results/prop-violations.ttl")

reformat_validation_graph(p_graph)
