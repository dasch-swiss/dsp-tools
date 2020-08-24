from typing import List, Set, Dict, Tuple, Optional, Union
from enum import Enum
from lxml import etree
from pprint import pprint
import os
import argparse
import base64
import json
import sys
import requests
import re
from knora import KnoraError, KnoraStandoffXml, Knora, Sipi

#==============================================================================
# Some type defitions

#
# A dictionary with key and values as strings
#
StrDict = Dict[str,str]

#
# A thing that can either be a string or StrDict
#
StrObj = Union[str,StrDict]

#
# A thing that either can be a single StrObj or a list of StrObj's
#
VarStrObj = Union[StrObj,List[StrObj]]



# https://raw.githubusercontent.com/dhlab-basel/dasch-ark-resolver-data/master/data/shortcodes.csv

class MyError(BaseException):
    """
    Used for error handling
    """
    def __init__(self, msg: str):
        self.message = msg


class KnoraValue:
    """
    Represents a single knora value

    A typical value has the form  (example for complex text)

    ::

        <text comment="a comment"
              permissions="permissionId"
              encoding="hex64"
              resrefs="A77|B88">PHA+YnM6IHdhaHJzY2hlaW5sa</text>

    All options are optional.
    """
    resrefs: List[str]
    comment: str
    permissions: str
    value: Union[str,KnoraStandoffXml]
    is_richtext: bool

    def __init__(self,
                 context: etree.iterparse,
                 node: Tuple,
                 type: str,
                 listname: Optional[str] = None) -> None:
        """
        Constructor for parsing a value from a XML DOM

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed
        :param type: The Value type ('text','color','date','decimal','geometry','geoname','list', etc.)
        :param listname: Name of the list [optional] (used for list values)
        """

        self.resrefs = None
        self.comment = node.get('comment')
        self.permissions = node.get('permissions')
        if node.get('resrefs') is not None:
            self.resrefs = node.attrib['resrefs'].split('|')
        if node.get('encoding') == 'hex64':
            #self.value = KnoraStandoffXml(
            #    '<?xml version="1.0" encoding="UTF-8"?>\n<text>' + \
            #    base64.b64decode("".join(node.itertext())).decode() + '</text>')
            self.value = '<?xml version="1.0" encoding="UTF-8"?>\n<text>' + \
                base64.b64decode("".join(node.itertext())).decode() + '</text>'
        else:
            if type == 'list':
                self.value = listname + ':' + "".join(node.itertext())
            else:
                self.value = "".join(node.itertext())
        while True:
            event, subnode = next(context)
            if event == 'start':
                raise MyError(
                    'Unexpected start tag: "{}" value-tags may contain no other tags!'.format(subnode.tag))
            else:
                if subnode.tag == type:
                    break
                else:
                    raise MyError('Unexpected end tag: "{}": </{}> expected!'.format(subnode.tag, type))

    def print(self)  -> None:
        """
        Print value to stdout for debugging...

        :return: None
        """
        print('    Value: ' + self.value)
        if self.comment:
            print('   Comment:' + self.comment)
        if self.resrefs is not None:
            for i in self.resrefs:
                print('    resref: ' + i)


class KnoraProperty:
    """
    A class representing a knora property class

    A typical property node has the form:

    ::
        <text-prop name="mySimpleText">
        …
        </text-prop>

    The option "name" is required an indicates the name of the knora property.
    """
    name: str
    type: str
    values: List[KnoraValue]

    def __init__(self, context: etree.iterparse, node: Tuple, type):
        """
        Constructor to parse a property class from XML DOM

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing a property class)
        :param type: The Value type ('text','color','date','decimal','geometry','geoname','list', etc.)
        """

        self.name = node.attrib['name'] # safe the property nam
        listname = node.attrib.get('list') # safe the list name if given (only for lists)
        self.type = type
        self.values = []

        #
        # Now we start procssing tbe subnodes which should be value nodes
        #
        while True:
            event, subnode = next(context)
            if event == 'start':
                if subnode.tag == type: # the subnode must correspond to the expected value type
                    self.values.append(KnoraValue(context, subnode, type, listname))
                else:
                    raise MyError('Unexpected start tag: "{}" <property> may contain only <value> tags!'.format(subnode.tag))
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
                    raise MyError('Unknown endtag for property: "{}"!'.format(subnode.tag))

    def print(self) -> None:
        """
        Print property class to stdout for debugging...

        :return: None
        """
        print('  Property: {} Type: {}'.format(self.name, self.type))
        for value in self.values:
            value.print()


class KnoraResource:
    """
    A class representing a resource from the XML DOM.

    A typical resource node looks like follows:

    ::

        <resource label="obj_inst2"
                  restype="MyObject"
                  unique_id="obj_0002"
                  permissions="res-default">

    The options ar as follows:

    label : (required)
        The knora label for the resource

    restype : (required)
        The resource type as defind in th knora project specific ontology

    unique_id : (required)
        An arbitrary unique id that ist used to refrencee this this resource from another one

    permissions : (optional)
        The reference ID of a permission set

    """
    unique_id: str
    label: str
    restype: str
    permissions: str
    image: str
    properties: List[KnoraProperty]

    def __init__(self, context: etree.iterparse, node: Tuple) -> None:
        """
        Constructor that parses a resource node from the XML DOM

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing a resource)
        """
        self.unique_id = node.attrib['unique_id'] # safe the unique id
        self.label = node.attrib['label']
        self.restype = node.attrib['restype']
        self.permissions = node.attrib['permissions']
        self.image = None
        self.properties = []
        while True:
            #
            # start processing the sub nodes
            #
            event, subnode = next(context)
            if event == 'start':
                if subnode.tag == 'image':
                    self.image = node.text
                elif subnode.tag == 'text-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'text'))
                elif subnode.tag == 'color-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'color'))
                elif subnode.tag == 'date-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'date'))
                elif subnode.tag == 'decimal-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'decimal'))
                elif subnode.tag == 'geometry-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'geometry'))
                elif subnode.tag == 'geoname-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'geoname'))
                elif subnode.tag == 'list-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'list'))
                elif subnode.tag == 'iconclass-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'iconclass'))
                elif subnode.tag == 'integer-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'integer'))
                elif subnode.tag == 'interval-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'interval'))
                elif subnode.tag == 'period-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'period'))
                elif subnode.tag == 'resptr-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'resptr'))
                elif subnode.tag == 'time-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'time'))
                elif subnode.tag == 'uri-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'uri'))
                elif subnode.tag == 'boolean-prop':
                    self.properties.append(KnoraProperty(context, subnode, 'boolean'))
                else:
                    raise MyError('Unexpected start tag: "{}" <resource> may contain only <property> or <image> tags!'.format(subnode.tag))
            else:
                if subnode.tag == 'resource':
                    break
                elif subnode.tag == 'image':
                    self.image = "".join(subnode.itertext())
                else:
                    raise MyError('Unexpected end tag: "{}" </resource> expected!'.format(subnode.tag))

    def print(self):
        """
        Print Resource to stdout for debugging...

        :return: None
        """
        print('Resource: id={} restype: {} label: {}'.format(self.unique_id, self.restype, self.label))
        if self.image is not None:
            print(' Image: ' + self.image)
        for property in self.properties:
            property.print()

    def get_resptrs(self) -> List[str]:
        """
        Return a list of all reesource id's  that a referenced by this rsource
        :return: List of resources identified by their unique id's
        """
        resptrs: List[str] = []
        for property in self.properties:
            if property.type == 'resptr':
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
            vals: List[StrObj] = [] # == List[Union[str,StrDict]
            for value in property.values:
                v: str
                if property.type == 'resptr': # we have a resptr, therefore simple lookup or IRI
                    iri = resiri_lookup.get(value.value)
                    if iri is not None:
                        v = iri
                    else:
                        v = value.value # if we do not find the unique_id, we assume it's a valid knora IRI
                elif property.type == 'text': # we have a text which might have embedded references to other resources
                    if isinstance(value.value, KnoraStandoffXml):
                        irirefs = value.value.findall() # The IRI's must be embedded  as "...IRI:unique_id:IRI..."
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

                if value.comment is None  and value.permissions is None:
                    # no comment or prmissions
                    vals.append(v)
                else:
                    # we have comment or permissions
                    tmp = {'value': v}
                    if value.comment is not None:
                        tmp['comment'] = value.comment
                    if value.permissions is not None:
                        tmp['permissions'] = permissions_lookup.get(value.permissions)
                    vals.append(tmp)
            propdata[property.name] = vals if len(vals) > 1 else vals[0] # append a Union[StrObj,List[StrObj]]
        return propdata

class Allow:
    """
    Class representing a single right in a permission set definition
    """
    group: str
    permission: str

    def __init__(self, context: etree.iterparse, node: Tuple) -> None:
        """
        Constructor which parses the XML DOM allow element

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing an single right in a permission set)
        """
        self.group = node.attrib['group']
        self.permission = "".join(node.itertext())
        # UnknownUser | KnownUser | ProjectMember | Creator | ProjectAdmin | SystemAdmin


class Permission:
    """
    A class representing a permission set
    """
    id: str
    allows: List[Allow]

    def __init__(self, context: etree.iterparse, node: Tuple) -> None:
        """
        Constructor which parses a XML DOM permissions element represrenting an named permission set

        :param context: Context for DOM node traversal
        :param node: The DOM node to be processed (representing an a permission set)
        """
        self.allows = []
        self.id = node.attrib['id']
        while True:
            event, subnode = next(context)
            if event == 'start':
                if subnode.tag == 'allow':
                    self.allows.append(Allow(context, subnode))
                else:
                    raise MyError ('Unexpected tag: "{}" <allow> expected!'.format(subnode.tag))
            else:
                if subnode.tag == 'allow':
                    pass
                elif subnode.tag == 'resource':
                    break
                elif subnode.tag == 'permissions':
                    break
                else:
                    raise MyError('Unexpected end tag: "{}" </resource> expected!'.format(subnode.tag))

    def __str__(self):
        allowstrs: List[str] = []
        for allow in self.allows:
            allowstrs.append("{} {}".format(allow.permission, allow.group))
        return '|'.join(allowstrs)


def create_permission(con: Knora, permission: Permission) -> str:
    """
    This function processes a Permission ans returns a Knora compatible permission string and
    transforming/resolving all groupnames using the knora project information

    :param con: Knora instance
    :param permission: Permission instance
    :return: Knora compatible permission string with resolved group names
    """
    allowstrs: List[str] = []
    for allow in permission.allows:
        tmp = allow.group.split(':')
        if len(tmp) > 1:
            project_name = tmp[0]
            group_name = tmp[1]
            group_iri = con.get_group_by_pshortname_and_gname(project_name, group_name)
        else:
            group_iri= 'knora-admin:' + tmp[0]
        allowstrs.append("{} {}".format(allow.permission, group_iri))
    return '|'.join(allowstrs)

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
                ok_resids.append(resource.unique_id)
            else:
                ok = True
                for resptr in resptrs:
                    if resptr in ok_resids:
                        pass
                    else:
                        ok = False;
                if ok:
                    ok_resources.append(resource)
                    ok_resids.append(resource.unique_id)
                else:
                    notok_resources.append(resource)
        resources = notok_resources
        if not len(notok_resources) < notok_len:
            print('Cannot resolve resptr dependencies. Giving up....')
            print(len(notok_resources))
            for r in notok_resources:
                print('Resource {} has unresolvable resptrs to: '.format(r.unique_id), end= ' ')
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

def program(args) -> None:
    """
    This is the main program that starts everyting

    :param args:
    :return:
    """

    #
    # first we read the command line options
    #
    parser = argparse.ArgumentParser()
    parser.add_argument("inproject", help="Shortname of project the data should be added to")
    parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
    parser.add_argument("-S", "--sipi", type=str, default="http://0.0.0.0:1024", help="URL of SIPI server")
    parser.add_argument("-u", "--user", type=str, default="root@example.com", help="Username for Knora")
    parser.add_argument("-p", "--password", type=str, default="test", help="The password for login")
    parser.add_argument("-F", "--folder", default="-", help="Input folder.")
    parser.add_argument("-i", "--infile", default="-", help="Input file.")
    parser.add_argument("-a", "--assets", default="-", help="Assets folder.")
    parser.add_argument("-I", "--images", default="-", help="images folder.")
    parser.add_argument("-V", "--validate", action='store_true', help="Do only validation of JSON, no upload of the ontology")
    args = parser.parse_args(args)

    current_dir = os.path.dirname(os.path.realpath(__file__))

    #
    # prepare (create) local directories to store all information
    #
    if args.folder == '-':
        folder = args.inproject + ".dir"
    else:
        folder = args.folder

    if args.assets == '-':
        assets_path = os.path.join(folder, 'assets')
    else:
        assets_path = args.assets;

    if args.images == '-':
        images_path = os.path.join(folder, 'images')
    else:
        images_path = args.images

    if args.infile == '-':
        infile_path = os.path.join(folder, args.inproject) + '.xml'
    else:
        infile_path = args.infile

    xmlschema_doc = etree.parse(os.path.join(current_dir, 'knora-data-schema.xsd'))
    xmlschema = etree.XMLSchema(xmlschema_doc)
    doc = etree.parse(infile_path)
    xmlschema.assertValid(doc)

    del xmlschema
    del doc
    del xmlschema_doc

    print("The imput data file is syntactically correct and passed validation!")

    if args.validate:
        exit(0)

    #
    # read the XML file containing the data, including project shortcode
    #
    context: etree.iterparse = etree.iterparse(infile_path, events=("start", "end"))
    resources: List[KnoraResource] = []
    permissions: Dict[str,Permission] = {}
    while True:
        event, node = next(context)
        if event == 'start':
            if node.tag == 'knora':
                ontology = node.attrib['ontology']
                shortcode = node.attrib['shortcode']
            elif event == 'start' and node.tag == 'resource':
                resources.append(KnoraResource(context, node))
            elif event == 'start' and node.tag == 'permissions':
                permission = Permission(context, node)
                permissions[permission.id] = permission
        elif event == 'end':
            if node.tag == 'knora':
                break;

    context = None  # delete XML tree tto save memory

    #
    # sort the resources so that resources which do not likt to others come first
    #
    resources = do_sortorder(resources)

    #
    # connect to Knora
    #
    con = Knora(args.server)
    con.login(args.user, args.password)

    sipi = Sipi(args.sipi, con.get_token())

    graph = con.get_ontology_graph(shortcode, ontology)
    schema = con.create_schema(shortcode, ontology)

    permissions_lookup: StrDict = {}
    for p in permissions.items():
        permissions_lookup[p[0]] = create_permission(con, p[1])

    resiri_lookup: StrDict = {}

    # cnt: int = 0

    for resource in resources:
        if resource.image is not None:
            print('Uploading ' + resource.image + '...')
            imgres = sipi.upload_image(resource.image)
            print('Upload done: ' + imgres['uploadedFiles'][0]['internalFilename'])
            fileref = imgres['uploadedFiles'][0]['internalFilename']
            print('Uploading data...')
            resinfo = con.create_resource(schema=schema,
                                          res_class=resource.restype,
                                          label=resource.label,
                                          values=resource.get_propvals(resiri_lookup, permissions_lookup),
                                          permissions=permissions_lookup.get(resource.permissions),
                                          stillimage=fileref)
        else:
            resinfo = con.create_resource(schema=schema,
                                          res_class=resource.restype,
                                          label=resource.label,
                                          values=resource.get_propvals(resiri_lookup, permissions_lookup),
                                          permissions=permissions_lookup.get(resource.permissions))
        resiri_lookup[resource.unique_id] = resinfo['iri']


def main():
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])
