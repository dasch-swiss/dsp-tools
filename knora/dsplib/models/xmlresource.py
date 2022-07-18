from typing import Optional, Union

from lxml import etree

from knora.dsplib.models.xmlbitstream import XMLBitstream
from knora.dsplib.models.helpers import BaseError
from knora.dsplib.models.permission import Permissions
from knora.dsplib.models.value import KnoraStandoffXml
from knora.dsplib.models.xmlproperty import XMLProperty


class XMLResource:
    """Represents a resource in the XML used for data import"""

    _id: str
    _iri: Optional[str]
    _ark: Optional[str]
    _label: str
    _restype: str
    _permissions: Optional[str]
    _bitstream: Optional[XMLBitstream]
    _properties: list[XMLProperty]

    def __init__(self, node: etree.Element, default_ontology: str) -> None:
        """
        Constructor that parses a resource node from the XML DOM

        Args:
            node: The DOM node to be processed representing a resource (which is a child of the knora element)
            default_ontology: The default ontology (given in the attribute default-ontology of the knora element)

        Returns:
            None
        """
        self._id = node.attrib['id']
        self._iri = node.attrib.get('iri')
        self._ark = node.attrib.get('ark')
        self._label = node.attrib['label']
        # get the resource type which is in format namespace:resourcetype, p.ex. rosetta:Image
        tmp_res_type = node.attrib['restype'].split(':')
        if len(tmp_res_type) > 1:
            if tmp_res_type[0]:
                self._restype = node.attrib['restype']
            else:
                # replace an empty namespace with the default ontology name
                self._restype = default_ontology + ':' + tmp_res_type[1]
        else:
            self._restype = 'knora-api:' + tmp_res_type[0]
        self._permissions = node.attrib.get("permissions")
        self._bitstream = None
        self._properties = []
        for subnode in node:
            if subnode.tag is etree.Comment:
                continue
            elif subnode.tag == 'bitstream':
                self._bitstream = XMLBitstream(subnode)
            else:
                # get the property type which is in format type-prop, p.ex. <decimal-prop>
                prop_type, _ = subnode.tag.split('-')
                self._properties.append(XMLProperty(subnode, prop_type, default_ontology))

    @property
    def id(self) -> str:
        """The unique id of the resource"""
        return self._id

    @property
    def iri(self) -> Optional[str]:
        """The custom IRI of the resource"""
        return self._iri

    @property
    def ark(self) -> Optional[str]:
        """The custom ARK of the resource"""
        return self._ark

    @property
    def label(self) -> str:
        """The label of the resource"""
        return self._label

    @property
    def restype(self) -> str:
        """The type of the resource"""
        return self._restype

    @property
    def permissions(self) -> Optional[str]:
        """The reference to the permissions set for this resource"""
        return self._permissions

    @property
    def bitstream(self) -> Optional[XMLBitstream]:
        """The bitstream object belonging to the resource"""
        return self._bitstream

    @property
    def properties(self) -> list[XMLProperty]:
        return self._properties

    @properties.setter
    def properties(self, new_properties: list[XMLProperty]) -> None:
        self._properties = new_properties

    def print(self) -> None:
        """Prints the resource and its attributes."""
        print(f'Resource: id={self._id}, restype: {self._restype}, label: {self._label}')
        if self._bitstream:
            print('  Bitstream: ' + self._bitstream.value)
        for prop in self._properties:
            prop.print()

    def get_props_with_links(self) -> list[XMLProperty]:
        """
        Get a list of all XMLProperties that have an outgoing link to another resource, be it a resptr-prop link
        or a standoff link in a text.
        """
        link_properties: list[XMLProperty] = []
        for prop in self._properties:
            if prop.valtype == 'resptr':
                link_properties.append(prop)
            elif prop.valtype == 'text':
                for value in prop.values:
                    if value.resrefs:
                        link_properties.append(prop)
                        break
        return link_properties

    def get_resptrs(self) -> list[str]:
        """
        Get a list of all resource id's that are referenced by this resource

        Returns:
            List of resources identified by their unique id's (as given in the XML)
        """
        resptrs: list[str] = []
        for prop in self._properties:
            if prop.valtype == 'resptr':
                for value in prop.values:
                    resptrs.append(str(value.value))
            elif prop.valtype == 'text':
                for value in prop.values:
                    if value.resrefs:
                        resptrs.extend(value.resrefs)
        return resptrs

    def get_propvals(
        self,
        resiri_lookup: dict[str, str],
        permissions_lookup: dict[str, Permissions]
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
        for prop in self._properties:
            vals: list[Union[str, dict[str, str]]] = []
            for value in prop.values:
                if prop.valtype == 'resptr':  # we have a resptr, therefore simple lookup or IRI
                    iri = resiri_lookup.get(value.value)
                    if iri:
                        v = iri
                    else:
                        v = value.value  # if we do not find the id, we assume it's a valid DSP IRI
                elif prop.valtype == 'text':
                    if isinstance(value.value, KnoraStandoffXml):
                        iri_refs = value.value.get_all_iris()
                        for iri_ref in iri_refs:
                            res_id = iri_ref.split(':')[1]
                            iri = resiri_lookup.get(res_id)
                            if not iri:
                                raise BaseError(f'Resource cannot be created, because it contains a salsah-Link to '
                                                f'the following invalid resource: {res_id}.')
                            value.value.replace(iri_ref, iri)
                    v = value.value
                else:
                    v = value.value

                if value.comment is None and value.permissions is None:
                    # no comment or permissions
                    vals.append(v)
                else:
                    # we have comment or permissions
                    tmp = {'value': v}
                    if value.comment:
                        tmp['comment'] = value.comment
                    if value.permissions:
                        tmp['permissions'] = permissions_lookup.get(value.permissions)
                    vals.append(tmp)
            prop_data[prop.name] = vals if len(vals) > 1 else vals[0]
        return prop_data

    def get_bitstream(self, internal_file_name_bitstream: str, permissions_lookup: dict[str, Permissions]) -> Optional[dict[str, Union[str, Permissions]]]:
        """
        Get the bitstream object belonging to the resource

        Args:
            internal_file_name_bitstream: Internal file name of bitstream object as returned from Sipi
            permissions_lookup: Is used to resolve the permission id's to permission sets

        Returns:
            A dict of the bitstream object
        """
        tmp = None
        if self._bitstream:
            bitstream = self._bitstream
            tmp = {'value': bitstream.value, 'internal_file_name': internal_file_name_bitstream}
            if bitstream.permissions:
                tmp['permissions'] = permissions_lookup.get(bitstream.permissions)
        return tmp
