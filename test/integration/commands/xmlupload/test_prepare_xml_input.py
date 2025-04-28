from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.commands.xmlupload.models.ingest import AssetClient
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.prepare_xml_input.list_client import ListClientLive
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_processed_resources_for_upload
from dsp_tools.commands.xmlupload.project_client import ProjectClient
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file
from test.integration.commands.xmlupload.connection_mock import ConnectionMockBase


@dataclass
class ConnectionMock(ConnectionMockBase):
    get_responses: list[dict[str, Any]]

    def get(
        self,
        route: str,  # noqa: ARG002 (unused-method-argument)
        headers: dict[str, str] | None = None,  # noqa: ARG002 (unused-method-argument)
    ) -> dict[str, Any]:
        return self.get_responses.pop(0)


def test_get_processed_resources_for_upload():
    list_iris = {"lists": [{"id": "http://rdfh.ch/lists/0001/list1"}]}
    list_a = {
        "list": {
            "listinfo": {
                "id": "http://rdfh.ch/lists/0001/list1",
                "name": "list1",
            },
            "children": [
                {
                    "id": "http://rdfh.ch/lists/0001/list1_node1",
                    "name": "list1_node1",
                }
            ],
        }
    }
    con = ConnectionMock([list_iris, list_a])
    list_client = ListClientLive(con, "")
    clients = UploadClients(AssetClient(), ProjectClient(), list_client, LegalInfoClient())
    xml_root = parse_and_clean_xml_file(Path("testdata/xml-data/test-list-iri-reference.xml"))
    result = get_processed_resources_for_upload(xml_root, clients)
    assert len(result) == 2
