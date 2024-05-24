from dataclasses import dataclass
from dataclasses import field

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig


@dataclass
class UploadState:
    """
    Save the state of an xmlupload, so that after an interruption, it can be resumed.
    """

    pending_resources: list[XMLResource]
    pending_stash: Stash | None
    config: UploadConfig
    permissions_lookup: dict[str, Permissions]
    failed_uploads: list[str] = field(default_factory=list)
    iri_resolver: IriResolver = field(default_factory=IriResolver)
