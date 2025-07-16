import importlib.resources
from pathlib import Path

from loguru import logger
from rdflib import Graph

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.legal_info_client_live import LegalInfoClientLive
from dsp_tools.commands.validate_data.api_clients import ListClient
from dsp_tools.commands.validate_data.api_clients import OntologyClient
from dsp_tools.commands.validate_data.models.api_responses import EnabledLicenseIris
from dsp_tools.commands.validate_data.models.api_responses import ListLookup
from dsp_tools.commands.validate_data.models.api_responses import OneList
from dsp_tools.commands.validate_data.models.api_responses import ProjectDataFromApi
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.prepare_data.get_rdf_like_data import get_rdf_like_data
from dsp_tools.commands.validate_data.prepare_data.make_data_graph import make_data_graph
from dsp_tools.commands.validate_data.sparql.construct_shacl import construct_shapes_graphs
from dsp_tools.utils.xml_parsing.get_lookups import get_authorship_lookup
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file


def get_info_and_parsed_resources_from_file(
    file: Path, api_url: str
) -> tuple[list[ParsedResource], str, dict[str, list[str]], list[str]]:
    root = parse_and_clean_xml_file(file)
    shortcode = root.attrib["shortcode"]
    authorship_lookup = get_authorship_lookup(root)
    permission_ids = [perm.attrib["id"] for perm in root.findall("permissions")]
    parsed_resources = get_parsed_resources(root, api_url)
    return parsed_resources, shortcode, authorship_lookup, permission_ids


def prepare_data_for_validation_from_parsed_resource(
    parsed_resources: list[ParsedResource],
    authorship_lookup: dict[str, list[str]],
    permission_ids: list[str],
    auth: AuthenticationClient,
    shortcode: str,
) -> tuple[RDFGraphs, set[str]]:
    used_iris = {x.res_type for x in parsed_resources}
    proj_info = _get_project_specific_information_from_api(auth, shortcode)
    list_lookup = _make_list_lookup(proj_info.all_lists)
    data_rdf = _make_data_graph_from_parsed_resources(parsed_resources, authorship_lookup, list_lookup)
    rdf_graphs = _create_graphs(data_rdf, shortcode, auth, proj_info, permission_ids)
    return rdf_graphs, used_iris


def _make_list_lookup(project_lists: list[OneList]) -> ListLookup:
    lookup = {}
    for li in project_lists:
        for nd in li.nodes:
            lookup[(li.list_name, nd.name)] = nd.iri
            lookup[("", nd.iri)] = nd.iri
    return ListLookup(lookup)


def _get_project_specific_information_from_api(auth: AuthenticationClient, shortcode: str) -> ProjectDataFromApi:
    list_client = ListClient(auth.server, shortcode)
    all_lists = list_client.get_lists()
    enabled_licenses = _get_license_iris(shortcode, auth)
    return ProjectDataFromApi(all_lists, enabled_licenses)


def _make_data_graph_from_parsed_resources(
    parsed_resources: list[ParsedResource], authorship_lookup: dict[str, list[str]], list_lookup: ListLookup
) -> Graph:
    rdf_like_data = get_rdf_like_data(parsed_resources, authorship_lookup, list_lookup)
    rdf_data = make_data_graph(rdf_like_data)
    return rdf_data


def _create_graphs(
    data_rdf: Graph,
    shortcode: str,
    auth: AuthenticationClient,
    proj_info: ProjectDataFromApi,
    permission_ids: list[str],
) -> RDFGraphs:
    logger.debug("Create all graphs.")
    onto_client = OntologyClient(auth.server, shortcode)
    ontologies, onto_iris = _get_project_ontos(onto_client)
    knora_ttl = onto_client.get_knora_api()
    knora_api = Graph()
    knora_api.parse(data=knora_ttl, format="ttl")
    shapes = construct_shapes_graphs(ontologies, knora_api, proj_info, permission_ids)
    api_shapes = Graph()
    api_shapes_path = importlib.resources.files("dsp_tools").joinpath("resources/validate_data/api-shapes.ttl")
    api_shapes.parse(str(api_shapes_path))
    api_card_shapes = Graph()
    api_card_path = importlib.resources.files("dsp_tools").joinpath(
        "resources/validate_data/api-shapes-resource-cardinalities.ttl"
    )
    api_card_shapes.parse(str(api_card_path))
    content_shapes = shapes.content + api_shapes
    card_shapes = shapes.cardinality + api_card_shapes
    data_rdf = _bind_prefixes_to_graph(data_rdf, onto_iris)
    ontologies = _bind_prefixes_to_graph(ontologies, onto_iris)
    card_shapes = _bind_prefixes_to_graph(card_shapes, onto_iris)
    content_shapes = _bind_prefixes_to_graph(content_shapes, onto_iris)
    knora_api = _bind_prefixes_to_graph(knora_api, onto_iris)
    return RDFGraphs(
        data=data_rdf,
        ontos=ontologies,
        cardinality_shapes=card_shapes,
        content_shapes=content_shapes,
        knora_api=knora_api,
    )


def _bind_prefixes_to_graph(g: Graph, project_ontos: list[str]) -> Graph:
    def get_one_prefix(ontology_iri: str) -> str:
        iri_split = ontology_iri.split("/")
        return iri_split[-2]

    g.bind("knora-api", "http://api.knora.org/ontology/knora-api/v2#")
    g.bind("api-shapes", "http://api.knora.org/ontology/knora-api/shapes/v2#")
    g.bind("dash", "http://datashapes.org/dash#")
    g.bind("salsah-gui", "http://api.knora.org/ontology/salsah-gui/v2#")
    for iri in project_ontos:
        g.bind(get_one_prefix(iri), f"{iri}#")
    return g


def _get_project_ontos(onto_client: OntologyClient) -> tuple[Graph, list[str]]:
    logger.debug("Get project ontologies from server.")
    all_ontos, onto_iris = onto_client.get_ontologies()
    onto_g = Graph()
    for onto in all_ontos:
        og = Graph()
        og.parse(data=onto, format="ttl")
        onto_g += og
    return onto_g, onto_iris


def _get_license_iris(shortcode: str, auth: AuthenticationClient) -> EnabledLicenseIris:
    legal_client = LegalInfoClientLive(auth.server, shortcode, auth)
    license_info = legal_client.get_licenses_of_a_project()
    iris = [x["id"] for x in license_info]
    return EnabledLicenseIris(iris)
