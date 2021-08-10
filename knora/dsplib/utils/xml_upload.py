"""
This module handles the import of XML data into the DSP platform.
"""
import os
from typing import Dict, List, Optional, Union

from lxml import etree

from dsplib.models.connection import Connection
from dsplib.models.group import Group
from dsplib.models.permission import Permissions
from dsplib.models.project import Project
from dsplib.models.resource import ResourceInstanceFactory
from dsplib.models.sipi import Sipi
from dsplib.models.value import KnoraStandoffXml


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
    _project_map: Dict[str, str]  # dictionary of (project name:project IRI) pairs
    _inv_project_map: Dict[str, str]  # dictionary of (project IRI:project name) pairs
    _groups: list[Group]
    _group_map: Dict[str, str]
    _shortcode: Optional[str]
    _project_name: Optional[str]

    def __init__(self, con: Connection, shortcode: Optional[str] = None):
        self._shortcode = shortcode
        self._projects = Project.getAllProjects(con=con)
        self._project_map: Dict[str, str] = {x.shortname: x.id for x in self._projects}
        self._inv_project_map: Dict[str, str] = {x.id: x.shortname for x in self._projects}
        self._groups = Group.getAllGroups(con=con)
        self._group_map: Dict[str, str] = {self._inv_project_map[x.project] + ':' + x.name: x.id for x in self._groups}
        self._project_name = None
        # get the project name from the shortcode
        if self._shortcode:
            for p in self._projects:
                if p.shortcode == self._shortcode:
                    self._project_name = p.shortname
                    break

    @property
    def group_map(self) -> Dict[str, str]:
        """Dictionary of (project:group name) and (group id) pairs of all groups in project"""
        return self._group_map

    @property
    def project_name(self) -> Optional[str]:
        """Name of the project"""
        return self._project_name


class KnoraValue:
    """Represents a value of a resource in the Knora ontology"""

    _value: Union[str, KnoraStandoffXml]
    _resrefs: Optional[List[str]]
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
    def resrefs(self) -> Optional[List[str]]:
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


class KnoraProperty:
    """Represents a property of a resource in the XML"""

    _name: str
    _valtype: str
    _values: List[KnoraValue]

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
                self._values.append(KnoraValue(subnode, valtype, listname))
            else:
                raise XmlError('Unexpected tag: "{}". Property may contain only value tags!'.format(subnode.tag))

    @property
    def name(self) -> str:
        """The name of the property"""
        return self._name

    @property
    def valtype(self) -> str:
        """The value type of the property"""
        return self._valtype

    @property
    def values(self) -> List[KnoraValue]:
        """List of values of this property"""
        return self._values

    def print(self) -> None:
        """Prints the property."""
        print('  Property: {} Type: {}'.format(self._name, self._valtype))
        for value in self._values:
            value.print()


class KnoraResource:
    """Represents a resource in the Knora ontology"""

    _id: str
    _label: str
    _restype: str
    _permissions: str
    _bitstream: Optional[str]
    _properties: List[KnoraProperty]

    def __init__(self, node: etree.Element, default_ontology: Optional[str] = None) -> None:
        """
        Constructor that parses a resource node from the XML DOM

        Args:
            node: The DOM node to be processed representing a resource (which is a child of the knora element)
            default_ontology: The default ontology (given in the attribute default-ontology of the knora element)
        """
        self._id = node.attrib['id']
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
        self._permissions = node.attrib['permissions']
        self._bitstream = None
        self._properties = []
        for subnode in node:
            if subnode.tag == 'bitstream':
                self._bitstream = subnode.text  # path to the file
            elif subnode.tag is etree.Comment:
                continue
            else:
                # get the property type which is in format type-prop, p.ex. <decimal-prop>
                prop_type, _ = subnode.tag.split('-')
                self._properties.append(KnoraProperty(subnode, prop_type, default_ontology))

    @property
    def id(self) -> str:
        """The unique id of the resource"""
        return self._id

    @property
    def label(self) -> str:
        """The label of the resource"""
        return self._label

    @property
    def restype(self) -> str:
        """The type of the resource"""
        return self._restype

    @property
    def permissions(self) -> str:
        """The reference to the permissions set for this resource"""
        return self._permissions

    @property
    def bitstream(self) -> Optional[str]:
        """The path to the bitstream object (file) belonging to the resource"""
        return self._bitstream

    def print(self) -> None:
        """Prints the resource and its attributes."""
        print(f'Resource: id={self._id}, restype: {self._restype}, label: {self._label}')
        if self._bitstream is not None:
            print('  Bitstream: ' + self._bitstream)
        for prop in self._properties:
            prop.print()

    def get_resptrs(self) -> List[str]:
        """
        Get a list of all resource id's that are referenced by this resource

        Returns:
            List of resources identified by their unique id's (as given in the XML)
        """
        resptrs: List[str] = []
        for prop in self._properties:
            if prop.valtype == 'resptr':
                for value in prop.values:
                    resptrs.append(value.value)
            elif prop.valtype == 'text':
                for value in prop.values:
                    if value.resrefs is not None:
                        resptrs.extend(value.resrefs)
        return resptrs

    def get_propvals(self, resiri_lookup: Dict[str, str], permissions_lookup: Dict[str, Permissions]) -> Dict[str, Permissions]:
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
            vals: List[Union[str, Dict[str, str]]] = []
            for value in prop.values:
                v: str
                if prop.valtype == 'resptr':  # we have a resptr, therefore simple lookup or IRI
                    iri = resiri_lookup.get(value.value)
                    if iri is not None:
                        v = iri
                    else:
                        v = value.value  # if we do not find the unique_id, we assume it's a valid knora IRI
                elif prop.valtype == 'text':
                    if isinstance(value.value, KnoraStandoffXml):
                        iri_refs = value.value.findall()  # The IRI's must be embedded  as "...IRI:unique_id:IRI..."
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
                    if value.comment is not None:
                        tmp['comment'] = value.comment
                    if value.permissions is not None:
                        tmp['permissions'] = permissions_lookup.get(value.permissions)
                    vals.append(tmp)
            prop_data[prop.name] = vals if len(vals) > 1 else vals[0]
        return prop_data


class XmlAllow:
    """Represents the allow element of the XML"""

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
    """Represents the permission set containing several XmlAllow elements"""

    _id: str
    _allows: List[XmlAllow]

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
    def allows(self) -> List[XmlAllow]:
        """List of XmlAllow elements defining permissions for specific groups"""
        return self._allows

    def get_permission_instance(self) -> Permissions:
        """Returns a list of allow elements of this permission instance"""
        permissions = Permissions()
        for allow in self._allows:
            permissions.add(allow.permission, allow.group)
        return permissions

    def __str__(self):
        allow_str: List[str] = []
        for allow in self._allows:
            allow_str.append("{} {}".format(allow.permission, allow.group))
        return '|'.join(allow_str)

    def print(self):
        """Prints the permission set"""
        print('Permission: ', self._id)
        for a in self._allows:
            a.print()


def do_sort_order(resources: List[KnoraResource]) -> List[KnoraResource]:
    """
    Sorts a list of resources.

    The sorting is such that resources that reference other resources are added after the referenced resources. It
    will fail with an error if there are circular references.

    Args:
        resources: List of resources before sorting

    Returns:
        sorted list of resources
    """

    # sort the resources according to outgoing resptrs
    ok_resources: [KnoraResource] = []
    notok_resources: [KnoraResource] = []
    ok_res_ids: [str] = []
    cnt = 0
    notok_len = 9999999
    while len(resources) > 0 and cnt < 10000:
        for resource in resources:
            resptrs = resource.get_resptrs()
            if len(resptrs) == 0:
                ok_resources.append(resource)
                ok_res_ids.append(resource.id)
            else:
                ok = True
                for resptr in resptrs:
                    if resptr in ok_res_ids:
                        pass
                    else:
                        ok = False
                if ok:
                    ok_resources.append(resource)
                    ok_res_ids.append(resource.id)
                else:
                    notok_resources.append(resource)
        resources = notok_resources
        if not len(notok_resources) < notok_len:
            print('Cannot resolve resptr dependencies. Giving up....')
            print(len(notok_resources))
            for r in notok_resources:
                print('Resource {} has unresolvable resptrs to: '.format(r.id), end=' ')
                for x in r.get_resptrs():
                    print(x, end=' ')
                print('')
                print('=============')
            exit(5)
        notok_len = len(notok_resources)
        notok_resources = []
        cnt += 1
        print('{}. Ordering pass Finished!'.format(cnt))
    # print('Remaining: {}'.format(len(resources)))
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
    xmlschema = etree.XMLSchema(schema_file)
    doc = etree.parse(input_file)

    is_valid = False

    if xmlschema.assertValid(doc):
        is_valid = True

    return is_valid


def xml_upload(input_file: str, server: str, user: str, password: str, imgdir: str, sipi: str, verbose: bool,
               validate_only: bool) -> bool:
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

    Returns:
        None
    """

    # Validate the input XML file
    current_dir = os.path.dirname(os.path.realpath(__file__))
    schema_file = etree.parse(os.path.join(current_dir, 'knora-data-schema.xsd'))

    if validate_xml_against_schema(input_file, schema_file):
        print("The input data file is syntactically correct and passed validation!")
        if validate_only:
            return True

    # Connect to the DaSCH Service Platform API and get the project context
    con = Connection(server)
    con.login(user, password)
    proj_context = ProjectContext(con=con)

    resources: List[KnoraResource] = []
    permissions: Dict[str, XmlPermission] = {}

    # parse the XML file containing the data
    tree = etree.parse(input_file)
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
            resources.append(KnoraResource(child, default_ontology))

    # sort the resources (resources which do not link to others come first)
    resources = do_sort_order(resources)

    sipi = Sipi(sipi, con.get_token())

    # get the project information and project ontology from the server
    project = ResourceInstanceFactory(con, shortcode)

    # create a dictionary to look up permissions
    permissions_lookup: Dict[str, Permissions] = {}
    for key, perm in permissions.items():
        permissions_lookup[key] = perm.get_permission_instance()

    # create a dictionary to look up resource classes
    res_classes: Dict[str, type] = {}
    for res_class_name in project.get_resclass_names():
        res_classes[res_class_name] = project.get_resclass(res_class_name)

    res_iri_lookup: Dict[str, str] = {}

    for resource in resources:
        if verbose:
            resource.print()
        if resource.bitstream:
            img = sipi.upload_bitstream(os.path.join(imgdir, resource.bitstream))
            bitstream = img['uploadedFiles'][0]['internalFilename']
        else:
            bitstream = None

        # create the resource on the server
        instance = res_classes[resource.restype](con=con, label=resource.label,
                                                 permissions=permissions_lookup.get(resource.permissions), bitstream=bitstream,
                                                 values=resource.get_propvals(res_iri_lookup, permissions_lookup)).create()
        res_iri_lookup[resource.id] = instance.iri
        print("Created resource: ", instance.label, " (", resource.id, ") with IRI ", instance.iri)
