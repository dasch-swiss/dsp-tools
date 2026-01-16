from dataclasses import dataclass
from dataclasses import field
from typing import Any

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.legal_info_client import LegalInfoClient
from test.integration.commands.xmlupload.authentication_client_mock import AuthenticationClientMockBase


@dataclass
class LegalInfoClientMockBase(LegalInfoClient):
    server: str = "http://0.0.0.0:3333"
    project_shortcode: str = "9999"
    authentication_client: AuthenticationClient = field(default_factory=AuthenticationClientMockBase)

    def post_copyright_holders(self, copyright_holders: list[str]) -> None:
        pass

    def get_licenses_of_a_project(self, enabled_only: bool) -> list[dict[str, Any]]:  # noqa: ARG002
        return []

    def enable_unknown_license(self) -> None:
        pass
