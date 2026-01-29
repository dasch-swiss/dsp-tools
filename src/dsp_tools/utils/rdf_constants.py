from typing import Union

from rdflib import IdentifiedNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import Variable
from rdflib.term import Node

# naming conventions of prefixes and namespaces

# a prefix as a string is called [...]_PREFIX
# a prefix as a rdflib Namespace has no further suffix

#####
# rdflib typing
type PropertyTypeAlias = Union[IdentifiedNode, Variable]
type SubjectObjectTypeAlias = Union[IdentifiedNode, Literal, Variable, Node]

#####
# DSP-Namespaces
KNORA_API_PREFIX = "http://api.knora.org/ontology/knora-api/v2#"
KNORA_API = Namespace(KNORA_API_PREFIX)

KNORA_ADMIN_PREFIX = "http://www.knora.org/ontology/knora-admin#"

SALSAH_GUI_PREFIX = "http://api.knora.org/ontology/salsah-gui/v2#"
SALSAH_GUI = Namespace(SALSAH_GUI_PREFIX)


#####
# Mappers

DSP_NAME_TO_PREFIX = {"knora-api": KNORA_API_PREFIX, "salsah-gui": SALSAH_GUI_PREFIX}

KNORA_PROPERTIES_FOR_DIRECT_USE = [f"{KNORA_API_PREFIX}seqnum", f"{KNORA_API_PREFIX}isPartOf"]


#####
# For validate-data
API_SHAPES_PREFIX = "http://api.knora.org/ontology/knora-api/shapes/v2#"
API_SHAPES = Namespace(API_SHAPES_PREFIX)
DATA = Namespace("http://data/")
DASH_PREFIX = "http://datashapes.org/dash#"
DASH = Namespace(DASH_PREFIX)
