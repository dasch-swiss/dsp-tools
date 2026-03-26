from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.utils.request_utils import ResponseCodeAndText


class MappingClient(Protocol):
    server: str
    auth: AuthenticationClient

    def add_class_mapping(
        self, ontology_iri: str, class_iri: str, external_iris: list[str]
    ) -> str | ResponseCodeAndText:
        """PUT mapping for a class. Returns the class IRI on success, ResponseCodeAndText otherwise."""

    def add_property_mapping(
        self, ontology_iri: str, property_iri: str, external_iris: list[str]
    ) -> str | ResponseCodeAndText:
        """PUT mapping for a property. Returns the property IRI on success, ResponseCodeAndText otherwise."""
