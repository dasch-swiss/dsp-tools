# mypy: disable-error-code="method-assign,no-untyped-def"

from uuid import uuid4

from rdflib import RDF
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.upload_stashed_resptr_props import _make_link_value_create_graph
from dsp_tools.utils.rdflib_constants import KNORA_API

ONTO_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#"

ONTO = Namespace(ONTO_STR)

RES_IRI_STR = "http://rdfh.ch/9999/res_one"
TARGET_IRI_STR = "http://rdfh.ch/9999/target_resource"
RES_IRI = URIRef(RES_IRI_STR)
RES_TYPE = ONTO.Resource


def test_make_link_value_create_graph():
    link_stash = LinkValueStashItem(
        res_id=RES_IRI_STR,
        res_type=RES_TYPE,
        value=ProcessedLink("target_resource_id", ONTO.hasLink, None, None, str(uuid4())),
    )
    result = _make_link_value_create_graph(link_stash, RES_IRI_STR, TARGET_IRI_STR)
    assert len(result) == 4
    res_type = next(result.objects(RES_IRI, RDF.type))
    assert res_type == RES_TYPE
    val_bn = next(result.objects(RES_IRI, ONTO.hasLinkValue))
    val_type = next(result.objects(val_bn, RDF.type))
    assert val_type == KNORA_API.LinkValue
    target_iri = next(result.objects(val_bn, KNORA_API.linkValueHasTargetIri))
    assert target_iri == URIRef(TARGET_IRI_STR)
