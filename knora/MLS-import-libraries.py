import csv
import argparse
from pprint import pprint
from knora import KnoraError, knora, BulkImport
from xml.dom.minidom import parse
import xml.dom.minidom

parser = argparse.ArgumentParser()
parser.add_argument("xmlfile", help="path to FileMaker XML Export file")
parser.add_argument("-s", "--server", type=str, default="http://0.0.0.0:3333", help="URL of the Knora server")
parser.add_argument("-u", "--user", default="root@example.com", help="Username for Knora")
parser.add_argument("-p", "--password", default="test", help="The password for login")
parser.add_argument("-P", "--projectcode", required=True, help="Project short code")
parser.add_argument("-O", "--ontoname", required=True, help="Shortname of ontology")
parser.add_argument("-x", "--xml", default="data.xml", help="Name of bulk import XML-File")
parser.add_argument("--start", default="1", help="Start with given line")
parser.add_argument("--stop", default="all", help="End with given line ('all' reads all lines")

args = parser.parse_args()

con = knora(args.server, args.user, args.password)
schema = con.create_schema(args.projectcode, args.ontoname)

bulk = BulkImport(schema)

mapping = {
    "Eindeutige_Sigle": None,
    "Land": None,
    "Stadt": None,
    "Beschreibung": "librarydescription",
    "Bibliothekssigle_ohne_Land" : "sigle",
    "Email": None,
    "Kontakadresse": None,
    "Kontakdatum": None,
    "Kontakperson": None,
    "Kontaktiert": None,
    "Kontaktnotizen": None,
    "Land_Kuerzel": None,
    "Online_Katalog": "catalogue",
    "PK_Bibl": None,
    "Telephonnr": None,
    "Web_site": "libraryweblink",
    "Zitierbare_Sigle": "None"
}

DOMTree = xml.dom.minidom.parse(args.xmlfile)
collection = DOMTree.documentElement
fields = collection.getElementsByTagName("FIELD")

valpos = []
for field in fields:
    name = field.getAttribute('NAME')
    valpos.append(name)


rows = collection.getElementsByTagName("ROW")
for row in rows:
    datas = row.getElementsByTagName("DATA")
    i = 0
    record = {}
    for data in datas:
        if data.firstChild is not None:
            if valpos[i] == "PK_Bibl":
                library_id = data.firstChild.nodeValue
            if valpos[i] == "Beschreibung":
                record["librarydescription"] = data.firstChild.nodeValue
            if valpos[i] == "Bibliothekssigle_ohne_Land":
                record["sigle"] = data.firstChild.nodeValue
            if valpos[i] == "Online_Katalog":
                record["catalogue"] = data.firstChild.nodeValue.strip("#")
            if valpos[i] == "Web_site":
                record["libraryweblink"] = data.firstChild.nodeValue.strip("#")
        i += 1

    if record.get("sigle") is None:
        record["sigle"] = "XXX"
    pprint(record)
    print("ID=" + str(library_id))
    print("=========================")
    bulk.add_resource(
        'library',
        'LIB_' + str(library_id), record["sigle"], record)

bulk.write_xml(args.xml)