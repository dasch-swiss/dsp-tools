from rdflib import XSD
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

ONTO_IRI = URIRef("http://0.0.0.0:3333/ontology/9999/onto/v2")
ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
LAST_MODIFICATION_DATE = Literal("2025-10-14T13:00:00.000000Z", datatype=XSD.dateTimeStamp)
PROJECT_IRI = "http://rdfh.ch/projects/projectIRI"
SHORTNAME = "shortname"
