from dataclasses import dataclass

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig


@dataclass(frozen=True)
class UploadState:
    """
    Save the state of an xmlupload, so that after an interruption, it can be resumed.
    """

    pending_resources: list[XMLResource]
    failed_uploads: list[str]
    iri_resolver_lookup: dict[str, str]
    pending_stash: Stash | None
    config: UploadConfig
    permissions_lookup: dict[str, Permissions]
