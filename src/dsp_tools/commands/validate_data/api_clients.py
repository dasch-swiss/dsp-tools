from dataclasses import dataclass
from typing import Any
from typing import cast
from urllib.parse import quote_plus

import requests
from loguru import logger
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.models.api_responses import AllProjectLists
from dsp_tools.commands.validate_data.models.api_responses import OneList
from dsp_tools.commands.validate_data.models.api_responses import SHACLValidationReport
from dsp_tools.models.exceptions import InternalError
from dsp_tools.models.exceptions import UserError


@dataclass
class OntologyConnection:
    api_con: ApiConnection
    shortcode: str

    def get_knora_api(self) -> str:
        response = self.api_con.get_with_endpoint(endpoint="ontology/knora-api/v2#", headers={"Accept": "text/turtle"})
        if not response.ok:
            msg = f"NON-OK RESPONSE | Code: {response.status_code} | Message: {response.text}"
            logger.error(msg)
            raise InternalError(msg)
        return response.text

    def get_ontologies(self) -> list[str]:
        """
        Returns a list of project ontologies as a string in turtle format.

        Returns:
            list of ontologies
        """
        ontology_iris = self._get_ontology_iris()
        return [self._get_one_ontology(x) for x in ontology_iris]

    def _get_ontology_iris(self) -> list[str]:
        response = self.api_con.get_with_endpoint(endpoint=f"admin/projects/shortcode/{self.shortcode}")
        if not response.ok:
            msg = f"NON-OK RESPONSE | Code: {response.status_code} | Message: {response.text}"
            logger.error(msg)
            raise InternalError(msg)
        response_json = cast(dict[str, Any], response.json())
        msg = f"The response from the API does not contain any ontologies.\nAPI response:{response.text}"
        if not (proj := response_json.get("project")):
            logger.exception(msg)
            raise UserError(msg)
        if not (ontos := proj.get("ontologies")):
            logger.exception(msg)
            raise UserError(msg)
        output = cast(list[str], ontos)
        return output

    def _get_one_ontology(self, ontology_iri: str) -> str:
        response = self.api_con.get_with_url(url=ontology_iri, headers={"Accept": "text/turtle"})
        if not response.ok:
            msg = f"NON-OK RESPONSE | Code: {response.status_code} | Message: {response.text}"
            logger.error(msg)
            raise InternalError(msg)
        return response.text


@dataclass
class ListConnection:
    """Client to request and reformat the lists of a project."""

    api_con: ApiConnection
    shortcode: str

    def get_lists(self) -> AllProjectLists:
        list_json = self._get_all_list_iris()
        all_iris = self._extract_list_iris(list_json)
        all_lists = [self._get_one_list(iri) for iri in all_iris]
        reformatted = [self._reformat_one_list(lst) for lst in all_lists]
        return AllProjectLists(reformatted)

    def _get_all_list_iris(self) -> dict[str, Any]:
        response = self.api_con.get_with_endpoint(endpoint=f"admin/lists?{self.shortcode}")
        if not response.ok:
            msg = f"NON-OK RESPONSE | Code: {response.status_code} | Message: {response.text}"
            logger.error(msg)
            raise InternalError(msg)
        json_response = cast(dict[str, Any], response.json())
        return json_response

    def _extract_list_iris(self, response_json: dict[str, Any]) -> list[str]:
        return [x["id"] for x in response_json["lists"]]

    def _get_one_list(self, list_iri: str) -> dict[str, Any]:
        encoded_list_iri = quote_plus(list_iri)
        response = self.api_con.get_with_endpoint(endpoint=f"admin/lists/{encoded_list_iri}")
        if not response.ok:
            msg = f"NON-OK RESPONSE | Code: {response.status_code} | Message: {response.text}"
            logger.error(msg)
            raise InternalError(msg)
        response_json = cast(dict[str, Any], response.json())
        return response_json

    def _reformat_one_list(self, response_json: dict[str, Any]) -> OneList:
        list_name = response_json["list"]["listinfo"]["name"]
        list_id = response_json["list"]["listinfo"]["id"]
        nodes = response_json["list"]["children"]
        all_nodes = []
        for child in nodes:
            all_nodes.append(child["name"])
            if node_child := child.get("children"):
                all_nodes.extend(self._reformat_children(node_child, all_nodes))
        return OneList(list_iri=list_id, list_name=list_name, nodes=all_nodes)

    def _reformat_children(self, list_child: list[dict[str, Any]], current_nodes: list[str]) -> list[str]:
        for child in list_child:
            current_nodes.append(child["name"])
            if grand_child := child.get("children"):
                self._reformat_children(grand_child, current_nodes)
        return current_nodes


@dataclass
class ShaclValidator:
    """Client to validate RDF data against a given SHACL shape."""

    api_url: str

    def validate(self, data_ttl: str, shacl_ttl: str) -> SHACLValidationReport:
        """
        Sends a multipart/form-data request with two turtle files (data.ttl and shacl.ttl) to the given URL
        and expects a response containing a single text/turtle body which is loaded into an rdflib Graph.

        Args:
            data_ttl (str): The turtle content for the data.ttl file (as a string).
            shacl_ttl (str): The turtle content for the shacl.ttl file (as a string).

        Returns:
            SHACLValidationReport: A report containing the validation graph and a bool to indicate if it passed.

        Raises:
            InternalError: in case of a non-ok response
        """
        response = self._request_validation_result(data_ttl, shacl_ttl)
        if not response.ok:
            msg = f"Failed to send request. Status code: {response.status_code}, Original Message:\n{response.text}"
            logger.error(msg)
            raise InternalError(msg)
        return self._parse_validation_result(response.text)

    def _request_validation_result(self, data_ttl: str, shacl_ttl: str) -> requests.Response:
        files = {
            "data.ttl": ("data.ttl", data_ttl, "text/turtle"),
            "shacl.ttl": ("shacl.ttl", shacl_ttl, "text/turtle"),
        }
        timeout = 10
        request_url = f"{self.api_url}/shacl/validate"
        logger.debug(f"REQUEST: POST to {request_url}, timeout: {timeout}")
        return requests.post(request_url, files=files, timeout=timeout)

    def _parse_validation_result(self, response_text: str) -> SHACLValidationReport:
        graph = Graph()
        graph.parse(data=response_text, format="turtle")
        conforms = bool(next(graph.objects(None, SH.conforms)))
        return SHACLValidationReport(conforms=conforms, validation_graph=graph)
