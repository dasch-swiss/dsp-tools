from dataclasses import dataclass

from dsp_tools.utils.xmlupload.upload_config import UploadConfig
from dsp_tools.xml_upload.domain.model.resource import InputResourceCollection
from dsp_tools.xml_upload.domain.model.upload_result import UploadResult
from dsp_tools.xml_upload.repo.dsp_upload_repo import DspUploadRepo


@dataclass(frozen=True)
class UploadServiceLive:
    repo: DspUploadRepo
    config: UploadConfig

    def upload_resources(
        self,
        resources: InputResourceCollection,
    ) -> UploadResult:
        for res in resources.resources:
            self.repo.create_resource(res)
        return UploadResult(
            id_to_iri_mapping={},
            not_uploaded_resources=[],
        )
