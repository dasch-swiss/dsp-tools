from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Protocol

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.xmlupload.models.lookup_models import ProjectLists
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import _get_list_info_from_server
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import _get_node_tuples


class ListClient(Protocol):
    """Interface (protocol) for list-related requests to the DSP-API."""

    con: Connection
    project_iri: str

    def get_list_node_id_to_iri_lookup(self) -> dict[tuple[str, str], str]:
        """Get a lookup of list node names to IRIs."""


@dataclass
class ListClientLive:
    """Client handling list-related requests to the DSP-API."""

    con: Connection
    project_iri: str
    list_info: ProjectLists | None = field(init=False, default=None)

    def get_list_node_id_to_iri_lookup(self) -> dict[tuple[str, str], str]:
        """
        Get a mapping of list node IDs to their respective IRIs.
        A list node ID is structured as follows:
        `("<list name>", "<node name>") where the list name is the node name of the root node.

        Returns:
            The mapping of list node IDs to IRIs.
        """
        if not self.list_info:
            self.list_info = _get_list_info_from_server(self.con, self.project_iri)
        lookup = dict(_get_node_tuples(self.list_info.lists))
        # Enable referencing list node IRIs in the XML:
        # add a reference of the list node IRIs to themselves (with empty list names)
        lookup.update({("", v): v for v in lookup.values()})
        return lookup
