from typing import Protocol

from dsp_tools.xml_upload.domain.model.resource import InputResourceCollection
from dsp_tools.xml_upload.domain.model.upload_result import UploadResult


class UploadService(Protocol):
    def upload_resources(
        self,
        resources: InputResourceCollection,
    ) -> UploadResult:
        ...
