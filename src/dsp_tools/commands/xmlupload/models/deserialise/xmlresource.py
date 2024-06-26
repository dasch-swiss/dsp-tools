from dataclasses import dataclass
from typing import Optional

from lxml import etree

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import IIIFUriInfo
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLBitstream
from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.models.datetimestamp import DateTimeStamp


@dataclass(frozen=True)
class BitstreamInfo:
    """
    Represents a bitstream object,
    consisting of its file name on the local file system,
    the internal file name assigned by the ingest service
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
    iiif_uri: Optional[IIIFUriInfo]
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
                self.restype = f"{default_ontology}:{tmp_res_type[1]}"
        else:
            self.restype = f"knora-api:{tmp_res_type[0]}"
        self.permissions = node.attrib.get("permissions")
        self.bitstream = None
        self.iiif_uri = None
        self.properties = []
        for subnode in node:
            match subnode.tag:
                case "bitstream":
                    self.bitstream = XMLBitstream(subnode)
                case "iiif-uri":
                    self.iiif_uri = IIIFUriInfo(subnode)
                case _:
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
