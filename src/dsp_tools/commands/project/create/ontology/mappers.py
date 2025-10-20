from rdflib import OWL
from rdflib import Literal

from dsp_tools.commands.project.create.models.rdf_ontology import RdfCardinalityRestriction

JSON_CARDINALITY_TO_RDFLIB = {
    "1": RdfCardinalityRestriction(OWL.cardinality, Literal(1)),
    "0-1": RdfCardinalityRestriction(OWL.maxCardinality, Literal(1)),
    "1-n": RdfCardinalityRestriction(OWL.minCardinality, Literal(1)),
    "0-n": RdfCardinalityRestriction(OWL.minCardinality, Literal(0)),
}
