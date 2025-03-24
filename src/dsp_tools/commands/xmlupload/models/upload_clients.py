from dataclasses import dataclass

from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.commands.xmlupload.models.ingest import AssetClient
from dsp_tools.commands.xmlupload.prepare_xml_input.list_client import ListClient
from dsp_tools.commands.xmlupload.project_client import ProjectClient


@dataclass(frozen=True)
class UploadClients:
    """Holds all the clients needed for the upload process."""

    asset_client: AssetClient
    project_client: ProjectClient
    list_client: ListClient
    legal_info_client: LegalInfoClient
