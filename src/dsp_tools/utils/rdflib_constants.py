from typing import Union

from rdflib import IdentifiedNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import Variable
from rdflib.term import Node

# rdflib typing
type PropertyTypeAlias = Union[IdentifiedNode, Variable]
type SubjectObjectTypeAlias = Union[IdentifiedNode, Literal, Variable, Node]

# Namespaces as string
KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
API_SHAPES_STR = "http://api.knora.org/ontology/knora-api/shapes/v2#"

# Namespaces
KNORA_API = Namespace(KNORA_API_STR)
API_SHAPES = Namespace(API_SHAPES_STR)
DATA = Namespace("http://data/")

DASH = Namespace("http://datashapes.org/dash#")
