"""
This module handles the import of XML data into the DSP platform.
"""
import base64
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from lxml import etree

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.group import Group
from knora.dsplib.models.helpers import BaseError
from knora.dsplib.models.permission import Permissions
from knora.dsplib.models.project import Project
from knora.dsplib.models.resource import ResourceInstanceFactory, ResourceInstance
from knora.dsplib.models.sipi import Sipi
from knora.dsplib.models.value import KnoraStandoffXml


class XmlError(BaseException):
    """Represents an error raised in the context of the XML import"""
    _message: str

    def __init__(self, msg: str):
        self._message = msg

    def __str__(self):
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
            tmp_id_list = self._value.findall()
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

    @property
    def resrefs(self) -> Optional[list[str]]:
        """List of resource references"""
        return self._resrefs

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
        The constructor for the knora property

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
    def iri(self) -> str:
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

    def print(self) -> None:
        """Prints the resource and its attributes."""
        print(f'Resource: id={self._id}, restype: {self._restype}, label: {self._label}')
        if self._bitstream:
            print('  Bitstream: ' + self._bitstream.value)
        for prop in self._properties:
            prop.print()

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
                    resptrs.append(value.value)
            elif prop.valtype == 'text':
                for value in prop.values:
                    if value.resrefs is not None:
                        resptrs.extend(value.resrefs)
        return resptrs

    def get_propvals(self, resiri_lookup: dict[str, str], permissions_lookup: dict[str, Permissions]) -> dict[str, Permissions]:
        """
        Get a dictionary of the property names and their values belonging to a resource

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
                        v = value.value  # if we do not find the id, we assume it's a valid knora IRI
                elif prop.valtype == 'text':
                    if isinstance(value.value, KnoraStandoffXml):
                        iri_refs = value.value.findall()
                        for iri_ref in iri_refs:
                            res_id = iri_ref.split(':')[1]
                            iri = resiri_lookup.get(res_id)
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

    def __str__(self):
        allow_str: list[str] = []
        for allow in self._allows:
            allow_str.append("{} {}".format(allow.permission, allow.group))
        return '|'.join(allow_str)

    def print(self):
        """Prints the permission set"""
        print('Permission: ', self._id)
        for a in self._allows:
            a.print()


def do_sort_order(resources: list[XMLResource], verbose) -> list[XMLResource]:
    """
    Sorts a list of resources.

    Resources that reference other resources are added after the referenced resources. The method will report circular
    references and exit with an error if there are any unresolvable references.

    Args:
        resources: list of resources to sort
        verbose: verbose output if True

    Returns:
        sorted list of resources
    """

    if verbose:
        print("Checking resources for unresolvable references...")

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
            print("ERROR Unable to resolve all resptr dependencies.")
            for res in nok_resources:
                unresolvable_resptrs = []
                for resptr_id in res.get_resptrs():
                    if resptr_id not in ok_res_ids:
                        unresolvable_resptrs.append(resptr_id)
                print(f"\tResource '{res.id}' has unresolvable resptrs to {unresolvable_resptrs}")
            exit(1)
        nok_len = len(nok_resources)
        nok_resources = []
        cnt += 1
        if verbose:
            print(f'{cnt}. ordering finished.')
    return ok_resources


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

    is_valid = False

    if xmlschema.validate(doc):
        is_valid = True

    return is_valid


def convert_ark_v0_to_resource_iri(ark: str) -> str:
    """
    Converts an ARK URL from salsah.org (ARK version 0) of the form ark:/72163/080c-779b9990a0c3f-6e to a DSP resource
    IRI of the form http://rdfh.ch/080C/fcb031cb-b01e-55b1-a7fb-bb259925d172

    This method is needed for the migration of projects from salsah.org to DSP. Resources need to be created with an
    existing ARK, so the IRI needs to be extracted from that ARK in order for the ARK URL to be still valid after the
    migration.

    Args:
        ark : an ARK version 0 of the form ark:/72163/080c-779b9990a0c3f-6e, '72163' being the Name Assigning Authority
        number, '080c' being the project shortcode, '779b9990a0c3f' being an ID derived from the object's Salsah ID and
        '6e' being check digits

    Returns:
        Resource IRI (str) of the form http://rdfh.ch/080C/fcb031cb-b01e-55b1-a7fb-bb259925d172
    """
    # create the DaSCH namespace to create version 5 UUIDs
    generic_namespace_url = uuid.NAMESPACE_URL
    dasch_uuid_ns = uuid.uuid5(generic_namespace_url, "https://dasch.swiss")  # cace8b00-717e-50d5-bcb9-486f39d733a2

    # get the salsah resource ID from the ARK and convert it to a UUID version 5
    if ark.count("-") != 2:
        raise BaseError(f"while converting ARK '{ark}'. The ARK seems to be invalid")
    project_id, resource_id, check_digits = ark.split("-")
    project_id = project_id.split("/")[-1]
    if not re.match("^[0-9aAbBcCdDeEfF]{4}$", project_id):
        raise BaseError(f"while converting ARK '{ark}'. Invalid project shortcode '{project_id}'")
    if not re.match("^[0-9A-Za-z]+$", resource_id):
        raise BaseError(f"while converting ARK '{ark}'. Invalid Salsah ID '{resource_id}'")

    dsp_uuid = base64.urlsafe_b64encode(uuid.uuid5(dasch_uuid_ns, resource_id).bytes).decode("utf-8")
    dsp_uuid = dsp_uuid[:-2]

    # use the new UUID to create the resource IRI
    return "http://rdfh.ch/" + project_id + "/" + dsp_uuid


def xml_upload(input_file: str, server: str, user: str, password: str, imgdir: str, sipi: str, verbose: bool,
               validate_only: bool, incremental: bool) -> None:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file : the XML with the data to be imported onto the DSP server
        server : the DSP server where the data should be imported
        user : the user (e-mail) with which the data should be imported
        password : the password of the user with which the data should be imported
        imgdir : the image directory
        sipi : the sipi instance to be used
        verbose : verbose option for the command, if used more output is given to the user
        validate_only : validation option to validate the XML data without the actual import of the data
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

    resources: list[XMLResource] = []
    permissions: dict[str, XmlPermission] = {}

    # parse the XML file containing the data
    tree = etree.parse(input_file)

    # Iterate through all XML elements
    for elem in tree.getiterator():
        # Skip comments and processing instructions,
        # because they do not have names
        if not (
            isinstance(elem, etree._Comment)
            or isinstance(elem, etree._ProcessingInstruction)
        ):
            # Remove a namespace URI in the element's name
            elem.tag = etree.QName(elem).localname

    # Remove unused namespace declarations
    etree.cleanup_namespaces(tree)

    knora = tree.getroot()
    default_ontology = knora.attrib['default-ontology']
    shortcode = knora.attrib['shortcode']

    for child in knora:
        # get all permissions
        if child.tag == "permissions":
            permission = XmlPermission(child, proj_context)
            permissions[permission.id] = permission
        # get all resources
        elif child.tag == "resource":
            resources.append(XMLResource(child, default_ontology))

    # sort the resources (resources which do not link to others come first) but only if not an incremental upload
    if not incremental:
        resources = do_sort_order(resources, verbose)

    sipi = Sipi(sipi, con.get_token())

    # get the project information and project ontology from the server
    project = ResourceInstanceFactory(con, shortcode)

    # create a dictionary to look up permissions
    permissions_lookup: dict[str, Permissions] = {}
    for key, perm in permissions.items():
        permissions_lookup[key] = perm.get_permission_instance()

    # create a dictionary to look up resource classes
    res_classes: dict[str, type] = {}
    for res_class_name in project.get_resclass_names():
        res_classes[res_class_name] = project.get_resclass(res_class_name)

    res_iri_lookup: dict[str, str] = {}

    failed_uploads = []
    for resource in resources:
        if verbose:
            resource.print()

        resource_iri = None
        if resource.ark:
            resource_iri = convert_ark_v0_to_resource_iri(resource.ark)

        resource_bitstream = None
        if resource.bitstream:
            img = sipi.upload_bitstream(os.path.join(imgdir, resource.bitstream.value))
            internal_file_name_bitstream = img['uploadedFiles'][0]['internalFilename']
            resource_bitstream = resource.get_bitstream(internal_file_name_bitstream, permissions_lookup)

        permissions_tmp = permissions_lookup.get(resource.permissions)

        try:
            # create a resource instance (ResourceInstance) from the given resource in the XML (XMLResource)
            instance: ResourceInstance = res_classes[resource.restype](con=con,
                                                                       label=resource.label,
                                                                       iri=resource_iri,
                                                                       permissions=permissions_tmp,
                                                                       bitstream=resource_bitstream,
                                                                       values=resource.get_propvals(res_iri_lookup,
                                                                                                    permissions_lookup)).create()
        except BaseError as err:
            print(
                f"ERROR while trying to create resource '{resource.label}' ({resource.id}). The error message was: {err.message}")
            failed_uploads.append(resource.id)
            continue

        except Exception as exception:
            print(
                f"ERROR while trying to create resource '{resource.label}' ({resource.id}). The error message was: {exception}")
            failed_uploads.append(resource.id)
            continue

        res_iri_lookup[resource.id] = instance.iri
        print(f"Created resource '{instance.label}' ({resource.id}) with IRI '{instance.iri}'")

    # write mapping of internal IDs to IRIs to file with timestamp
    timestamp_now = datetime.now()
    timestamp_str = timestamp_now.strftime("%Y%m%d-%H%M%S")

    xml_file_name = Path(input_file).stem
    res_iri_lookup_file = "id2iri_" + xml_file_name + "_mapping_" + timestamp_str + ".json"
    with open(res_iri_lookup_file, "w") as outfile:
        print(f"============\nThe mapping of internal IDs to IRIs was written to {res_iri_lookup_file}")
        outfile.write(json.dumps(res_iri_lookup))

    if failed_uploads:
        print(f"Could not upload the following resources: {failed_uploads}")
