from dataclasses import dataclass
from typing import Any
from typing import cast
from urllib.parse import quote_plus

import requests
from loguru import logger
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.models.api_responses import OneList
from dsp_tools.commands.validate_data.models.api_responses import OneNode
from dsp_tools.commands.validate_data.models.api_responses import SHACLValidationReport
from dsp_tools.commands.validate_data.models.validation import RDFGraphStrings
from dsp_tools.error.exceptions import InternalError
from dsp_tools.utils.request_utils import PostFile
from dsp_tools.utils.request_utils import PostFiles
from dsp_tools.utils.request_utils import RequestParameters
from dsp_tools.utils.request_utils import log_request
from dsp_tools.utils.request_utils import log_response


@dataclass
class OntologyClient:
    api_url: str
    shortcode: str

    def get_knora_api(self) -> str:
        url = f"{self.api_url}/ontology/knora-api/v2#"
        headers = {"Accept": "text/turtle"}
        timeout = 60
        log_request(RequestParameters("GET", url, timeout=timeout, headers=headers))
        response = requests.get(url=url, headers=headers, timeout=timeout)
        log_response(response, include_response_content=False)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        return response.text

    def get_ontologies(self) -> tuple[list[str], list[str]]:
        """
        Returns a list of project ontologies as a string in turtle format.
        And a list of the ontology IRIs

        Returns:
            list of ontologies and IRIs
        """
        ontology_iris = self._get_ontology_iris()
        ontologies = [self._get_one_ontology(x) for x in ontology_iris]
        return ontologies, ontology_iris

    def _get_ontology_iris(self) -> list[str]:
        url = f"{self.api_url}/admin/projects/shortcode/{self.shortcode}"
        timeout = 10
        log_request(RequestParameters("GET", url, timeout=timeout))
        response = requests.get(url=url, timeout=timeout)
        log_response(response)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        response_json = cast(dict[str, Any], response.json())
        if not (ontos := response_json.get("project", {}).get("ontologies")):
            raise InternalError(f"The response from the API does not contain any ontologies.\nResponse:{response.text}")
        output = cast(list[str], ontos)
        return output

    def _get_one_ontology(self, ontology_iri: str) -> str:
        url = ontology_iri
        headers = {"Accept": "text/turtle"}
        timeout = 30
        log_request(RequestParameters("GET", url, timeout=timeout, headers=headers))
        response = requests.get(url=url, headers=headers, timeout=timeout)
        log_response(response, include_response_content=False)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        return response.text


@dataclass
class ListClient:
    """Client to request and reformat the lists of a project."""

    api_url: str
    shortcode: str

    def get_lists(self) -> list[OneList]:
        list_json = self._get_all_list_iris()
        all_iris = self._extract_list_iris(list_json)
        all_lists = [self._get_one_list(iri) for iri in all_iris]
        return [self._reformat_one_list(lst) for lst in all_lists]

    def _get_all_list_iris(self) -> dict[str, Any]:
        url = f"{self.api_url}/admin/lists?projectShortcode={self.shortcode}"
        timeout = 10
        log_request(RequestParameters("GET", url, timeout))
        response = requests.get(url=url, timeout=timeout)
        log_response(response)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        json_response = cast(dict[str, Any], response.json())
        return json_response

    def _extract_list_iris(self, response_json: dict[str, Any]) -> list[str]:
        return [x["id"] for x in response_json["lists"]]

    def _get_one_list(self, list_iri: str) -> dict[str, Any]:
        encoded_list_iri = quote_plus(list_iri)
        url = f"{self.api_url}/admin/lists/{encoded_list_iri}"
        timeout = 30
        log_request(RequestParameters("GET", url, timeout))
        response = requests.get(url=url, timeout=timeout)
        log_response(response, include_response_content=False)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        response_json = cast(dict[str, Any], response.json())
        return response_json

    def _reformat_one_list(self, response_json: dict[str, Any]) -> OneList:
        list_name = response_json["list"]["listinfo"]["name"]
        list_id = response_json["list"]["listinfo"]["id"]
        nodes = response_json["list"]["children"]
        all_nodes = []
        for child in nodes:
            all_nodes.append(OneNode(child["name"], child["id"]))
            if node_child := child.get("children"):
                self._reformat_children(node_child, all_nodes)
        return OneList(list_iri=list_id, list_name=list_name, nodes=all_nodes)

    def _reformat_children(self, list_child: list[dict[str, Any]], current_nodes: list[OneNode]) -> None:
        for child in list_child:
            current_nodes.append(OneNode(child["name"], child["id"]))
            if grand_child := child.get("children"):
                self._reformat_children(grand_child, current_nodes)


@dataclass
class ShaclValidator:
    """Client to validate RDF data against a given SHACL shape."""

    api_url: str

    def validate(self, graph_strings: RDFGraphStrings) -> SHACLValidationReport:
        """
        Sends a multipart/form-data request with two turtle files (data.ttl and shacl.ttl) to the given URL
        and expects a response containing a single text/turtle body which is loaded into an rdflib Graph.

        Args:
            graph_strings: Graphs in RDF form that should be validated

        Returns:
            SHACLValidationReport: A report containing the validation graph and a bool to indicate if it passed.

        Raises:
            InternalError: in case of a non-ok response
        """
        result_graph = Graph()
        conforms = True

        card_result = self._validate_cardinality(graph_strings)
        if not card_result.conforms:
            result_graph += card_result.validation_graph
            conforms = False

        content_result = self._validate_content(graph_strings)
        if not content_result.conforms:
            result_graph += content_result.validation_graph
            conforms = False

        return SHACLValidationReport(conforms=conforms, validation_graph=result_graph)

    def validate_ontology(self, onto_graph: Graph, onto_shacl: Graph) -> SHACLValidationReport:
        logger.debug("Validating the ontology.")
        post_files = self._prepare_validation_files_for_request(
            onto_graph.serialize(format="ttl"), onto_shacl.serialize(format="ttl")
        )
        url = f"{self.api_url}/shacl/validate"
        timeout = 360
        log_request(RequestParameters("POST", url, timeout, files=post_files))
        response = requests.post(url=url, files=post_files.to_dict(), timeout=timeout)
        log_response(response, include_response_content=False)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        return self._parse_validation_result(response.text)

    def _validate_cardinality(self, graph_strings: RDFGraphStrings) -> SHACLValidationReport:
        logger.debug("Validate Cardinality")
        card_files = self._prepare_validation_files_for_request(
            graph_strings.cardinality_validation_data, graph_strings.cardinality_shapes
        )
        url = f"{self.api_url}/shacl/validate"
        timeout = 360
        log_request(RequestParameters("POST", url, timeout, files=card_files))
        response = requests.post(url=url, files=card_files.to_dict(), timeout=timeout)
        log_response(response, include_response_content=False)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        return self._parse_validation_result(response.text)

    def _validate_content(self, graph_strings: RDFGraphStrings) -> SHACLValidationReport:
        logger.debug("Validate Content")
        content_files = self._prepare_validation_files_for_request(
            graph_strings.content_validation_data, graph_strings.content_shapes
        )
        url = f"{self.api_url}/shacl/validate"
        timeout = 360
        log_request(RequestParameters("POST", url, timeout, files=content_files))
        response = requests.post(url=url, files=content_files.to_dict(), timeout=timeout)
        log_response(response, include_response_content=False)
        if not response.ok:
            raise InternalError(f"Failed Request: {response.status_code} {response.text}")
        return self._parse_validation_result(response.text)

    @staticmethod
    def _prepare_validation_files_for_request(data_str: str, shacl_str: str) -> PostFiles:
        shacl_file = PostFile(file_name="shacl.ttl", fileobj=shacl_str, content_type="text/turtle")
        data_file = PostFile(file_name="data.ttl", fileobj=data_str, content_type="text/turtle")
        return PostFiles([shacl_file, data_file])

    def _parse_validation_result(self, response_text: str) -> SHACLValidationReport:
        logger.debug("Parse validation response from API.")
        graph = Graph()
        graph.parse(data=response_text, format="turtle")
        conforms = bool(next(graph.objects(None, SH.conforms)))
        return SHACLValidationReport(conforms=conforms, validation_graph=graph)
