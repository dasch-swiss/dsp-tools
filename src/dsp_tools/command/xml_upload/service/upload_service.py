from typing import Protocol

from dsp_tools.command.xml_upload.models.resource import InputResourceCollection
from dsp_tools.command.xml_upload.models.upload_result import UploadResult


class UploadService(Protocol):
    def upload_resources(
        self,
        resources: InputResourceCollection,
    ) -> UploadResult:
        ...
