from typing import TypeAlias
from typing import Union

from rdflib import IdentifiedNode
from rdflib import Literal
from rdflib import Namespace
from rdflib import Node
from rdflib import Variable

# rdflib typing
PropertyTypeAlias: TypeAlias = Union[IdentifiedNode, Variable]
SubjectObjectTypeAlias: TypeAlias = Union[IdentifiedNode, Literal, Variable, Node]

# Namespaces as string
KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
API_SHAPES_STR = "http://api.knora.org/ontology/knora-api/shapes/v2#"

# Namespaces
KNORA_API = Namespace(KNORA_API_STR)
API_SHAPES = Namespace(API_SHAPES_STR)
DATA = Namespace("http://data/")

DASH = Namespace("http://datashapes.org/dash#")
