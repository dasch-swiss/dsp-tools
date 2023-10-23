from typing import Protocol

from dsp_tools.xml_upload.domain.model.resource import Resource


class DspUploadRepo(Protocol):
    def create_resource(self, resource: Resource) -> None:
        ...
