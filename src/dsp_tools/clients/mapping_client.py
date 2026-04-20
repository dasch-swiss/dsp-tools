from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.utils.request_utils import ResponseCodeAndText


class MappingClient(Protocol):
    server: str
    auth: AuthenticationClient

    def put_class_mapping(self, class_iri: str, mapping_iris: list[str]) -> None | ResponseCodeAndText:
        """PUT mapping for a class. Returns None on success, ResponseCodeAndText otherwise."""

    def put_property_mapping(self, property_iri: str, mapping_iris: list[str]) -> None | ResponseCodeAndText:
        """PUT mapping for a property. Returns None on success, ResponseCodeAndText otherwise."""
