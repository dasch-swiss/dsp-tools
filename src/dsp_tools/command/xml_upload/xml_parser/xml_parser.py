from typing import Protocol

from dsp_tools.command.xml_upload.models.resource import InputResourceCollection


class XmlParser(Protocol):
    """Interface (protocol) for XML parsers."""

    def get_resources(self) -> InputResourceCollection:
        """Get a collection of resources from the XML file."""
