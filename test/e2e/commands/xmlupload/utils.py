import json
import urllib.parse

import requests
from rdflib import RDFS
from rdflib import Graph
from rdflib import Literal

from dsp_tools.utils.rdflib_constants import SubjectObjectTypeAlias


def _util_request_resources_by_class(resclass_iri: str, auth_header: dict[str, str], project_iri: str, creds) -> Graph:
    resclass_iri_encoded = urllib.parse.quote_plus(resclass_iri)
    get_resources_route = f"{creds.server}/v2/resources?resourceClass={resclass_iri_encoded}&page=0"
    headers = auth_header | {"X-Knora-Accept-Project": project_iri}
    response = requests.get(get_resources_route, timeout=3, headers=headers).json()
    resources = json.dumps(response)
    g = Graph()
    g.parse(data=resources, format="json-ld")
    return g


def _util_get_res_iri_from_label(g: Graph, label_str: str) -> SubjectObjectTypeAlias:
    return next(g.subjects(RDFS.label, Literal(label_str)))
