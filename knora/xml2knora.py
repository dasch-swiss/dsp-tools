from typing import List, Set, Dict, Tuple, Optional, Union
import os
from lxml import etree
import argparse
from pprint import pprint
import base64
import json
from knora import KnoraError, KnoraStandoffXml, Knora, Sipi
import sys
import requests
import re

# https://raw.githubusercontent.com/dhlab-basel/dasch-ark-resolver-data/master/data/shortcodes.csv

class MyError(BaseException):
    def __init__(self, msg: str):
        self.message = msg

class KnoraValue:
    resrefs: List[str]
    comment: str
    value: str
    is_richtext: bool

    def __init__(self, context: etree.iterparse, node: Tuple, type: str, listname: Optional[str] = None) -> None:
        self.resrefs = None
        self.comment = node.get('comment')
        if node.get('resrefs') is not None:
            self.resrefs = node.attrib['resrefs'].split('|')
        if node.get('encoding') == 'hex64':
            self.value = KnoraStandoffXml(
                '<?xml version="1.0" encoding="UTF-8"?>\n<text>' + \
                base64.b64decode("".join(node.itertext())).decode() + '</text>')
        else:
            if type == 'list':
                self.value = listname + ':' + "".join(node.itertext())
            else:
                self.value = "".join(node.itertext())
        while True:
            event, subnode = next(context)
            if event == 'start':
                raise MyError(
                    'Unexpected start tag: "{}" <property> may contain only <value> tags!'.format(subnode.tag))
            else:
                if subnode.tag == type:
                    break
                else:
                    raise MyError('Unexpected end tag: "{}": </{}> expected!'.format(subnode.tag, type))

    def print(self):
        print('    Value: ' + self.value)
        if self.comment:
            print('   Comment:' + self.comment)
        if self.resrefs is not None:
            for i in self.resrefs:
                print('    resref: ' + i)


class KnoraProperty:
    name: str
    type: str
    values: List[KnoraValue]

    def __init__(self, context: etree.iterparse, node: Tuple, type):
        self.name = node.attrib['name']
        listname = node.attrib.get('list')
        self.type = type
        self.values = []
        while True:
            event, subnode = next(context)
            if event == 'start':
                if subnode.tag == type:
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

    def print(self):
        print('  Property: {} Type: {}'.format(self.name, self.type))
        for value in self.values:
            value.print()


class KnoraResource:
    unique_id: str
    label: str
    restype: str
    image: str
    properties: List[KnoraProperty]

    def __init__(self, context: etree.iterparse, node: Tuple):
        self.unique_id = node.attrib['unique_id']
        self.label = node.attrib['label']
        self.restype = node.attrib['restype']
        self.image = None
        self.properties = []
        while True:
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
        print('Resource: id={} restype: {} label: {}'.format(self.unique_id, self.restype, self.label))
        if self.image is not None:
            print(' Image: ' + self.image)
        for property in self.properties:
            property.print()

    def get_resptrs(self) -> List[str]:
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

    def get_propvals(self, resiri_lookup) -> str:
        propdata = {}
        exp = re.compile(r'IRI:[^:]*:IRI')
        for property in self.properties:
            vals = []
            for value in property.values:
                v: str
                if property.type == 'resptr':
                    iri = resiri_lookup.get(value.value)
                    if iri is not None:
                        v = iri
                    else:
                        v = value.value
                elif property.type == 'text':
                    irirefs = exp.findall(value.value)
                    str = value.value
                    for iriref in irirefs:
                        resid = iriref.split(':')[1]
                        iri = resiri_lookup.get(resid)
                        str.replace(iriref, iri)
                    v = str
                else:
                    v = value.value

                if value.comment is None:
                    vals.append(v)
                else:
                    vals.append({'value': v, 'comment': value.comment})
            propdata[property.name] = vals if len(vals) > 1 else vals[0]
        return propdata

def do_sortorder(resources: List[KnoraResource]) -> List[KnoraResource]:
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
    parser = argparse.ArgumentParser()
    parser.add_argument("inproject", help="Shortname of project the data should be added to")
    parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
    parser.add_argument("-S", "--sipi", type=str, default="http://0.0.0.0:1024", help="URL of SIPI server")
    parser.add_argument("-u", "--user", type=str, default="root@example.com", help="Username for Knora")
    parser.add_argument("-p", "--password", type=str, default="test", help="The password for login")
    parser.add_argument("-F", "--folder", default="-", help="Input folder.")
    args = parser.parse_args(args)

    if args.folder == '-':
        folder = args.inproject + ".dir"
    else:
        folder = args.folder

    assets_path = os.path.join(folder, 'assets')
    images_path = os.path.join(folder, 'images')
    infile_path = os.path.join(folder, args.inproject) + '.xml'

    #
    # read the XML file containing the data, including project shortcode
    #
    context: etree.iterparse = etree.iterparse(infile_path, events=("start", "end"))
    resources: List[KnoraResource] = []
    while True:
        event, node = next(context)
        if event == 'start':
            if node.tag == 'knora':
                vocabulary = node.attrib['vocabulary']
                shortcode = node.attrib['shortcode']
            elif event == 'start' and node.tag == 'resource':
                resources.append(KnoraResource(context, node))
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

    graph = con.get_ontology_graph(shortcode, vocabulary)
    schema = con.create_schema(shortcode, vocabulary)

    resiri_lookup: Dict[str,str] = {}

    # cnt: int = 0

    for resource in resources:
        if resource.image is not None:
            print('Uploading ' + resource.image + '...')
            imgres = sipi.upload_image(resource.image)
            print('Upload done: ' + imgres['uploadedFiles'][0]['internalFilename'])
            fileref = imgres['uploadedFiles'][0]['internalFilename']
            print('Uploading data...')
            resinfo = con.create_resource(schema, resource.restype, resource.label, resource.get_propvals(resiri_lookup), fileref)
        else:
            resinfo = con.create_resource(schema, resource.restype, resource.label, resource.get_propvals(resiri_lookup))
        resiri_lookup[resource.unique_id] = resinfo['iri']


def main():
    program(sys.argv[1:])


if __name__ == '__main__':
    program(sys.argv[1:])
