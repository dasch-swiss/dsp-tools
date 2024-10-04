import warnings
from copy import deepcopy
from pathlib import Path

from lxml import etree
from rdflib import SH
from rdflib import Graph
from termcolor import cprint

from dsp_tools.commands.xml_validate.api_connection import OntologyConnection
from dsp_tools.commands.xml_validate.api_connection import ShaclValidator
from dsp_tools.commands.xml_validate.deserialise_input import deserialise_xml
from dsp_tools.commands.xml_validate.make_data_rdf import make_data_rdf
from dsp_tools.commands.xml_validate.models.data_deserialised import ProjectDeserialised
from dsp_tools.commands.xml_validate.models.data_rdf import DataRDF
from dsp_tools.commands.xml_validate.models.validation import ValidationReport
from dsp_tools.commands.xml_validate.reformat_validaton_result import reformat_validation_graph
from dsp_tools.commands.xml_validate.sparql.construct_shapes import construct_shapes_graph
from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.utils.xml_utils import parse_xml_file
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree
from dsp_tools.utils.xml_utils import transform_into_localnames
from dsp_tools.utils.xml_validation import validate_xml

LIST_SEPARATOR = "\n    - "


def xml_validate(filepath: Path, api_url: str, dev_route: bool, save_graphs: bool) -> bool:  # noqa: ARG001 (unused argument)
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
    ontologies, shapes = _get_shacl(onto_con)
    data_graph = data_rdf.make_graph()
    if save_graphs:
        _save_graph(filepath, ontologies, shapes, data_graph)
    # data_graph += ontologies
    val = ShaclValidator(api_url)
    report = _validate(val, shapes, data_graph)
    if report.conforms:
        cprint("\n   Validation passed!   ", color="green", attrs=["bold", "reverse"])
    else:
        reformatted = reformat_validation_graph(report.validation_graph, data_graph)
        problem_msg = reformatted.get_msg()
        cprint("\n   Validation errors found!   ", color="light_red", attrs=["bold", "reverse"])
        print(problem_msg)
        if reformatted.unexpected_results:
            reformatted.unexpected_results.save_inform_user(
                results_graph=report.validation_graph,
                shacl=report.shacl_graph,
                data=data_graph,
            )
    return True


def _inform_about_experimental_feature() -> None:
    what_is_validated = [
        "This is an experimental feature, it will change and be extended continuously. "
        "The following information of your data is being validated:",
        "Cardinalities",
    ]
    warnings.warn(DspToolsUserWarning(LIST_SEPARATOR.join(what_is_validated)))


def _save_graph(filepath: Path, onto: Graph, shacl: Graph, data: Graph) -> None:
    parent_directory = filepath.parent
    new_directory = parent_directory / "graphs"
    new_directory.mkdir(exist_ok=True)
    cprint(f"\n   Saving graphs to {new_directory}   ", color="light_blue", attrs=["bold", "reverse"])
    generic_filepath = new_directory / filepath.stem
    onto.serialize(f"{generic_filepath}_ONTO.ttl")
    shacl.serialize(f"{generic_filepath}_SHACL.ttl")
    data.serialize(f"{generic_filepath}_DATA.ttl")
    onto_data = onto + data
    onto_data.serialize(f"{generic_filepath}_ONTO_DATA.ttl")


def _validate(validator: ShaclValidator, shapes_graph: Graph, data_graph: Graph) -> ValidationReport:
    shape_str = shapes_graph.serialize(format="ttl")
    data_str = data_graph.serialize(format="ttl")
    results = validator.validate(data_str, shape_str)
    conforms = bool(next(results.objects(None, SH.conforms)))
    return ValidationReport(
        conforms=conforms,
        validation_graph=results,
        shacl_graph=shapes_graph,
        data_graph=data_graph,
    )


def _get_shacl(onto_con: OntologyConnection) -> tuple[Graph, Graph]:
    ontologies = _get_project_ontos(onto_con)
    knora_ttl = onto_con.get_knora_api()
    kag = Graph()
    kag.parse(data=knora_ttl, format="ttl")
    onto_for_construction = deepcopy(ontologies) + kag
    shapes = construct_shapes_graph(onto_for_construction)
    shapes += ontologies
    return ontologies, shapes


def _get_project_ontos(onto_con: OntologyConnection) -> Graph:
    all_ontos = onto_con.get_ontologies()
    onto_g = Graph()
    for onto in all_ontos:
        og = Graph()
        og.parse(data=onto, format="ttl")
        onto_g += og
    return onto_g


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
    with open("src/dsp_tools/resources/xml_validate/replace_namespace.xslt", "rb") as xslt_file:
        xslt_data = xslt_file.read()
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    namespace = f"{api_url}/ontology/{shortcode}/{default_ontology}/v2#"
    xslt_root = etree.XML(xslt_data)
    transform = etree.XSLT(xslt_root)
    replacement_value = etree.XSLT.strparam(namespace)
    return transform(root, replacementValue=replacement_value).getroot()
