from dataclasses import dataclass
from typing import Optional

from lxml import etree

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.xmlbitstream import XMLBitstream
from dsp_tools.commands.xmlupload.models.xmlproperty import XMLProperty
from dsp_tools.models.datetimestamp import DateTimeStamp


@dataclass(frozen=True)
class BitstreamInfo:
    """
    Represents a bitstream object,
    consisting of its file name on the local file system,
    the internal file name assigned by SIPI
    and optionally its permissions.
    """

    local_file: str
    internal_file_name: str
    permissions: Permissions | None = None


class XMLResource:
    """
    Represents a resource in the XML used for data import.

    Attributes:
        res_id: The unique id of the resource
        iri: The custom IRI of the resource
        ark: The custom ARK of the resource
        label: The label of the resource
        restype: The type of the resource
        permissions: The reference to the permissions set for this resource
        creation_date: The creation date of the resource
        bitstream: The bitstream object belonging to the resource
        properties: The list of properties of the resource
    """

    res_id: str
    iri: Optional[str]
    ark: Optional[str]
    label: str
    restype: str
    permissions: Optional[str]
    creation_date: Optional[DateTimeStamp]
    bitstream: Optional[XMLBitstream]
    properties: list[XMLProperty]

    def __init__(self, node: etree._Element, default_ontology: str) -> None:
        """
        Constructor that parses a resource node from the XML DOM

        Args:
            node: The DOM node to be processed representing a resource (which is a child of the <knora> element)
            default_ontology: The default ontology (given in the attribute default-ontology of the <knora> element)
        """
        self.res_id = node.attrib["id"]
        self.iri = node.attrib.get("iri")
        self.ark = node.attrib.get("ark")
        self.creation_date = None
        if node.attrib.get("creation_date"):
            self.creation_date = DateTimeStamp(node.attrib.get("creation_date"))
        self.label = node.attrib["label"]
        # get the resource type which is in format namespace:resourcetype, p.ex. rosetta:Image
        tmp_res_type = node.attrib["restype"].split(":")
        if len(tmp_res_type) > 1:
            if tmp_res_type[0]:
                self.restype = node.attrib["restype"]
            else:
                # replace an empty namespace with the default ontology name
                self.restype = default_ontology + ":" + tmp_res_type[1]
        else:
            self.restype = "knora-api:" + tmp_res_type[0]
        self.permissions = node.attrib.get("permissions")
        self.bitstream = None
        self.properties = []
        for subnode in node:
            if subnode.tag == "bitstream":
                self.bitstream = XMLBitstream(subnode)
            else:
                # get the property type which is in format type-prop, p.ex. <decimal-prop>
                prop_type, _ = subnode.tag.split("-")
                self.properties.append(XMLProperty(subnode, prop_type, default_ontology))

    def get_props_with_links(self) -> list[XMLProperty]:
        """
        Get a list of all XMLProperties that have an outgoing link to another resource, be it a resptr-prop link
        or a standoff link in a text.

        Returns:
            list of all XMLProperties
        """
        link_properties: list[XMLProperty] = []
        for prop in self.properties:
            if prop.valtype == "resptr":
                link_properties.append(prop)
            elif prop.valtype == "text":
                for value in prop.values:
                    if value.resrefs:
                        link_properties.append(prop)
                        break
        return link_properties

    def get_bitstream_information(
        self,
        internal_file_name_bitstream: str,
        permissions_lookup: dict[str, Permissions],
    ) -> BitstreamInfo | None:
        """
        This method constructs a `BitstreamInfo` object from the current resource,
        or None, if the resource does not have a bitstream representation.
        The `BitstreamInfo` object contains the local file name (relative to the imgdir directory),
        the internal file name assigned by SIPI
        and the permissions of the bitstream representation, if permissions are defined.

        Args:
            internal_file_name_bitstream: Internal file name of bitstream object as returned from Sipi
            permissions_lookup: Is used to resolve the permission id's to permission sets

        Returns:
            A BitstreamInfo object
        """
        if not self.bitstream:
            return None
        permissions = permissions_lookup.get(self.bitstream.permissions) if self.bitstream.permissions else None
        return BitstreamInfo(
            local_file=self.bitstream.value,
            internal_file_name=internal_file_name_bitstream,
            permissions=permissions,
        )
