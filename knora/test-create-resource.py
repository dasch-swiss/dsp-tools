import os
from typing import List, Set, Dict, Tuple, Optional
from pprint import pprint
import argparse
import json
from jsonschema import validate
from knora import KnoraError, knora


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
parser.add_argument("-p", "--password", default="test", help="The password for login")
parser.add_argument("-P", "--projectcode", required=True, help="Project short code")
parser.add_argument("-O", "--ontoname", required=True, help="Shortname of ontology")

args = parser.parse_args()


con = knora(args.server, args.user, args.password)
schema = con.create_schema(args.projectcode, args.ontoname)

res_info = con.create_resource(schema, 'book', 'test-buch', {
    'title': "Ein Test-Buch",
    'book_comment': "Ein Kommentar zum Test-Buch",
    'description': "Eine Beschreibung des Test-Buches",
    'hasAuthor': "Lukas Rosenthaler",
    'location': "Ort des Test-Buches",
    'note': "Eine Notiz zum Test-Buch",
    'physical_desc': "Die Beschreibung des physischen Erscheinungsbildes",
    'pubdate': "1496:CE:1499-11-02",
    'url': 'http://dhlab.unibas.ch'
})

pprint(res_info)
