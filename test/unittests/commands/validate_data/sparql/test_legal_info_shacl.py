# mypy: disable-error-code="method-assign,no-untyped-def"

from rdflib import RDF
from rdflib import SH
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.models.api_responses import EnabledLicenseIris
from dsp_tools.commands.validate_data.sparql.legal_info_shacl import construct_allowed_licenses_shape
from dsp_tools.utils.rdflib_constants import API_SHAPES
from dsp_tools.utils.rdflib_constants import KNORA_API

NUMBER_OF_TRIPLES_NO_LICENSES = 8


def test_construct_allowed_licenses_shape_one_license():
    all_licenses = EnabledLicenseIris(["http://rdfh.ch/1"])
    result = construct_allowed_licenses_shape(all_licenses)
    referenced_license_triples = 2
    assert len(result) == NUMBER_OF_TRIPLES_NO_LICENSES + referenced_license_triples
    subj = API_SHAPES.FileValue_ClassShape
    assert next(result.objects(subj, RDF.type)) == SH.NodeShape
    assert next(result.objects(subj, SH.targetClass)) == KNORA_API.FileValue
    prop_shape = next(result.objects(subj, SH.property))
    assert next(result.objects(prop_shape, RDF.type)) == SH.PropertyShape
    assert next(result.objects(prop_shape, SH.path)) == KNORA_API.hasLicense
    in_bn, license_iris = next(result.subject_objects(predicate=RDF.first))
    sh_in = URIRef("http://www.w3.org/ns/shacl#in")
    assert next(result.objects(prop_shape, sh_in)) == in_bn
    assert license_iris == URIRef("http://rdfh.ch/1")
    expected_msg = (
        "Please only use enabled licenses in your data. Consult the project information for enabled licenses."
    )
    assert next(result.objects(prop_shape, SH.message)) == Literal(expected_msg)
    assert next(result.objects(prop_shape, SH.severity)) == SH.Violation


def test_construct_allowed_licenses_shape_no_license():
    all_licenses = EnabledLicenseIris([])
    result = construct_allowed_licenses_shape(all_licenses)
    assert len(result) == NUMBER_OF_TRIPLES_NO_LICENSES
    subj = API_SHAPES.FileValue_ClassShape
    assert next(result.objects(subj, RDF.type)) == SH.NodeShape
    assert next(result.objects(subj, SH.targetClass)) == KNORA_API.FileValue
    prop_shape = next(result.objects(subj, SH.property))
    assert next(result.objects(prop_shape, RDF.type)) == SH.PropertyShape
    assert next(result.objects(prop_shape, SH.path)) == KNORA_API.hasLicense
    expected_msg = "You are only allowed to reference enabled licenses. No licenses are enabled for this project."
    assert next(result.objects(prop_shape, SH.message)) == Literal(expected_msg)
    assert next(result.objects(prop_shape, SH.severity)) == SH.Violation
