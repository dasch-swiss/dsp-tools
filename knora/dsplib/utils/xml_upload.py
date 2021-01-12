import os
import re

from typing import List, Set, Dict, Tuple, Optional, Union
from lxml import etree
from pprint import pprint

from dsplib.models.connection import Connection
from dsplib.models.group import Group
from dsplib.models.helpers import IriTest
from dsplib.models.project import Project
from dsplib.models.resource import ResourceInstanceFactory
from dsplib.models.value import BooleanValue, ColorValue, DateValue, DecimalValue, IntValue, IntervalValue, TextValue, \
    UriValue, KnoraStandoffXml, make_value
from dsplib.models.permission import PermissionValue, Permissions
from dsplib.models.sipi import Sipi

StrDict = Dict[str, str]

StrObj = Union[str, StrDict]

VarStrObj = Union[StrObj, List[StrObj]]

richtext_tags = [
    'p', 'em', 'strong', 'u', 'sub', 'strike', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ol', 'ul', 'li', 'tbody',
    'table', 'tr', 'td', 'br', 'hr', 'pre', 'cite', 'blockquote', 'code'
]

class XmlError(BaseException):

    def __init__(self, msg: str):
        self._message = msg

    def __str__(self):
        return 'XML-ERROR: ' + self._message


class ProjectContext:
    _projects: Project
    _groups: Group
    _projectmap: Dict[str, str]
    _invprojectmap: Dict[str, str]
    _groupmap: Dict[str, str]
    _shortcode: Union[str, None]
    _project_name: Union[str, None]

    def __init__(self, con: Connection, shortcode: Optional[str] = None):
        self._shortcode = shortcode
        self._projects = Project.getAllProjects(con=con)
        self._projectmap: Dict[str, str] = {x.shortname: x.id for x in self._projects}
        invprojectmap: Dict[str, str] = {x.id: x.shortname for x in self._projects}
        self._groups = Group.getAllGroups(con=con)
        self._groupmap: Dict[str, str] = {invprojectmap[x.project] + ':' + x.name: x.id for x in self._groups}
        self._project_name = None
        if self._shortcode:
            for p in self._projects:
                if p.shortcode == self._shortcode:
                    self._project_name = p.shortname
                    break

    @property
    def groupmap(self):
        return self._groupmap

    @property
    def shortcode(self) -> Union[str, None]:
        return self._shortcode

    @shortcode.setter
    def shortcode(self, val: str) -> None:
        for p in self._projects:
            if p.shortcode == self._shortcode:
                self._project_name = p.shortname
                break

    @property
    def project_name(self) -> Union[str, None]:
        return self._project_name


class KnoraValue:
    _value: Union[str, KnoraStandoffXml]
    _resrefs: List[str]
    _comment: str
    _permissions: str
    is_richtext: bool

    def __init__(self,
                 node: etree.Element,
                 valtype: str,
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
            tmpidlist = self._value.findall()
            if tmpidlist:
                refs = set()
                for tmpid in tmpidlist:
                    refs.add(tmpid.split(':')[1])
                self._resrefs = list(refs)
        else:
            if valtype == 'list':
                self._value = listname + ':' + "".join(node.itertext())
            else:
                self._value = "".join(node.itertext())

    @property
    def value(self):
        return self._value

    @property
    def resrefs(self):
        return self._resrefs

    @property
    def comment(self):
        return self._comment

    @property
    def permissions(self):
        return self._permissions

    def print(self) -> None:
        """
        Print value to stdout for debugging...

        :return: None
        """
        print('    Value: ' + str(self._value))
        if self._comment:
            print('   Comment:' + self._comment)
        if self._resrefs is not None:
            for i in self._resrefs:
                print('    resref: ' + i)


class KnoraProperty:
    _name: str
    _valtype: str
    _values: List[KnoraValue]

    def __init__(self, node: etree.Element, valtype: str, default_ontology: Optional[str] = None):
        tmp = node.attrib['name'].split(':')
        if len(tmp) > 1:
            if tmp[0]:
                self._name = node.attrib['name']
            else:
                self._name = default_ontology + ':' + tmp[1]
        else:
            self._name = 'knora-admin:' + tmp[0]
        listname = node.attrib.get('list')  # safe the list name if given (only for lists)
        self._valtype = valtype
        self._values = []

        for subnode in node:
            if subnode.tag == valtype:  # the subnode must correspond to the expected value type
                self._values.append(KnoraValue(subnode, valtype, listname))
            else:
                raise XmlError('Unexpected tag: "{}" <property> may contain only <value> tags!'.format(subnode.tag))

    @property
    def name(self):
        return self._name

    @property
    def valtype(self):
        return self._valtype

    @property
    def values(self):
        return self._values

    def print(self) -> None:
        print('  Property: {} Type: {}'.format(self._name, self._valtype))
        for value in self._values:
            value.print()


class KnoraResource:
    _id: str
    _label: str
    _restype: str
    _permissions: str
    _image: str
    _properties: List[KnoraProperty]

    def __init__(self, node: etree.Element, default_ontology: Optional[str] = None) -> None:
        """
        Constructor that parses a resource node from the XML DOM

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing a resource)
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
        self._image = None
        self._properties = []
        for subnode in node:
            if subnode.tag == 'image':
                self._image = subnode.text
            elif subnode.tag is etree.Comment:
                    continue
            else:
                ptype, dummy = subnode.tag.split('-')
                self._properties.append(KnoraProperty(subnode, ptype, default_ontology))

    @property
    def id(self) -> str:
        return self._id

    @property
    def label(self) -> str:
        return self._label

    @property
    def restype(self) -> str:
        return self._restype

    @property
    def image(self) -> str:
        return self._image

    @property
    def permissions(self):
        return self._permissions

    def print(self):
        print('Resource: id={} restype: {} label: {}'.format(self._id, self._restype, self._label))
        if self._image is not None:
            print(' Image: ' + self._image)
        for property in self._properties:
            property.print()

    def get_resptrs(self) -> List[str]:
        """
        Return a list of all reesource id's  that a referenced by this resource
        :return: List of resources identified by their unique id's
        """
        resptrs: List[str] = []
        for property in self._properties:
            if property.valtype == 'resptr':
                for value in property.values:
                    resptrs.append(value.value)
            elif property.valtype == 'text':
                for value in property.values:
                    if value.resrefs is not None:
                        resptrs.extend(value.resrefs)
        return resptrs

    def get_propvals(self,
                     resiri_lookup: StrDict,
                     permissions_lookup: StrDict) -> Dict[str, VarStrObj]:
        """
        A function which retrieves...

        :param resiri_lookup: Is used to solve internal unique_id's of resourcs to real IRI's
        :param permissions_lookup: Is usd to resolve thee permission ID's to permission sets
        :return: A dict of values with the property name as key and a single value. This dict represents
                 the JSON structure that Knora.create_resource() expects.
        """
        propdata = {}
        for property in self._properties:
            vals: List[StrObj] = []  # == List[Union[str,StrDict]
            for value in property.values:
                v: str
                if property.valtype == 'resptr':  # we have a resptr, therefore simple lookup or IRI
                    iri = resiri_lookup.get(value.value)
                    if iri is not None:
                        v = iri
                    else:
                        v = value.value  # if we do not find the unique_id, we assume it's a valid knora IRI
                elif property.valtype == 'text':
                    if isinstance(value.value, KnoraStandoffXml):
                        irirefs = value.value.findall()  # The IRI's must be embedded  as "...IRI:unique_id:IRI..."
                        for iriref in irirefs:
                            resid = iriref.split(':')[1]
                            iri = resiri_lookup.get(resid)
                            value.value.replace(iriref, iri)
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
            propdata[property.name] = vals if len(vals) > 1 else vals[0]  # append a Union[StrObj,List[StrObj]]
        return propdata


class XmlAllow:
    _group: str
    _permission: str

    def __init__(self, node: etree.Element, project_context: ProjectContext) -> None:
        """
        Constructor which parses the XML DOM allow element

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing an single right in a permission set)
        """
        tmp = node.attrib['group'].split(':')
        sysgroups = ['UnknownUser', 'KnownUser', 'ProjectMember', 'Creator', 'ProjectAdmin', 'SystemAdmin']
        if len(tmp) > 1:
            if tmp[0]:
                if tmp[0] == 'knora-admin' and tmp[1] in sysgroups:
                    self._group = node.attrib['group']
                else:
                    self._group = project_context.groupmap.get(node.attrib['group'])
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
    def group(self):
        return self._group

    @property
    def permission(self):
        return self._permission

    def print(self):
        print("  group=", self._group, " permission=", self._permission)


class XmlPermission:
    """
    A class representing a permission set
    """
    _id: str
    _allows: List[XmlAllow]

    def __init__(self, node: etree.Element, project_context: ProjectContext) -> None:
        """
        Constructor which parses a XML DOM permissions element representing an named permission set

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing an a permission set)
        """
        self._allows = []
        self._id = node.attrib['id']
        for allow_node in node:
            self._allows.append(XmlAllow(allow_node, project_context))

    @property
    def id(self) -> str:
        return self._id

    @property
    def allows(self) -> List[XmlAllow]:
        return self._allows

    def get_permission_instance(self) -> Permissions:
        permissions = Permissions()
        for allow in self._allows:
            permissions.add(allow.permission, allow.group)
        return permissions

    def __str__(self):
        allowstrs: List[str] = []
        for allow in self._allows:
            allowstrs.append("{} {}".format(allow.permission, allow.group))
        return '|'.join(allowstrs)

    def print(self):
        print('Permission: ', self._id)
        for a in self._allows:
            a.print()


def do_sortorder(resources: List[KnoraResource]) -> List[KnoraResource]:
    """
    Sort the list of resources such that resources that reference other resources are
    added after the referenced resources. It will fail with an error if there are circular
    references.

    :param resources: List of resources before sorting
    :return: Sorted list of resources
    """
    #
    # here we sort the resources according to outgoing resptrs
    #
    ok_resources: [KnoraResource] = []
    notok_resources: [KnoraResource] = []
    ok_resids : [str] = []
    cnt = 0
    notok_len = 9999999
    while len(resources) > 0 and cnt < 10000:
        for resource in resources:
            resptrs = resource.get_resptrs()
            if len(resptrs) == 0:
                ok_resources.append(resource)
                ok_resids.append(resource.id)
            else:
                ok = True
                for resptr in resptrs:
                    if resptr in ok_resids:
                        pass
                    else:
                        ok = False;
                if ok:
                    ok_resources.append(resource)
                    ok_resids.append(resource.id)
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
    current_dir = os.path.dirname(os.path.realpath(__file__))

    xmlschema_doc = etree.parse(os.path.join(current_dir, 'knora-data-schema.xsd'))
    xmlschema = etree.XMLSchema(xmlschema_doc)
    doc = etree.parse(input_file)
    xmlschema.assertValid(doc)

    del xmlschema
    del doc
    del xmlschema_doc

    if validate:
        return

    print("The input data file is syntactically correct and passed validation!")

    #
    # Connect to the DaSCH Service Platform API
    #
    con = Connection(server)
    con.login(user, password)

    proj_context = ProjectContext(con=con)

    resources: List[KnoraResource] = []
    permissions: Dict[str, XmlPermission] = {}
    shortcode: Union[str, None] = None
    default_ontology = None

    #
    # read the XML file containing the data, including project shortcode
    #
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

    #
    # sort the resources so that resources which do not link to others come first
    #
    resources = do_sortorder(resources)

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
        if resource.image:
            img = sipi.upload_image(os.path.join(imgdir, resource.image))
            bitstream = img['uploadedFiles'][0]['internalFilename']
        else:
            bitstream = None
        instance = resclasses[resource.restype](con=con,
                                                label=resource.label,
                                                permissions=permissions_lookup.get(resource.permissions),
                                                bitstream=bitstream,
                                                values=resource.get_propvals(resiri_lookup, permissions_lookup)).create()
        resiri_lookup[resource.id] = instance.iri
        print("Created:", instance.iri)
