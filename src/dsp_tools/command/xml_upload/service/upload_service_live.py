from dataclasses import dataclass

from dsp_tools.command.xml_upload.models.resource import InputResource
from dsp_tools.command.xml_upload.models.upload_result import UploadResult
from dsp_tools.command.xml_upload.upload_api_client.api_client import DspUploadRepo
from dsp_tools.utils.xmlupload.upload_config import UploadConfig

# XXX: do we really need this "service"?

# XXX: should not use input resources but processed resources


@dataclass(frozen=True)
class UploadServiceLive:
    repo: DspUploadRepo
    config: UploadConfig

    def upload_resources(
        self,
        resources: list[InputResource],
    ) -> UploadResult:
        for res in resources:
            self.repo.create_resource(res)
        return UploadResult(
            id_to_iri_mapping={},
            not_uploaded_resources=[],
        )
