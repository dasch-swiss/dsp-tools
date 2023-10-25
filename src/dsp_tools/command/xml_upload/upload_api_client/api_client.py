from typing import Protocol

from dsp_tools.command.xml_upload.models.resource import InputResource


class DspUploadRepo(Protocol):
    def create_resource(self, resource: InputResource) -> None:
        ...
