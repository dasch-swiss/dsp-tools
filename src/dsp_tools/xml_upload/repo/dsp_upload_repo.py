from typing import Protocol

from dsp_tools.xml_upload.domain.model.resource import InputResource


class DspUploadRepo(Protocol):
    def create_resource(self, resource: InputResource) -> None:
        ...
