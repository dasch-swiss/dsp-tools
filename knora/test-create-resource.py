import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
from knora import KnoraError, knora, Sipi


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
parser.add_argument("-S", "--sipi", type=str, default="http://0.0.0.0:1024", help="URL of SIPI server")
parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
parser.add_argument("-p", "--password", default="test", help="The password for login")
parser.add_argument("-P", "--projectcode", required=True, help="Project short code")
parser.add_argument("-O", "--ontoname", required=True, help="Shortname of ontology")

args = parser.parse_args()


con = knora(args.server, args.user, args.password)
graph = con.get_ontology_graph('00FE', 'kpt')
#print(graph)
#exit(0)
schema = con.create_schema(args.projectcode, args.ontoname)

"""
book_info = con.create_resource(schema, 'book', 'test-buch', {
    'title': "Ein Test-Buch",
    'book_comment': ["Ein Kommentar zum Test-Buch", {'value': "EIN KOMMENTAR", 'comment': "MIT KOMMENTAR"}],
    'description': "Eine Beschreibung des Test-Buches",
    'hasAuthor': {'value': "Lukas Rosenthaler", 'comment': "Nicht bestätigt!"},
    'location': "Ort des Test-Buches",
    'note': "Eine Notiz zum Test-Buch",
    'physical_desc': "Die Beschreibung des physischen Erscheinungsbildes",
    'pubdate': "1496:CE:1499-11-02",
    'url': 'http://dhlab.unibas.ch'
})
"""

inst1_info = con.create_resource(schema, "object1", "obj1_inst1", {
    "textprop": "Dies ist ein Text!",
    "intprop": 7,
    "listprop": "options:opt2",
    "dateprop": "1966:CE:1967-05-21",
    "decimalprop": {'value': "3.14159", 'comment': "Die Zahl PI"}
})
pprint(inst1_info)
exit(0)

sipi = Sipi(args.sipi, con.get_token())
res = sipi.upload_image('test.tif')
pprint(res)
fileref = res['uploadedFiles'][0]['internalFilename']

page_info = con.create_resource(schema, 'page', 'test-page', {
    'origname': 'gaga.gaga',
    'description': "Eine Beschreibung der Test-Seite",
    'partOfValue': book_info['iri']
}, fileref)
pprint(book_info)