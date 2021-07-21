"""
The code in this file handles the import of XML data into the DSP platform.
"""
import os
from typing import List, Dict, Optional, Union

from dsplib.models.connection import Connection
from dsplib.models.group import Group
from dsplib.models.permission import Permissions
from dsplib.models.project import Project
from dsplib.models.resource import ResourceInstanceFactory
from dsplib.models.sipi import Sipi
from dsplib.models.value import KnoraStandoffXml
from lxml import etree

StrDict = Dict[str, str]

StrObj = Union[str, StrDict]

VarStrObj = Union[StrObj, List[StrObj]]

richtext_tags = [
    'p', 'em', 'strong', 'u', 'sub', 'strike', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'li', 'tbody',
    'table', 'tr', 'td', 'br', 'hr', 'pre', 'cite', 'blockquote', 'code'
]


class XmlError(BaseException):
    """Represents an error raised in the context of the XML import."""

    def __init__(self, msg: str):
        self._message = msg

    def __str__(self):
        return 'XML-ERROR: ' + self._message


class ProjectContext:
    """Represents the project context."""
    _projects: list[Project]
    _groups: list[Group]
    _project_map: Dict[str, str]
    _inv_project_map: Dict[str, str]
    _group_map: Dict[str, str]
    _shortcode: Union[str, None]
    _project_name: Union[str, None]

    def __init__(self, con: Connection, shortcode: Optional[str] = None):
        self._shortcode = shortcode
        self._projects = Project.getAllProjects(con=con)
        self._project_map: Dict[str, str] = {x.shortname: x.id for x in self._projects}
        inv_project_map: Dict[str, str] = {x.id: x.shortname for x in self._projects}
        self._groups = Group.getAllGroups(con=con)
        self._group_map: Dict[str, str] = {inv_project_map[x.project] + ':' + x.name: x.id for x in self._groups}
        self._project_name = None
        if self._shortcode:
            for p in self._projects:
                if p.shortcode == self._shortcode:
                    self._project_name = p.shortname
                    break

    @property
    def group_map(self) -> Dict[str, str]:
        """Dictionary of (project:group name) and (group id) of all groups in project, p.ex. {'rosetta:rosetta
        -editors': 'http://rdfh.ch/groups/082E/7IdVjy0WTVyYe21Z1GnsKQ'}"""
        return self._group_map

    @property
    def shortcode(self) -> Union[str, None]:
        """Shortcode of the project"""
        return self._shortcode

    @shortcode.setter
    def shortcode(self, value) -> None:
        for p in self._projects:
            if p.shortcode == self._shortcode:
                self._project_name = p.shortname
                break

    @property
    def project_name(self) -> Union[str, None]:
        """Name of the project"""
        return self._project_name


class KnoraValue:
    """Represents a value of a resource in the Knora ontology"""
    _value: Union[str, KnoraStandoffXml]
    _resrefs: Union[List[str], None]
    _comment: str
    _permissions: str
    is_richtext: bool

    def __init__(self,
                 node: etree.Element,
                 val_type: str,
                 listname: Optional[str] = None) -> None:

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
    def resrefs(self) -> Union[List[str], None]:
        """List of resource references ???"""
        return self._resrefs

    @property
    def comment(self) -> str:
        """Comment for this value"""
        return self._comment

    @property
    def permissions(self) -> str:
        """Reference to a set of permissions"""
        return self._permissions

    def print(self) -> None:
        """Prints the value and its attributes."""
        print('   Value: ' + str(self._value))
        if self._comment:
            print('   Comment:' + self._comment)
        if self._resrefs is not None:
            for i in self._resrefs:
                print('   res_ref: ' + i)


class KnoraProperty:
    """Represents a property of a resource in the Knora ontology"""
    _name: str
    _val_type: str
    _values: List[KnoraValue]

    def __init__(self, node: etree.Element, val_type: str, default_ontology: Optional[str] = None):
        tmp = node.attrib['name'].split(':')
        if len(tmp) > 1:
            if tmp[0]:
                self._name = node.attrib['name']
            else:
                self._name = default_ontology + ':' + tmp[1]
        else:
            self._name = 'knora-admin:' + tmp[0]
        listname = node.attrib.get('list')  # safe the list name if given (only for lists)
        self._val_type = val_type
        self._values = []

        for subnode in node:
            if subnode.tag == val_type:  # the subnode must correspond to the expected value type
                self._values.append(KnoraValue(subnode, val_type, listname))
            else:
                raise XmlError('Unexpected tag: "{}" <property> may contain only <value> tags!'.format(subnode.tag))

    @property
    def name(self) -> str:
        """The name of the property"""
        return self._name

    @property
    def valtype(self) -> str:
        """The value type of the property"""
        return self._val_type

    @property
    def values(self) -> List[KnoraValue]:
        """List of values of this property"""
        return self._values

    def print(self) -> None:
        """Prints the property."""
        print('  Property: {} Type: {}'.format(self._name, self._val_type))
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
            node: The DOM node to be processed (representing a resource, is a child of the knora element)
            default_ontology: The default ontology (given with the attribute default-ontology of the knora element)
        """
        self._id = node.attrib['id']  # safe the unique id
        self._label = node.attrib['label']
        tmp = node.attrib['restype'].split(':')
        if len(tmp) > 1:
            if tmp[0]:
                self._restype = node.attrib['restype']
            else:
                self._restype = default_ontology + ':' + tmp[1]
        else:
            self._restype = 'knora-admin:' + tmp[0]
        self._permissions = node.attrib['permissions']
        self._bitstream = None
        self._properties = []
        for subnode in node:
            if subnode.tag == 'bitstream':
                self._bitstream = subnode.text
            elif subnode.tag is etree.Comment:
                continue
            else:
                ptype, dummy = subnode.tag.split('-')
                self._properties.append(KnoraProperty(subnode, ptype, default_ontology))

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
    def bitstream(self) -> Optional[str]:
        """The path to the bitstream object (file) belonging to the resource"""
        return self._bitstream

    @property
    def permissions(self) -> str:
        """The reference to the permissions set for this resource"""
        return self._permissions

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

    def get_propvals(self,
                     resiri_lookup: StrDict,
                     permissions_lookup: StrDict) -> Dict[str, VarStrObj]:
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
            vals: List[StrObj] = []  # == List[Union[str,StrDict]
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
            prop_data[prop.name] = vals if len(vals) > 1 else vals[0]  # append a Union[StrObj,List[StrObj]]
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
    print('Remaining: {}'.format(len(resources)))
    return ok_resources


def xml_upload(input_file: str,
               server: str,
               user: str,
               password: str,
               imgdir: str,
               sipi: str,
               verbose: bool,
               validate: bool) -> bool:
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
        validate : validation option to validate the XML data only without the actual import of the data

    Returns:
        None
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))

    xmlschema_doc = etree.parse(os.path.join(current_dir, 'knora-data-schema.xsd'))
    xmlschema = etree.XMLSchema(xmlschema_doc)
    doc = etree.parse(input_file)
    xmlschema.assertValid(doc)

    print("The input data file is syntactically correct and passed validation!")

    if validate:
        return True

    # Connect to the DaSCH Service Platform API
    con = Connection(server)
    con.login(user, password)

    proj_context = ProjectContext(con=con)

    resources: List[KnoraResource] = []
    permissions: Dict[str, XmlPermission] = {}

    # read the XML file containing the data, including project shortcode
    tree = etree.parse(input_file)
    knora = tree.getroot()
    default_ontology = knora.attrib['default-ontology']
    shortcode = knora.attrib['shortcode']
    for child in knora:
        if child.tag == "permissions":
            permission = XmlPermission(child, proj_context)
            permissions[permission.id] = permission
        elif child.tag == "resource":
            resources.append(KnoraResource(child, default_ontology))

    # sort the resources so that resources which do not link to others come first
    resources = do_sort_order(resources)

    sipi = Sipi(sipi, con.get_token())

    factory = ResourceInstanceFactory(con, shortcode)

    permissions_lookup: Dict[str, Permissions] = {}
    for key, perm in permissions.items():
        permissions_lookup[key] = perm.get_permission_instance()

    resclassnames = factory.get_resclass_names()
    resclasses: Dict[str, type] = {}
    for resclassname in resclassnames:
        resclasses[resclassname] = factory.get_resclass(resclassname)
    resiri_lookup: StrDict = {}

    for resource in resources:
        if verbose:
            resource.print()
        if resource.bitstream:
            img = sipi.upload_bitstream(os.path.join(imgdir, resource.bitstream))
            bitstream = img['uploadedFiles'][0]['internalFilename']
        else:
            bitstream = None
        instance = resclasses[resource.restype](con=con,
                                                label=resource.label,
                                                permissions=permissions_lookup.get(resource.permissions),
                                                bitstream=bitstream,
                                                values=resource.get_propvals(resiri_lookup,
                                                                             permissions_lookup)).create()
        resiri_lookup[resource.id] = instance.iri
        print("Created resource: ", instance.label, " with IRI ", instance.iri)
