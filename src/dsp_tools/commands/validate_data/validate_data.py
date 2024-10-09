import warnings
from copy import deepcopy
from pathlib import Path

from lxml import etree
from rdflib import SH
from rdflib import Graph
from termcolor import cprint

from dsp_tools.commands.validate_data.api_connection import OntologyConnection
from dsp_tools.commands.validate_data.api_connection import ShaclValidator
from dsp_tools.commands.validate_data.deserialise_input import deserialise_xml
from dsp_tools.commands.validate_data.make_data_rdf import make_data_rdf
from dsp_tools.commands.validate_data.models.data_deserialised import ProjectDeserialised
from dsp_tools.commands.validate_data.models.data_rdf import DataRDF
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReports
from dsp_tools.commands.validate_data.reformat_validaton_result import reformat_validation_graph
from dsp_tools.commands.validate_data.sparql.cardinality_shacl import construct_cardinality_node_shapes
from dsp_tools.commands.validate_data.sparql.content_shacl import construct_content_shapes_graph
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.xml_utils import parse_xml_file
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree
from dsp_tools.utils.xml_utils import transform_into_localnames
from dsp_tools.utils.xml_validation import validate_xml

LIST_SEPARATOR = "\n    - "


def validate_data(filepath: Path, api_url: str, dev_route: bool, save_graphs: bool) -> bool:  # noqa: ARG001 (unused argument)
    """
    Takes a file and project information and validates it against the ontologies on the server.

    Args:
        filepath: path to the xml data file
        api_url: url of the api host
        dev_route: if this flag is set features that are still in development will be used
        save_graphs: if this flag is set, all the graphs will be saved in a folder

    Returns:
        true unless it crashed
    """
    _inform_about_experimental_feature()
    data_rdf, shortcode = _get_data_info_from_file(filepath, api_url)
    onto_con = OntologyConnection(api_url, shortcode)
    rdf_graphs = _create_graphs(onto_con, data_rdf)
    generic_filepath = Path()
    if save_graphs:
        generic_filepath = _save_graphs(filepath, rdf_graphs)
    val = ShaclValidator(api_url)
    report = _validate(val, rdf_graphs)
    if save_graphs:
        if report.content_validation:
            report.content_validation.serialize(f"{generic_filepath}_VALIDATION_REPORT_CONTENT.ttl")
        if report.cardinality_validation:
            report.cardinality_validation.serialize(f"{generic_filepath}_VALIDATION_REPORT_CARD.ttl")
    if report.conforms:
        cprint("\n   Validation passed!   ", color="green", attrs=["bold", "reverse"])
    else:
        reformatted = reformat_validation_graph(report)
        problem_msg = reformatted.get_msg(filepath)
        cprint("\n   Validation errors found!   ", color="light_red", attrs=["bold", "reverse"])
        print(problem_msg)
        if reformatted.unexpected_results:
            report_graphs = Graph()
            if report.content_validation:
                report_graphs += report.content_validation
            if report.cardinality_validation:
                report_graphs += report.cardinality_validation
            reformatted.unexpected_results.save_inform_user(
                results_graph=report_graphs,
                shacl=report.shacl_graphs,
                data=rdf_graphs.data,
            )
    return True


def _inform_about_experimental_feature() -> None:
    what_is_validated = [
        "This is an experimental feature, it will change and be extended continuously. "
        "The following information of your data is being validated:",
        "Cardinalities",
    ]
    warnings.warn(DspToolsUserWarning(LIST_SEPARATOR.join(what_is_validated)))


def _create_graphs(onto_con: OntologyConnection, data_rdf: DataRDF) -> RDFGraphs:
    ontologies = _get_project_ontos(onto_con)
    knora_ttl = onto_con.get_knora_api()
    kag = Graph()
    kag.parse(data=knora_ttl, format="ttl")
    onto_for_construction = deepcopy(ontologies) + kag
    card_shapes = construct_cardinality_node_shapes(onto_for_construction)
    content_shapes = construct_content_shapes_graph(onto_for_construction)
    api_shapes = Graph()
    api_shapes.parse("src/dsp_tools/resources/validate_data/api-shapes.ttl")
    content_shapes += api_shapes
    return RDFGraphs(
        data=data_rdf.make_graph(), ontos=ontologies, cardinality_shapes=card_shapes, content_shapes=content_shapes
    )


def _get_project_ontos(onto_con: OntologyConnection) -> Graph:
    all_ontos = onto_con.get_ontologies()
    onto_g = Graph()
    for onto in all_ontos:
        og = Graph()
        og.parse(data=onto, format="ttl")
        onto_g += og
    return onto_g


def _save_graphs(filepath: Path, rdf_graphs: RDFGraphs) -> Path:
    parent_directory = filepath.parent
    new_directory = parent_directory / "graphs"
    new_directory.mkdir(exist_ok=True)
    cprint(f"\n   Saving graphs to {new_directory}   ", color="light_blue", attrs=["bold", "reverse"])
    generic_filepath = new_directory / filepath.stem
    rdf_graphs.ontos.serialize(f"{generic_filepath}_ONTO.ttl")
    rdf_graphs.cardinality_shapes.serialize(f"{generic_filepath}_SHACL_CARD.ttl")
    rdf_graphs.content_shapes.serialize(f"{generic_filepath}_SHACL_CONTENT.ttl")
    rdf_graphs.data.serialize(f"{generic_filepath}_DATA.ttl")
    onto_data = rdf_graphs.data + rdf_graphs.ontos
    onto_data.serialize(f"{generic_filepath}_ONTO_DATA.ttl")
    return generic_filepath


def _validate(validator: ShaclValidator, rdf_graphs: RDFGraphs) -> ValidationReports:
    card_shacl = rdf_graphs.get_cardinality_shacl_str()
    card_data = rdf_graphs.get_cardinality_data_str()
    card_results = validator.validate(card_data, card_shacl)
    card_conforms = bool(next(card_results.objects(None, SH.conforms)))

    content_shacl = rdf_graphs.get_content_shacl_str()
    content_data = rdf_graphs.get_content_data_str()
    content_results = validator.validate(content_data, content_shacl)
    content_conforms = bool(next(content_results.objects(None, SH.conforms)))

    conforms = all([content_conforms, card_conforms])
    card_report: Graph | None = None
    content_report: Graph | None = None
    if not card_conforms:
        card_report = card_results
    if not content_conforms:
        content_report = content_results
    return ValidationReports(
        conforms=conforms,
        content_validation=content_report,
        cardinality_validation=card_report,
        shacl_graphs=rdf_graphs.cardinality_shapes + rdf_graphs.content_shapes,
        data_graph=rdf_graphs.data,
    )


def _get_data_info_from_file(file: Path, api_url: str) -> tuple[DataRDF, str]:
    cleaned_root = _parse_and_clean_file(file, api_url)
    deserialised: ProjectDeserialised = deserialise_xml(cleaned_root)
    rdf_data: DataRDF = make_data_rdf(deserialised.data)
    return rdf_data, deserialised.info.shortcode


def _parse_and_clean_file(file: Path, api_url: str) -> etree._Element:
    root = parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml(root)
    root = transform_into_localnames(root)
    return _replace_namespaces(root, api_url)


def _replace_namespaces(root: etree._Element, api_url: str) -> etree._Element:
    with open("src/dsp_tools/resources/validate_data/replace_namespace.xslt", "rb") as xslt_file:
        xslt_data = xslt_file.read()
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    namespace = f"{api_url}/ontology/{shortcode}/{default_ontology}/v2#"
    xslt_root = etree.XML(xslt_data)
    transform = etree.XSLT(xslt_root)
    replacement_value = etree.XSLT.strparam(namespace)
    return transform(root, replacementValue=replacement_value).getroot()
