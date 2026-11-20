from dataclasses import dataclass

from dsp_vre_lib.clients import AssetClient
from dsp_vre_lib.clients import LegalInfoClient
from dsp_vre_lib.clients.list_client import ListGetClient


@dataclass(frozen=True)
class UploadClients:
    """Holds all the clients needed for the upload process."""

    asset_client: AssetClient
    list_client: ListGetClient
    legal_info_client: LegalInfoClient
