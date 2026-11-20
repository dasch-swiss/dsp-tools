from rdflib import OWL
from rdflib import Literal

from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.rdf_ontology import RdfCardinalityRestriction

PARSED_CARDINALITY_TO_RDF = {
    Cardinality.C_1: RdfCardinalityRestriction(OWL.cardinality, Literal(1)),
    Cardinality.C_0_1: RdfCardinalityRestriction(OWL.maxCardinality, Literal(1)),
    Cardinality.C_1_N: RdfCardinalityRestriction(OWL.minCardinality, Literal(1)),
    Cardinality.C_0_N: RdfCardinalityRestriction(OWL.minCardinality, Literal(0)),
}
