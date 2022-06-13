"""
This module handles the import of XML data into the DSP platform.
"""
import base64
import json
import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, cast, Tuple, Any
from urllib.parse import quote_plus
from lxml import etree
from requests import RequestException

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.group import Group
from knora.dsplib.models.helpers import BaseError
from knora.dsplib.models.permission import Permissions
from knora.dsplib.models.project import Project
from knora.dsplib.models.resource import ResourceInstanceFactory, ResourceInstance, KnoraStandoffXmlEncoder
from knora.dsplib.models.sipi import Sipi
from knora.dsplib.models.value import KnoraStandoffXml


class XmlError(BaseException):
    """Represents an error raised in the context of the XML import"""
    _message: str

    def __init__(self, msg: str):
        self._message = msg

    def __str__(self) -> str:
        return 'XML-ERROR: ' + self._message


class ProjectContext:
    """Represents the project context"""

    _projects: list[Project]
    _project_map: dict[str, str]  # dictionary of (project name:project IRI) pairs
    _inv_project_map: dict[str, str]  # dictionary of (project IRI:project name) pairs
    _groups: Optional[list[Group]]
    _group_map: Optional[dict[str, str]]
    _shortcode: Optional[str]
    _project_name: Optional[str]

    def __init__(self, con: Connection, shortcode: Optional[str] = None):
        self._shortcode = shortcode
        self._projects = Project.getAllProjects(con=con)
        self._project_map: dict[str, str] = {x.shortname: x.id for x in self._projects}
        self._inv_project_map: dict[str, str] = {x.id: x.shortname for x in self._projects}
        try:
            self._groups = Group.getAllGroups(con=con)
        except BaseError:
            self._groups = None
        if self._groups:
            self._group_map: dict[str, str] = {self._inv_project_map[x.project] + ':' + x.name: x.id for x in
                                               self._groups}
        else:
            self._group_map = None
        self._project_name = None
        # get the project name from the shortcode
        if self._shortcode:
            for p in self._projects:
                if p.shortcode == self._shortcode:
                    self._project_name = p.shortname
                    break

    @property
    def group_map(self) -> dict[str, str]:
        """Dictionary of (project:group name) and (group id) pairs of all groups in project"""
        return self._group_map

    @property
    def project_name(self) -> Optional[str]:
        """Name of the project"""
        return self._project_name


class XMLBitstream:
    """Represents a bitstream object (file) of a resource in the XML used for data import"""

    _value: str
    _permissions: str

    def __init__(self, node: etree.Element) -> None:
        self._value = node.text
        self._permissions = node.get('permissions')

    @property
    def value(self) -> str:
        """The file path of the bitstream object"""
        return self._value

    @property
    def permissions(self) -> str:
        """Reference to the set of permissions for the bitstream object"""
        return self._permissions

    def print(self) -> None:
        """Prints the bitstream object and its attributes."""
        print('   Bitstream file path: ' + str(self._value))


class XMLValue:
    """Represents a value of a resource property in the XML used for data import"""

    _value: Union[str, KnoraStandoffXml]
    _resrefs: Optional[list[str]]
    _comment: str
    _permissions: str
    _is_richtext: bool

    def __init__(self, node: etree.Element, val_type: str, listname: Optional[str] = None) -> None:

        self._resrefs = None
        self._comment = node.get('comment')
        self._permissions = node.get('permissions')
        if node.get('encoding') == 'xml':
            node.attrib.clear()
            xmlstr = etree.tostring(node, encoding="unicode", method="xml")
            xmlstr = xmlstr.replace('<text xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">', '')
            xmlstr = xmlstr.replace('</text>', '')
            self._value = KnoraStandoffXml(xmlstr)
            tmp_id_list = self._value.get_all_iris()
            if tmp_id_list:
                refs = set()
                for tmp_id in tmp_id_list:
                    refs.add(tmp_id.split(':')[1])
                self._resrefs = list(refs)
        else:
            if val_type == 'list':
                self._value = listname + ':' + "".join(node.itertext())
            else:
                self._value = "".join(node.itertext())

    @property
    def value(self) -> Union[str, KnoraStandoffXml]:
        """The actual value of the value instance"""
        return self._value

    @value.setter
    def value(self, value: Union[str, KnoraStandoffXml]) -> None:
        self._value = value

    @property
    def resrefs(self) -> Optional[list[str]]:
        """List of resource references"""
        return self._resrefs

    @resrefs.setter
    def resrefs(self, resrefs: Optional[list[str]]) -> None:
        self._resrefs = resrefs

    @property
    def comment(self) -> str:
        """Comment about the value"""
        return self._comment

    @property
    def permissions(self) -> str:
        """Reference to the set of permissions for the value"""
        return self._permissions

    @property
    def is_richtext(self) -> bool:
        """true if text value is of type richtext, false otherwise"""
        return self._is_richtext

    def print(self) -> None:
        """Prints the value and its attributes."""
        print('   Value: ' + str(self._value))
        if self._comment:
            print('   Comment:' + self._comment)
        if self._resrefs is not None:
            for i in self._resrefs:
                print('   res_ref: ' + i)


class XMLProperty:
    """Represents a property of a resource in the XML used for data import"""

    _name: str
    _valtype: str
    _values: list[XMLValue]

    def __init__(self, node: etree.Element, valtype: str, default_ontology: Optional[str] = None):
        """
        The constructor for the DSP property

        Args:
            node: the property node, p.ex. <decimal-prop></decimal-prop>
            valtype: the type of value given by the name of the property node, p.ex. decimal in <decimal-prop>
            default_ontology: the name of the ontology
        """
        # get the property name which is in format namespace:propertyname, p.ex. rosetta:hasName
        tmp_prop_name = node.attrib['name'].split(':')
        if len(tmp_prop_name) > 1:
            if tmp_prop_name[0]:
                self._name = node.attrib['name']
            else:
                # replace an empty namespace with the default ontology name
                self._name = default_ontology + ':' + tmp_prop_name[1]
        else:
            self._name = 'knora-admin:' + tmp_prop_name[0]
        listname = node.attrib.get('list')  # safe the list name if given (only for lists)
        self._valtype = valtype
        self._values = []

        # parse the subnodes of the property nodes which contain the actual values of the property
        for subnode in node:
            if subnode.tag == valtype:  # the subnode must correspond to the expected value type
                self._values.append(XMLValue(subnode, valtype, listname))
            else:
                raise XmlError(f"ERROR Unexpected tag: '{subnode.tag}'. Property may contain only value tags!")

    @property
    def name(self) -> str:
        """The name of the property"""
        return self._name

    @property
    def valtype(self) -> str:
        """The value type of the property"""
        return self._valtype

    @property
    def values(self) -> list[XMLValue]:
        """List of values of this property"""
        return self._values

    def print(self) -> None:
        """Prints the property."""
        print('  Property: {} Type: {}'.format(self._name, self._valtype))
        for value in self._values:
            value.print()


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

    def __init__(self, node: etree.Element, default_ontology: Optional[str] = None) -> None:
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
            self._restype = 'knora-admin:' + tmp_res_type[0]
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


class XmlAllow:
    """Represents the allow element of the XML used for data import"""

    _group: str
    _permission: str

    def __init__(self, node: etree.Element, project_context: ProjectContext) -> None:
        """
        Constructor which parses the XML DOM allow element

        Args:
            node: The DOM node to be processed (represents a single right in a permission set)
            project_context: Context for DOM node traversal

        Returns:
            None
        """
        tmp = node.attrib['group'].split(':')
        sysgroups = ['UnknownUser', 'KnownUser', 'ProjectMember', 'Creator', 'ProjectAdmin', 'SystemAdmin']
        if len(tmp) > 1:
            if tmp[0]:
                if tmp[0] == 'knora-admin' and tmp[1] in sysgroups:
                    self._group = node.attrib['group']
                else:
                    self._group = project_context.group_map.get(node.attrib['group'])
                    if self._group is None:
                        raise XmlError("Group \"{}\" is not known: Cannot find project!".format(node.attrib['group']))
            else:
                if project_context.project_name is None:
                    raise XmlError("Project shortcode has not been set in ProjectContext")
                self._group = project_context.project_name + ':' + tmp[1]
        else:
            if tmp[0] in sysgroups:
                self._group = 'knora-admin:' + node.attrib['group']
            else:
                raise XmlError("Group \"{}\" is not known: ".format(node.attrib['group']))
        self._permission = node.text

    @property
    def group(self) -> str:
        """The group specified in the allow element"""
        return self._group

    @property
    def permission(self) -> str:
        """The reference to a set of permissions"""
        return self._permission

    def print(self) -> None:
        """Prints the attributes of the XmlAllow instance"""
        print("  group=", self._group, " permission=", self._permission)


class XmlPermission:
    """Represents the permission set containing several XmlAllow elements in the XML used for data import"""

    _id: str
    _allows: list[XmlAllow]

    def __init__(self, node: etree.Element, project_context: ProjectContext) -> None:
        """
        Constructor which parses a XML DOM permissions element representing an named permission set

        Args:
            node: The DOM node to be processed (representing an a permission set)
            project_context: Context for DOM node traversal
        """
        self._allows = []
        self._id = node.attrib['id']
        for allow_node in node:
            self._allows.append(XmlAllow(allow_node, project_context))

    @property
    def id(self) -> str:
        """The id of the permission set, p.ex. res-default"""
        return self._id

    @property
    def allows(self) -> list[XmlAllow]:
        """List of XmlAllow elements defining permissions for specific groups"""
        return self._allows

    def get_permission_instance(self) -> Permissions:
        """Returns a list of allow elements of this permission instance"""
        permissions = Permissions()
        for allow in self._allows:
            permissions.add(allow.permission, allow.group)
        return permissions

    def __str__(self) -> str:
        allow_str: list[str] = []
        for allow in self._allows:
            allow_str.append("{} {}".format(allow.permission, allow.group))
        return '|'.join(allow_str)

    def print(self) -> None:
        """Prints the permission set"""
        print('Permission: ', self._id)
        for a in self._allows:
            a.print()


def remove_circular_references(resources: list[XMLResource], verbose: bool) -> \
        tuple[list[XMLResource],
              dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
              dict[XMLResource, dict[XMLProperty, list[str]]]
              ]:
    """
    Temporarily removes problematic resource-references from a list of resources. A reference is problematic if
    it creates a circle (circular references).

    Args:
        resources: list of resources that possibly contain circular references
        verbose: verbose output if True

    Returns:
        list: list of cleaned resources
        stashed_xml_texts: dict with the stashed XML texts
        stashed_resptr_props: dict with the stashed resptr-props
    """

    if verbose:
        print("Checking resources for unresolvable references...")

    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]] = {}
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]] = {}

    # sort the resources according to outgoing resptrs
    ok_resources: list[XMLResource] = []
    nok_resources: list[XMLResource] = []
    ok_res_ids: list[str] = []
    cnt = 0
    nok_len = 9999999
    while len(resources) > 0 and cnt < 10000:
        for resource in resources:
            resptrs = resource.get_resptrs()
            if len(resptrs) == 0:
                ok_resources.append(resource)
                ok_res_ids.append(resource.id)
            else:
                ok = True
                for resptr in resptrs:
                    if resptr not in ok_res_ids:
                        ok = False
                if ok:
                    ok_resources.append(resource)
                    ok_res_ids.append(resource.id)
                else:
                    nok_resources.append(resource)
        resources = nok_resources
        if len(nok_resources) == nok_len:
            # there are circular references. go through all problematic resources, and stash the problematic references.
            nok_resources, ok_res_ids, ok_resources, stashed_xml_texts, stashed_resptr_props = stash_circular_references(
                nok_resources,
                ok_res_ids,
                ok_resources,
                stashed_xml_texts,
                stashed_resptr_props
            )
        nok_len = len(nok_resources)
        nok_resources = []
        cnt += 1
        if verbose:
            print(f'{cnt}. ordering pass finished.')
    return ok_resources, stashed_xml_texts, stashed_resptr_props


def stash_circular_references(
    nok_resources: list[XMLResource],
    ok_res_ids: list[str],
    ok_resources: list[XMLResource],
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]]
) -> Tuple[
    list[XMLResource],
    list[str],
    list[XMLResource],
    dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    dict[XMLResource, dict[XMLProperty, list[str]]]
]:
    for res in nok_resources.copy():
        for link_prop in res.get_props_with_links():
            if link_prop.valtype == 'text':
                for value in link_prop.values:
                    if value.resrefs and not all([_id in ok_res_ids for _id in value.resrefs]):
                        # stash this XML text, replace it by its hash, and remove the
                        # problematic resrefs from the XMLValue's resrefs list
                        value_hash = str(hash(f'{value.value}{datetime.now()}'))
                        if res not in stashed_xml_texts:
                            stashed_xml_texts[res] = {link_prop: {value_hash: cast(KnoraStandoffXml, value.value)}}
                        elif link_prop not in stashed_xml_texts[res]:
                            stashed_xml_texts[res][link_prop] = {value_hash: cast(KnoraStandoffXml, value.value)}
                        else:
                            stashed_xml_texts[res][link_prop][value_hash] = cast(KnoraStandoffXml, value.value)
                        value.value = KnoraStandoffXml(value_hash)
                        value.resrefs = [_id for _id in value.resrefs if _id in ok_res_ids]
            elif link_prop.valtype == 'resptr':
                for value in link_prop.values.copy():
                    if value.value not in ok_res_ids:
                        # value.value is the id of the target resource. stash it, then delete it
                        if res not in stashed_resptr_props:
                            stashed_resptr_props[res] = {}
                            stashed_resptr_props[res][link_prop] = [str(value.value)]
                        else:
                            if link_prop not in stashed_resptr_props[res]:
                                stashed_resptr_props[res][link_prop] = [str(value.value)]
                            else:
                                stashed_resptr_props[res][link_prop].append(str(value.value))
                        link_prop.values.remove(value)
            else:
                raise BaseError(f'ERROR in remove_circular_references(): link_prop.valtype is '
                                f'neither text nor resptr.')

            if len(link_prop.values) == 0:
                # if all values of a link property have been stashed, the property needs to be removed
                res.properties.remove(link_prop)

        ok_resources.append(res)
        ok_res_ids.append(res.id)
        nok_resources.remove(res)

    return nok_resources, ok_res_ids, ok_resources, stashed_xml_texts, stashed_resptr_props


def validate_xml_against_schema(input_file: str, schema_file: str) -> bool:
    """
    Validates an XML file against an XSD schema

    Args:
        input_file: the XML file to be validated
        schema_file: the schema against which the XML file should be validated

    Returns:
        True if the XML file is valid, False otherwise
    """
    xmlschema = etree.XMLSchema(etree.parse(schema_file))
    doc = etree.parse(input_file)

    if xmlschema.validate(doc):
        return True
    else:
        print("The input data file cannot be uploaded due to the following validation error(s):")
        for error in xmlschema.error_log:
            print(f"  Line {error.line}: {error.message}")
        return False


def convert_ark_v0_to_resource_iri(ark: str) -> str:
    """
    Converts an ARK URL from salsah.org (ARK version 0) of the form ark:/72163/080c-779b9990a0c3f-6e to a DSP resource
    IRI of the form http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q

    This method is needed for the migration of projects from salsah.org to DSP. Resources need to be created with an
    existing ARK, so the IRI needs to be extracted from that ARK in order for the ARK URL to be still valid after the
    migration.

    Args:
        ark: an ARK version 0 of the form ark:/72163/080c-779b9990a0c3f-6e, '72163' being the Name Assigning Authority
        number, '080c' being the project shortcode, '779b9990a0c3f' being an ID derived from the object's Salsah ID and
        '6e' being check digits

    Returns:
        Resource IRI (str) of the form http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q
    """
    # create the DaSCH namespace to create version 5 UUIDs
    generic_namespace_url = uuid.NAMESPACE_URL
    dasch_uuid_ns = uuid.uuid5(generic_namespace_url, "https://dasch.swiss")  # cace8b00-717e-50d5-bcb9-486f39d733a2

    # get the salsah resource ID from the ARK and convert it to a UUID version 5 (base64 encoded)
    if ark.count("-") != 2:
        raise BaseError(f"while converting ARK '{ark}'. The ARK seems to be invalid")
    project_id, resource_id, _ = ark.split("-")
    _, project_id = project_id.rsplit("/", 1)
    project_id = project_id.upper()
    if not re.match("^[0-9a-fA-F]{4}$", project_id):
        raise BaseError(f"while converting ARK '{ark}'. Invalid project shortcode '{project_id}'")
    if not re.match("^[0-9A-Za-z]+$", resource_id):
        raise BaseError(f"while converting ARK '{ark}'. Invalid Salsah ID '{resource_id}'")

    # make a UUID v5 from the namespace created above (which is a UUID itself) and the resource ID and encode it to base64
    dsp_uuid = base64.urlsafe_b64encode(uuid.uuid5(dasch_uuid_ns, resource_id).bytes).decode("utf-8")
    dsp_uuid = dsp_uuid[:-2]

    # use the new UUID to create the resource IRI
    return "http://rdfh.ch/" + project_id + "/" + dsp_uuid


def xml_upload(input_file: str, server: str, user: str, password: str, imgdir: str, sipi: str, verbose: bool,
               validate_only: bool, incremental: bool) -> None:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: the XML with the data to be imported onto the DSP server
        server: the DSP server where the data should be imported
        user: the user (e-mail) with which the data should be imported
        password: the password of the user with which the data should be imported
        imgdir: the image directory
        sipi: the sipi instance to be used
        verbose: verbose option for the command, if used more output is given to the user
        validate_only: validation option to validate the XML data without the actual import of the data
        incremental: if set, IRIs instead of internal IDs are expected as resource pointers

    Returns:
        None
    """

    # Validate the input XML file
    current_dir = os.path.dirname(os.path.realpath(__file__))
    schema_file = os.path.join(current_dir, '../schemas/data.xsd')
    if validate_xml_against_schema(input_file, schema_file):
        print("The input data file is syntactically correct and passed validation.")
        if validate_only:
            exit(0)
    else:
        print("ERROR The input data file did not pass validation.")
        exit(1)

    # Connect to the DaSCH Service Platform API and get the project context
    con = Connection(server)
    con.login(user, password)
    proj_context = ProjectContext(con=con)
    sipi_server = Sipi(sipi, con.get_token())

    # parse the XML file
    tree = etree.parse(input_file)
    for elem in tree.getiterator():
        if not (isinstance(elem, etree._Comment) or isinstance(elem, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname  # remove namespace URI in the element's name
    etree.cleanup_namespaces(tree)  # remove unused namespace declarations

    knora = tree.getroot()
    default_ontology = knora.attrib['default-ontology']
    shortcode = knora.attrib['shortcode']

    resources: list[XMLResource] = []
    permissions: dict[str, XmlPermission] = {}
    for child in knora:
        if child.tag == "permissions":
            permission = XmlPermission(child, proj_context)
            permissions[permission.id] = permission
        elif child.tag == "resource":
            resources.append(XMLResource(child, default_ontology))

    # get the project information and project ontology from the server
    project = ResourceInstanceFactory(con, shortcode)
    permissions_lookup: dict[str, Permissions] = {s: perm.get_permission_instance() for s, perm in permissions.items()}
    resclass_name_2_type: dict[str, type] = {s: project.get_resclass_type(s) for s in project.get_resclass_names()}

    # temporarily remove circular references, but only if not an incremental upload
    if not incremental:
        resources, stashed_xml_texts, stashed_resptr_props = remove_circular_references(resources, verbose)
    else:
        stashed_xml_texts = dict()
        stashed_resptr_props = dict()

    id2iri_mapping: dict[str, str] = {}
    failed_uploads: list[str] = []

    try:
        id2iri_mapping, failed_uploads = upload_resources(verbose, resources, imgdir, sipi_server, permissions_lookup,
                                                          resclass_name_2_type, id2iri_mapping, con, failed_uploads)
    except BaseException as err:
        handle_upload_error(err, input_file, id2iri_mapping, failed_uploads, stashed_xml_texts, stashed_resptr_props)

    # update the resources with the stashed XML texts
    nonapplied_xml_texts = {}
    if len(stashed_xml_texts) > 0:
        try:
            nonapplied_xml_texts = upload_stashed_xml_texts(verbose, id2iri_mapping, con, stashed_xml_texts)
        except BaseException as err:
            handle_upload_error(err, input_file, id2iri_mapping, failed_uploads, stashed_xml_texts, stashed_resptr_props)

    # update the resources with the stashed resptrs
    nonapplied_resptr_props = {}
    if len(stashed_resptr_props) > 0:
        try:
            nonapplied_resptr_props = upload_stashed_resptr_props(verbose, id2iri_mapping, con, stashed_resptr_props)
        except BaseException as err:
            handle_upload_error(err, input_file, id2iri_mapping, failed_uploads, stashed_xml_texts, stashed_resptr_props)

    # write log files
    exit_code = 0
    timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    write_id2iri_mapping(input_file, id2iri_mapping, timestamp_str)
    if len(nonapplied_xml_texts) > 0:
        write_stashed_xml_texts(nonapplied_xml_texts, timestamp_str)
        exit_code = 1
    if len(nonapplied_resptr_props) > 0:
        write_stashed_resptr_props(nonapplied_resptr_props, timestamp_str)
        exit_code = 1

    if failed_uploads:
        print(f"Could not upload the following resources: {failed_uploads}")
        exit_code = 1

    exit(exit_code)


def _try_sipi_upload(sipi_server: Sipi, filepath: str) -> dict[Any, Any]:
    """
    Wrapper around sipi_server.upload_bitstream(filepath), that handles errors and retries in case of connectivity
    issues.

    Args:
        sipi_server: Sipi instance
        filepath: file to upload

    Returns:
        response from DSP
    """

    for _ in range(5):
        try:
            return sipi_server.upload_bitstream(filepath)
        except ConnectionError:
            print(f'{datetime.now().isoformat()}: Try reconnecting to SIPI...')
            time.sleep(1)
            continue
        except RequestException:
            print(f'{datetime.now().isoformat()}: Try reconnecting to SIPI...')
            time.sleep(1)
            continue
    raise BaseError(f'Cannot upload "{filepath}" to SIPI')


def upload_resources(
    verbose: bool,
    resources: list[XMLResource],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    resclass_name_2_type: dict[str, type],
    id2iri_mapping: dict[str, str],
    con: Connection,
    failed_uploads: list[str]
) -> tuple[dict[str, str], list[str]]:
    """
    Iterates through all resources and tries to upload them to DSP

    Args:
        verbose: bool
        resources: list of XMLResources to upload to DSP
        imgdir: folder containing the multimedia files
        sipi_server: Sipi instance
        permissions_lookup: maps permission strings to Permission objects
        resclass_name_2_type: maps resource class names to their types
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP (initially empty, gets filled during the upload)
        con: connection to DSP
        failed_uploads: ids of resources that could not be uploaded (initially empty, gets filled during the upload)

    Returns:
        id2iri_mapping, failed_uploads: These two arguments are modified during the upload
    """

    for resource in resources:
        if verbose:
            resource.print()

        resource_iri = resource.iri
        if resource.ark:
            resource_iri = convert_ark_v0_to_resource_iri(resource.ark)

        # in case of a multimedia resource: upload the multimedia file
        resource_bitstream = None
        if resource.bitstream:
            try:
                img = _try_sipi_upload(sipi_server=sipi_server, filepath=os.path.join(imgdir, resource.bitstream.value))
                internal_file_name_bitstream = img['uploadedFiles'][0]['internalFilename']
                resource_bitstream = resource.get_bitstream(internal_file_name_bitstream, permissions_lookup)
            except BaseError:
                print(f"ERROR while trying to create resource '{resource.label}' ({resource.id}). ")
                failed_uploads.append(resource.id)
                continue

        permissions_tmp = permissions_lookup.get(resource.permissions)

        # create the resource in DSP
        resclass_instance: ResourceInstance = None
        for _ in range(5):
            try:
                resclass_type = resclass_name_2_type[resource.restype]
                properties = resource.get_propvals(id2iri_mapping, permissions_lookup)
                resclass_instance = resclass_type(
                    con=con,
                    label=resource.label,
                    iri=resource_iri,
                    permissions=permissions_tmp,
                    bitstream=resource_bitstream,
                    values=properties
                )
                resclass_instance = resclass_instance.create()
                break
            except ConnectionError:
                print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server...')
                time.sleep(1)
                continue
            except RequestException:
                print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server...')
                time.sleep(1)
                continue
            except BaseError:
                break

        if not resclass_instance or not resclass_instance.iri:
            print(f"ERROR while trying to create resource '{resource.label}' ({resource.id}). ")
            failed_uploads.append(resource.id)
        else:
            id2iri_mapping[resource.id] = resclass_instance.iri
            print(f"Created resource '{resclass_instance.label}' ({resource.id}) with IRI '{resclass_instance.iri}'")

    return id2iri_mapping, failed_uploads


def upload_stashed_xml_texts(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]
) -> dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]:
    """
    After all resources are uploaded, the stashed xml texts must be applied to their resources in DSP.

    Args:
        verbose: bool
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        con: connection to DSP
        stashed_xml_texts: all xml texts that have been stashed

    Returns:
        nonapplied_xml_texts: the xml texts that could not be uploaded
    """

    print('Update the stashed XML texts...')
    for resource, link_props in stashed_xml_texts.copy().items():
        print(f'Update XML text(s) of resource "{resource.id}"...')
        res_iri = id2iri_mapping[resource.id]
        existing_resource = con.get(path=f'/v2/resources/{quote_plus(res_iri)}')
        for link_prop, hash_to_value in link_props.items():
            existing_values = existing_resource[link_prop.name]
            if not isinstance(existing_values, list):
                existing_values = [existing_values, ]
            for existing_value in existing_values:
                old_xmltext = existing_value.get("knora-api:textValueAsXml")
                if not old_xmltext:
                    continue

                # strip all xml tags from the old xmltext, so that the pure text itself remains
                pure_text = re.sub(r'(<\?xml.+>\s*)?<text>\s*(.+)\s*<\/text>', r'\2', old_xmltext)

                # if the pure text is a hash, the replacement must be made. This hash originates from
                # stash_circular_references(), and identifies the XML texts
                if pure_text not in hash_to_value:
                    continue
                new_xmltext = hash_to_value[pure_text]

                # replace the outdated internal ids by their IRI
                for _id, _iri in id2iri_mapping.items():
                    new_xmltext.regex_replace(f'href="IRI:{_id}:IRI"', f'href="{_iri}"')

                # prepare API call
                jsonobj = {
                    "@id": res_iri,
                    "@type": resource.restype,
                    link_prop.name: {
                        "@id": existing_value['@id'],
                        "@type": "knora-api:TextValue",
                        "knora-api:textValueAsXml": new_xmltext,
                        "knora-api:textValueHasMapping": {
                            '@id': 'http://rdfh.ch/standoff/mappings/StandardMapping'
                        }
                    },
                    "@context": existing_resource['@context']
                }
                jsondata = json.dumps(jsonobj, indent=4, separators=(',', ': '), cls=KnoraStandoffXmlEncoder)

                # execute API call
                response = None
                for _ in range(5):
                    try:
                        response = con.put(path='/v2/values', jsondata=jsondata)
                        stashed_xml_texts[resource][link_prop].pop(pure_text)
                        break
                    except ConnectionError:
                        print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server...')
                        time.sleep(1)
                        continue
                    except RequestException:
                        print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server...')
                        time.sleep(1)
                        continue
                    except BaseError:
                        print(f'ERROR while updating the xml text of "{link_prop.name}" of resource "{resource.id}"')
                        break
                if verbose:
                    if response:
                        print(f'  Successfully updated xml text of "{link_prop.name}"\n')

    # make a purged version of stashed_xml_texts, without empty entries
    nonapplied_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]] = {}
    for res, propdict in stashed_xml_texts.items():
        for prop, xmldict in propdict.items():
            if len(xmldict) > 0:
                if res not in nonapplied_xml_texts:
                    nonapplied_xml_texts[res] = {}
                nonapplied_xml_texts[res][prop] = xmldict

    return nonapplied_xml_texts


def upload_stashed_resptr_props(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]]
) -> dict[XMLResource, dict[XMLProperty, list[str]]]:
    """
    After all resources are uploaded, the stashed resptr props must be applied to their resources in DSP.

    Args:
        verbose: bool
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        con: connection to DSP
        stashed_resptr_props: all resptr props that have been stashed

    Returns:
        nonapplied_resptr_props: the resptr props that could not be uploaded
    """

    print('Update the stashed resptrs...')
    for resource, prop_2_resptrs in stashed_resptr_props.copy().items():
        print(f'Update resptrs of resource "{resource.id}"...')
        res_iri = id2iri_mapping[resource.id]
        existing_resource = con.get(path=f'/v2/resources/{quote_plus(res_iri)}')
        for link_prop, resptrs in prop_2_resptrs.items():
            for resptr in resptrs.copy():
                jsonobj = {
                    '@id': res_iri,
                    '@type': resource.restype,
                    f'{link_prop.name}Value': {
                        '@type': 'knora-api:LinkValue',
                        'knora-api:linkValueHasTargetIri': {
                            '@id': id2iri_mapping[resptr]
                        }
                    },
                    '@context': existing_resource['@context']
                }
                jsondata = json.dumps(jsonobj, indent=4, separators=(',', ': '))
                response = None
                for _ in range(5):
                    try:
                        response = con.post(path='/v2/values', jsondata=jsondata)
                        stashed_resptr_props[resource][link_prop].remove(resptr)
                        break
                    except ConnectionError:
                        print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server...')
                        time.sleep(1)
                        continue
                    except RequestException:
                        print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server...')
                        time.sleep(1)
                        continue
                    except BaseError:
                        print(f'ERROR while updating the resptr prop of "{link_prop.name}" of resource "{resource.id}"')
                        break
                if verbose:
                    if response:
                        print(f'  Successfully updated resptr-prop of "{link_prop.name}"\n'
                              f'    Value: {resptr}')

    # make a purged version of stashed_resptr_props, without empty entries
    nonapplied_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]] = {}
    for res, propdict in stashed_resptr_props.items():
        for prop, resptrs in propdict.items():
            if len(resptrs) > 0:
                if res not in nonapplied_resptr_props:
                    nonapplied_resptr_props[res] = {}
                nonapplied_resptr_props[res][prop] = resptrs

    return nonapplied_resptr_props


def handle_upload_error(
    err: BaseException,
    input_file: str,
    id2iri_mapping: dict[str, str],
    failed_uploads: list[str],
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]]
) -> None:
    """
    In case the xmlupload must be interrupted, e.g. because of an error that could not be handled, or due to keyboard
    interrupt, this method ensures that all information about what is already in DSP is written into log files.

    It then re-raises the original error.

    Args:
        err: error that was the cause of the abort
        input_file: file name of the original XML file
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP (only successful uploads appear here)
        failed_uploads: resources that caused an error when uploading to DSP
        stashed_xml_texts: all xml texts that have been stashed
        stashed_resptr_props: all resptr props that have been stashed

    Returns:
        None
    """

    print('xmlupload must be aborted because of an error')
    timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")

    # write id2iri_mapping of the resources that are already in DSP
    write_id2iri_mapping(input_file, id2iri_mapping, timestamp_str)

    # Both stashes are purged from resources that have not been uploaded yet. Only stashed properties of resources that
    # already exist in DSP are of interest.
    stashed_xml_texts = {res: propdict for res, propdict in stashed_xml_texts.items() if res.id in id2iri_mapping}
    if len(stashed_xml_texts) > 0:
        write_stashed_xml_texts(stashed_xml_texts, timestamp_str)
    stashed_resptr_props = {res: propdict for res, propdict in stashed_resptr_props.items() if res.id in id2iri_mapping}
    if len(stashed_resptr_props) > 0:
        write_stashed_resptr_props(stashed_resptr_props, timestamp_str)

    # print the resources that threw an error when they were tried to be uploaded
    if failed_uploads:
        print(f"Independently of this error, there were some resources that could not be uploaded: "
              f"{failed_uploads}")

    raise err


def write_id2iri_mapping(input_file: str, id2iri_mapping: dict[str, str], timestamp_str: str) -> None:
    """
    Write the id2iri mapping into a file. The timestamp must be created by the caller, so that different log files can
    have an identical time stamp.

    Args:
        input_file: the file name of the original XML file
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        timestamp_str: timestamp for log file identification

    Returns:
        None
    """

    id2iri_mapping_file = "id2iri_" + Path(input_file).stem + "_mapping_" + timestamp_str + ".json"
    with open(id2iri_mapping_file, "w") as outfile:
        print(f"============\nThe mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")
        outfile.write(json.dumps(id2iri_mapping))


def write_stashed_xml_texts(
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    timestamp_str: str
) -> None:
    """
    Write the stashed_xml_texts into a file. The timestamp must be created by the caller, so that different log files
    can have an identical time stamp.

    Args:
        stashed_xml_texts: all xml texts that have been stashed
        timestamp_str: timestamp for log file identification

    Returns:
        None
    """

    filename = f'stashed_xml_texts_{timestamp_str}.txt'
    print(f'There are stashed xml texts that could not be reapplied. They were saved to {filename}')
    with open(filename, 'a') as f:
        f.write('Stashed XML texts that could not be reapplied\n')
        f.write('*********************************************\n')
        for res, props in stashed_xml_texts.items():
            f.write(f'\n{res.id}\n---------\n')
            for prop, stashed_texts in props.items():
                f.write(f'{prop.name}\n')
                for i, standoff in enumerate(stashed_texts.values()):
                    f.write(f'\t{i}. text: {standoff}')


def write_stashed_resptr_props(
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
    timestamp_str: str
) -> None:
    """
    Write the stashed_resptr_props into a file. The timestamp must be created by the caller, so that different log files
    can have an identical time stamp.

    Args:
        stashed_resptr_props: all resptr props that have been stashed
        timestamp_str: timestamp for log file identification

    Returns:
        None
    """

    filename = f'stashed_resptr_props_{timestamp_str}.txt'
    print(f'There are stashed resptr props that could not be reapplied. They were saved to {filename}')
    with open(filename, 'a') as f:
        f.write('Stashed resptr props that could not be reapplied\n')
        f.write('************************************************\n')
        for res, props_ in stashed_resptr_props.items():
            f.write(f'\n{res.id}\n---------\n')
            for prop, stashed_props in props_.items():
                f.write(f'{prop.name}\n\t{stashed_props}\n')
