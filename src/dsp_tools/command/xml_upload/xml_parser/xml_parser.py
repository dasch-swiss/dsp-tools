from __future__ import annotations

from typing import Protocol

from dsp_tools.command.xml_upload.models.resource import InputResource


class XmlParser(Protocol):
    """Interface (protocol) for XML parsers."""

    def get_resources(self) -> list[InputResource]:
        """Get a collection of resources from the XML file."""
