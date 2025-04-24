from dataclasses import dataclass
from dataclasses import field

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.upload_config import UploadConfig


@dataclass
class UploadState:
    """
    Save the state of an xmlupload, so that after an interruption, it can be resumed.
    """

    pending_resources: list[ProcessedResource]
    pending_stash: Stash | None
    config: UploadConfig
    failed_uploads: list[str] = field(default_factory=list)
    iri_resolver: IriResolver = field(default_factory=IriResolver)
