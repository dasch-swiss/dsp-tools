# mypy: disable-error-code="no-untyped-def"

import json
import urllib.parse

import requests
from rdflib import RDFS
from rdflib import Graph
from rdflib import Literal

from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias


def util_request_resources_by_class(resclass_iri: str, auth_header: dict[str, str], project_iri: str, creds) -> Graph:
    all_resources = Graph()
    for i in range(100):
        g = _get_single_graph_from_api(resclass_iri, auth_header, project_iri, creds, i)
        all_resources += g
        if not list(g.triples((None, KNORA_API.mayHaveMoreResults, None))):
            break
    return all_resources


def _get_single_graph_from_api(resclass_iri: str, auth_header: dict[str, str], project_iri: str, creds, offset: int):
    resclass_iri_encoded = urllib.parse.quote_plus(resclass_iri)
    get_resources_route = f"{creds.server}/v2/resources?resourceClass={resclass_iri_encoded}&page={offset}"
    headers = auth_header | {"X-Knora-Accept-Project": project_iri}
    response = requests.get(get_resources_route, timeout=3, headers=headers).json()
    resources = json.dumps(response)
    returned_g = Graph()
    returned_g.parse(data=resources, format="json-ld")
    return returned_g


def util_get_res_iri_from_label(g: Graph, label_str: str) -> SubjectObjectTypeAlias:
    return next(g.subjects(RDFS.label, Literal(label_str)))
