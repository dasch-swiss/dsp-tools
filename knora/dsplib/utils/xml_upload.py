import os
import re

from typing import List, Set, Dict, Tuple, Optional, Union
from lxml import etree
from dsplib.models.connection import Connection
from dsplib.models.resource import ResourceInstanceFactory
from dsplib.models.value import BooleanValue, ColorValue, DateValue, DecimalValue, IntValue, IntervalValue, TextValue, \
    UriValue, KnoraStandoffXml, make_value
from dsplib.models.permission import PermissionValue, Permissions

StrDict = Dict[str, str]

StrObj = Union[str, StrDict]

VarStrObj = Union[StrObj,List[StrObj]]


class XmlError(BaseException):

    def __init__(self, msg: str):
        self._message = msg

    def __str__(self):
        return 'XML-ERROR: ' + self._message

class KnoraValue:
    _value: Union[str, KnoraStandoffXml]
    _resrefs: List[str]
    _comment: str
    _permissions: str
    is_richtext: bool

    def __init__(self,
                 context: etree.iterparse,
                 node: Tuple,
                 valtype: str,
                 listname: Optional[str] = None) -> None:

        self._resrefs = None
        self._comment = node.get('comment')
        self._permissions = node.get('permissions')
        if node.get('resrefs') is not None:
            self._resrefs = node.attrib['resrefs'].split('|')
        if node.get('encoding') == 'basic':
            self._value = KnoraStandoffXml("".join(node.itertext()))
        else:
            if valtype == 'list':
                self._value = listname + ':' + "".join(node.itertext())
            else:
                self._value = "".join(node.itertext())
        while True:
            event, subnode = next(context)
            if event == 'start':
                raise XmlError(
                    'Unexpected start tag: "{}" value-tags may contain no other tags!'.format(subnode.tag))
            else:
                if subnode.tag == type:
                    break
                else:
                    raise XmlError('Unexpected end tag: "{}": </{}> expected!'.format(subnode.tag, type))

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
        print('    Value: ' + self._value)
        if self._comment:
            print('   Comment:' + self._comment)
        if self._resrefs is not None:
            for i in self._resrefs:
                print('    resref: ' + i)


class KnoraProperty:
    _name: str
    _valtype: str
    _values: List[KnoraValue]

    def __init__(self, context: etree.iterparse, node: Tuple, valtype: str):
        self._name = node.attrib['name'] # safe the property nam
        listname = node.attrib.get('list') # safe the list name if given (only for lists)
        self._valtype = type
        self._values = []

        while True:
            event, subnode = next(context)
            if event == 'start':
                if subnode.tag == valtype:  # the subnode must correspond to the expected value type
                    self._values.append(KnoraValue(context, subnode, valtype, listname))
                else:
                    raise XmlError('Unexpected start tag: "{}" <property> may contain only <value> tags!'.format(subnode.tag))
            else:
                if subnode.tag == 'text-prop' or subnode.tag == 'color-prop' or \
                    subnode.tag == 'date-prop' or subnode.tag == 'decimal-prop' or \
                    subnode.tag == 'geometry-prop' or subnode.tag == 'geoname-prop' or \
                    subnode.tag == 'list-prop' or subnode.tag == 'iconclass-prop' or \
                    subnode.tag == 'integer-prop' or subnode.tag == 'interval-prop' or \
                    subnode.tag == 'period-prop' or subnode.tag == 'resptr-prop' or \
                    subnode.tag == 'resptr-prop' or subnode.tag == 'time-prop' or \
                    subnode.tag == 'uri-prop' or subnode.tag == 'boolean-prop':
                    break
                else:
                    raise XmlError('Unknown endtag for property: "{}"!'.format(subnode.tag))

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
    _unique_id: str
    _label: str
    _restype: str
    _permissions: str
    _image: str
    _properties: List[KnoraProperty]

    def __init__(self, context: etree.iterparse, node: Tuple) -> None:
        """
        Constructor that parses a resource node from the XML DOM

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing a resource)
        """
        self._unique_id = node.attrib['unique_id'] # safe the unique id
        self._label = node.attrib['label']
        self._restype = node.attrib['restype']
        self._permissions = node.attrib['permissions']
        self._image = None
        self._properties = []
        while True:
            event, subnode = next(context)
            if event == 'start':
                if subnode.tag == 'image':
                    self._image = node.text
                elif subnode.tag == 'text-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'text'))
                elif subnode.tag == 'color-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'color'))
                elif subnode.tag == 'date-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'date'))
                elif subnode.tag == 'decimal-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'decimal'))
                elif subnode.tag == 'geometry-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'geometry'))
                elif subnode.tag == 'geoname-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'geoname'))
                elif subnode.tag == 'list-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'list'))
                elif subnode.tag == 'iconclass-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'iconclass'))
                elif subnode.tag == 'integer-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'integer'))
                elif subnode.tag == 'interval-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'interval'))
                elif subnode.tag == 'period-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'period'))
                elif subnode.tag == 'resptr-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'resptr'))
                elif subnode.tag == 'time-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'time'))
                elif subnode.tag == 'uri-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'uri'))
                elif subnode.tag == 'boolean-prop':
                    self._properties.append(KnoraProperty(context, subnode, 'boolean'))
                else:
                    raise XmlError('Unexpected start tag: "{}" <resource> may contain only <property> or <image> tags!'.format(subnode.tag))
            else:
                if subnode.tag == 'resource':
                    break
                elif subnode.tag == 'image':
                    self.image = "".join(subnode.itertext())
                else:
                    raise XmlError('Unexpected end tag: "{}" </resource> expected!'.format(subnode.tag))

    def print(self):
        print('Resource: id={} restype: {} label: {}'.format(self._unique_id, self._restype, self._label))
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
            elif property.type == 'text':
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
        exp = re.compile(r'IRI:[^:]*:IRI') # regepx to parse the IRI's in RichText's
        for property in self.properties:
            vals: List[StrObj] = []  # == List[Union[str,StrDict]
            for value in property.values:
                v: str
                if property.type == 'resptr':  # we have a resptr, therefore simple lookup or IRI
                    iri = resiri_lookup.get(value.value)
                    if iri is not None:
                        v = iri
                    else:
                        v = value.value  # if we do not find the unique_id, we assume it's a valid knora IRI
                elif property.type == 'text':  # we have a text which might have embedded references to other resources
                    if isinstance(value.value, KnoraStandoffXml):
                        irirefs = value.value.findall()  # The IRI's must be embedded  as "...IRI:unique_id:IRI..."
                        for iriref in irirefs:
                            resid = iriref.split(':')[1]
                            iri = resiri_lookup.get(resid)
                            value.value.replace(iriref, iri)
                    #tmpstr: str = value.value
                    #for iriref in irirefs:
                    #    resid = iriref.split(':')[1]
                    #    iri = resiri_lookup.get(resid)
                    #    tmpstr.replace(iriref, iri)
                    #v = tmpstr
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

    def __init__(self, context: etree.iterparse, node: Tuple) -> None:
        """
        Constructor which parses the XML DOM allow element

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing an single right in a permission set)
        """
        self._group = node.attrib['group']
        self._permission = "".join(node.itertext())
        # UnknownUser | KnownUser | ProjectMember | Creator | ProjectAdmin | SystemAdmin

    @property
    def group(self):
        return self._group

    @property
    def permission(self):
        return self._permission


class XmlPermission:
    """
    A class representing a permission set
    """
    _id: str
    _allows: List[XmlAllow]

    def __init__(self, context: etree.iterparse, node: Tuple) -> None:
        """
        Constructor which parses a XML DOM permissions element represrenting an named permission set

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing an a permission set)
        """
        self._allows = []
        self._id = node.attrib['id']
        while True:
            event, subnode = next(context)
            if event == 'start':
                if subnode.tag == 'allow':
                    self._allows.append(XmlAllow(context, subnode))
                else:
                    raise XmlError ('Unexpected tag: "{}" <allow> expected!'.format(subnode.tag))
            else:
                if subnode.tag == 'allow':
                    pass
                elif subnode.tag == 'resource':
                    break
                elif subnode.tag == 'permissions':
                    break
                else:
                    raise XmlError('Unexpected end tag: "{}" </resource> expected!'.format(subnode.tag))

    def get(self) -> Permissions:
        permissions = Permissions()
        for allow in self._allows:
            permissions.add(allow.permission, allow.group)
        return permissions

    def __str__(self):
        allowstrs: List[str] = []
        for allow in self._allows:
            allowstrs.append("{} {}".format(allow.permission, allow.group))
        return '|'.join(allowstrs)

def xml_upload(input_file: str,
               server: str,
               user: str,
               password: str,
               verbose: bool) -> bool:
    current_dir = os.path.dirname(os.path.realpath(__file__))

    #
    # Connect to the DaSCH Service Platform API
    #
    con = Connection(server)
    con.login(user, password)

    xmlschema_doc = etree.parse(os.path.join(current_dir, 'knora-data-schema.xsd'))
    xmlschema = etree.XMLSchema(xmlschema_doc)
    doc = etree.parse(input_file)
    xmlschema.assertValid(doc)

    del xmlschema
    del doc
    del xmlschema_doc

    print("The imput data file is syntactically correct and passed validation!")
