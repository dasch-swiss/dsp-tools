from rdflib import OWL
from rdflib import Literal

from dsp_tools.commands.project.create.models.ontology import CardinalityRestriction

JSON_CARDINALITY_TO_RDFLIB = {
    "1": CardinalityRestriction(OWL.cardinality, Literal(1)),
    "0-1": CardinalityRestriction(OWL.maxCardinality, Literal(1)),
    "1-n": CardinalityRestriction(OWL.minCardinality, Literal(1)),
    "0-n": CardinalityRestriction(OWL.minCardinality, Literal(0)),
}
