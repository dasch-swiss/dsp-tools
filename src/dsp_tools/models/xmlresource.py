from typing import Optional, Union

import regex
from lxml import etree

from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.helpers import DateTimeStamp
from dsp_tools.models.permission import Permissions
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlbitstream import XMLBitstream
from dsp_tools.models.xmlproperty import XMLProperty


class XMLResource:  # pylint: disable=too-many-instance-attributes
    """
    Represents a resource in the XML used for data import.

    Attributes:
        id: The unique id of the resource
        iri: The custom IRI of the resource
        ark: The custom ARK of the resource
        label: The label of the resource
        restype: The type of the resource
        permissions: The reference to the permissions set for this resource
        creation_date: The creation date of the resource
        bitstream: The bitstream object belonging to the resource
        properties: The list of properties of the resource
    """

    id: str
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
            node: The DOM node to be processed representing a resource (which is a child of the DSP element)
            default_ontology: The default ontology (given in the attribute default-ontology of the DSP element)

        Returns:
            None
        """
        self.id = node.attrib["id"]
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

    def get_resptrs(self) -> list[str]:
        """
        Get a list of all resource IDs/IRIs that are referenced by this resource.

        Returns:
            List of resources identified by their unique id's (as given in the XML)
        """
        resptrs: list[str] = []
        for prop in self.properties:
            if prop.valtype == "resptr":
                for value in prop.values:
                    resptrs.append(value.value)
            elif prop.valtype == "text":
                for value in prop.values:
                    if value.resrefs:
                        resptrs.extend(value.resrefs)
        return resptrs

    def get_internal_resptrs(self) -> set[str]:
        """
        Get a set of all resource IDs that are referenced by this resource by means of an internal ID.
        Returns:
            Set of resources identified by their unique id's (as given in the XML)
        """
        return {x for x in self.get_resptrs() if not regex.search(r"https?://rdfh.ch/[a-fA-F0-9]{4}/\w{22}", x)}

    def get_propvals(
        self,
        resiri_lookup: dict[str, str],
        permissions_lookup: dict[str, Permissions],
    ) -> dict[str, Union[list[Union[str, dict[str, str]]], str, dict[str, str]]]:
        """
        Get a dictionary of the property names and their values. Replace the internal ids by their IRI first.

        Args:
            resiri_lookup: Is used to solve internal unique id's of resources to real IRI's
            permissions_lookup: Is used to resolve the permission id's to permission sets

        Returns:
            A dict of values with the property name as key and a single value. This dict represents the JSON structure
            that Knora.create_resource() expects.
        """
        prop_data = {}
        for prop in self.properties:
            vals: list[Union[str, dict[str, str]]] = []
            for value in prop.values:
                if prop.valtype == "resptr":  # we have a resptr, therefore simple lookup or IRI
                    iri = resiri_lookup.get(value.value)
                    if iri:
                        v = iri
                    else:
                        v = value.value  # if we do not find the id, we assume it's a valid DSP IRI
                elif prop.valtype == "text":
                    if isinstance(value.value, KnoraStandoffXml):
                        iri_refs = value.value.get_all_iris()
                        for iri_ref in iri_refs or []:
                            res_id = iri_ref.split(":")[1]
                            iri = resiri_lookup.get(res_id)
                            if not iri:
                                raise BaseError(
                                    f"Resource '{self.id}' cannot be created, because it contains a salsah-Link to "
                                    f"the following invalid resource: '{res_id}'"
                                )
                            value.value.replace(iri_ref, iri)
                    v = value.value
                else:
                    v = value.value

                if value.comment is None and value.permissions is None:
                    # no comment or permissions
                    vals.append(v)
                else:
                    # we have comment or permissions
                    tmp = {"value": v}
                    if value.comment:
                        tmp["comment"] = value.comment
                    if value.permissions:
                        tmp["permissions"] = permissions_lookup.get(value.permissions)
                    vals.append(tmp)
            prop_data[prop.name] = vals if len(vals) > 1 else vals[0]
        return prop_data

    def get_bitstream_information(
        self, internal_file_name_bitstream: str, permissions_lookup: dict[str, Permissions]
    ) -> Optional[dict[str, Union[str, Permissions]]]:
        """
        Get the bitstream object belonging to the resource

        Args:
            internal_file_name_bitstream: Internal file name of bitstream object as returned from Sipi
            permissions_lookup: Is used to resolve the permission id's to permission sets

        Returns:
            A dict of the bitstream object
        """
        tmp: Optional[dict[str, Union[str, Permissions]]] = None
        if self.bitstream:
            bitstream = self.bitstream
            tmp = {"value": bitstream.value, "internal_file_name": internal_file_name_bitstream}
            if bitstream.permissions:
                permissions = permissions_lookup.get(bitstream.permissions)
                if permissions:
                    tmp["permissions"] = permissions
        return tmp
